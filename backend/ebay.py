"""Bloc « Vendre seul (eBay) ». API Browse officielle d'eBay, notre code, sans IA.

Règles (CLAUDE.md, règles 4 et 5) :
- les prix eBay restent dans ce bloc : ils ne passent ni dans pricing.shop_block, ni dans un modèle de texte ;
- on ne garde que le titre, le prix, l'état et le lien. Le pseudonyme du vendeur et le reste de la réponse
  sont jetés dès la lecture ;
- rien n'est conservé : ni cache des résultats, ni journal des annonces. Seul le jeton OAuth reste en mémoire.

Limite connue : l'API Browse rend les annonces EN COURS, donc des prix demandés et non des prix de vente.
D'où la décote appliquée à la médiane.

Aide à la publication (suggest_category) : catégorie eBay suggérée par l'API Taxonomy, avec le même jeton
applicatif. Aucun compte utilisateur : c'est l'utilisateur qui publie son annonce sur eBay.
"""

from __future__ import annotations

import asyncio
import base64
import os
import re
import statistics
import time
import unicodedata
from dataclasses import asdict, dataclass
from typing import Optional

import httpx

from backend import matching
from backend.pricing import remove_outliers  # fonction de calcul seule : aucun prix eBay n'entre dans shop_block

# HYPOTHÈSE des Specs (décote eBay autour de 10 %) : les annonces en cours affichent un prix demandé,
# un peu au-dessus du prix de vente réel. À recalibrer avec le jeu de 30 objets (prix vendus relevés à la main).
SELL_DISCOUNT = float(os.getenv("EBAY_SELL_DISCOUNT", "0.10"))

MIN_PRICES = 3        # en dessous, pas de fourchette : trop peu d'annonces pour un prix fiable
MAX_ITEMS_SHOWN = 10  # annonces affichées avec leur lien
TIMEOUT_S = 10.0

# Occasion et reconditionné. Exclus : neuf (1000, 1500) et « pour pièces » (7000).
USED_CONDITION_IDS = "2000|2010|2020|2030|2500|3000|4000|5000|6000"

HOSTS = {"production": "https://api.ebay.com", "sandbox": "https://api.sandbox.ebay.com"}
SCOPE = "https://api.ebay.com/oauth/api_scope"


class EbayNotConfigured(Exception):
    pass


class EbayError(Exception):
    pass


@dataclass
class EbayItem:
    title: str
    price_eur: float
    condition: Optional[str] = None
    url: Optional[str] = None


def _host() -> str:
    return HOSTS.get(os.getenv("EBAY_ENV", "production"), HOSTS["production"])


def configured() -> bool:
    return bool(os.getenv("EBAY_CLIENT_ID") and os.getenv("EBAY_CLIENT_SECRET"))


# --- Jeton OAuth (client credentials), gardé en mémoire jusqu'à 5 min avant son expiration ---

_token: Optional[str] = None
_token_exp = 0.0
_token_lock = asyncio.Lock()


async def _get_token(client: httpx.AsyncClient) -> str:
    global _token, _token_exp
    async with _token_lock:
        if _token and time.time() < _token_exp:
            return _token
        cid, secret = os.getenv("EBAY_CLIENT_ID"), os.getenv("EBAY_CLIENT_SECRET")
        if not (cid and secret):
            raise EbayNotConfigured()
        basic = base64.b64encode(f"{cid}:{secret}".encode()).decode()
        r = await client.post(
            f"{_host()}/identity/v1/oauth2/token",
            headers={"Authorization": f"Basic {basic}", "Content-Type": "application/x-www-form-urlencoded"},
            data={"grant_type": "client_credentials", "scope": SCOPE},
        )
        if r.status_code != 200:
            raise EbayError(f"jeton refusé ({r.status_code})")
        body = r.json()
        _token = body["access_token"]
        _token_exp = time.time() + int(body.get("expires_in", 7200)) - 300
        return _token


# --- Lecture de la réponse : on ne garde que 4 champs ---

def parse_items(payload: dict) -> list[EbayItem]:
    items = []
    for it in payload.get("itemSummaries") or []:
        price = it.get("price") or {}
        if price.get("currency") != "EUR":
            continue
        try:
            value = float(price.get("value"))
        except (TypeError, ValueError):
            continue
        if value <= 0 or not it.get("title"):
            continue
        items.append(EbayItem(title=it["title"], price_eur=value, condition=it.get("condition"), url=it.get("itemWebUrl")))
    return items


def ebay_block(prices: list[float]) -> Optional[dict]:
    """Fourchette = quartiles des prix gardés (min et max sous 4 prix), prix conseillé = médiane moins la décote."""
    prices = [p for p in prices if p > 0]
    if len(prices) < MIN_PRICES:
        return None
    kept = sorted(remove_outliers(prices))
    median = statistics.median(kept)
    if len(kept) >= 4:
        q1, _, q3 = statistics.quantiles(kept, n=4, method="inclusive")
    else:
        q1, q3 = kept[0], kept[-1]
    k = 1 - SELL_DISCOUNT
    return {
        "n_prices": len(prices),
        "n_kept": len(kept),
        "listed_low": round(q1, 2),
        "listed_high": round(q3, 2),
        "listed_median": round(median, 2),
        "discount": SELL_DISCOUNT,
        "sell_low": round(q1 * k),
        "sell_high": round(q3 * k),
        "sell_price": round(median * k),
    }


async def search(product: str, category: str, client: Optional[httpx.AsyncClient] = None) -> dict:
    """Rend {state, block, items, n_found, n_rejected, duration_s}. state : ok | aucun_resultat."""
    if not configured():
        raise EbayNotConfigured()
    t0 = time.monotonic()
    own = client is None
    client = client or httpx.AsyncClient(timeout=TIMEOUT_S)
    try:
        token = await _get_token(client)
        r = await client.get(
            f"{_host()}/buy/browse/v1/item_summary/search",
            headers={"Authorization": f"Bearer {token}", "X-EBAY-C-MARKETPLACE-ID": "EBAY_FR"},
            params={
                "q": product,
                "limit": "100",
                "filter": f"buyingOptions:{{FIXED_PRICE}},priceCurrency:EUR,itemLocationCountry:FR,"
                          f"conditionIds:{{{USED_CONDITION_IDS}}}",
            },
        )
        if r.status_code != 200:
            raise EbayError(f"recherche refusée ({r.status_code})")
        items = parse_items(r.json())
    except httpx.HTTPError as e:
        raise EbayError(type(e).__name__) from e
    finally:
        if own:
            await client.aclose()

    # Même tri par modèle que pour les boutiques (Switch Lite écartée pour « Nintendo Switch », accessoires...).
    kept, n_rejected = matching.filter_offers(product, category, items)
    block = ebay_block([i.price_eur for i in kept])
    shown = sorted(kept, key=lambda i: i.price_eur)
    if block:  # on montre les annonces dans la fourchette, pas les extrêmes écartés du calcul
        lo, hi = block["listed_low"], block["listed_high"]
        shown = [i for i in shown if lo <= i.price_eur <= hi] or shown
    return {
        "state": "ok" if block else "aucun_resultat",
        "block": block,
        "items": [asdict(i) for i in shown[:MAX_ITEMS_SHOWN]],
        "n_found": len(items),
        "n_rejected": n_rejected,
        "duration_s": round(time.monotonic() - t0, 2),
    }


# --- Aide à la publication : catégorie eBay suggérée (API Taxonomy) ---
# Même jeton applicatif que la recherche (scope api_scope) : aucun compte utilisateur, c'est lui qui publie.
# On ne garde que l'identifiant, le nom et le chemin de la catégorie. Seul l'identifiant de l'arbre des catégories
# d'EBAY_FR reste en mémoire (une donnée de configuration, pas une annonce).
# Limite eBay : get_category_suggestions n'existe pas en sandbox.

MAX_CATEGORIES = 3

_tree_id: Optional[str] = None


async def _category_tree_id(client: httpx.AsyncClient, token: str) -> str:
    global _tree_id
    if _tree_id:
        return _tree_id
    r = await client.get(
        f"{_host()}/commerce/taxonomy/v1/get_default_category_tree_id",
        headers={"Authorization": f"Bearer {token}"},
        params={"marketplace_id": "EBAY_FR"},
    )
    if r.status_code != 200:
        raise EbayError(f"arbre des catégories refusé ({r.status_code})")
    tree = r.json().get("categoryTreeId")
    if not tree:
        raise EbayError("arbre des catégories absent")
    _tree_id = str(tree)
    return _tree_id


def parse_categories(payload: dict, limit: int = MAX_CATEGORIES) -> list[dict]:
    """Rend [{id, name, path}], dans l'ordre d'eBay. path va de la racine à la catégorie : « Jeux vidéo > Consoles »."""
    out = []
    for s in payload.get("categorySuggestions") or []:
        cat = s.get("category") or {}
        if not (cat.get("categoryId") and cat.get("categoryName")):
            continue
        ancestors = sorted(
            (a for a in s.get("categoryTreeNodeAncestors") or [] if a.get("categoryName") and a.get("categoryTreeNodeLevel", 1) >= 1),
            key=lambda a: a.get("categoryTreeNodeLevel", 0),
        )
        path = [a["categoryName"] for a in ancestors] + [cat["categoryName"]]
        out.append({"id": str(cat["categoryId"]), "name": cat["categoryName"], "path": " > ".join(path)})
        if len(out) == limit:
            break
    return out


# --- Choix de la catégorie : l'ordre d'eBay ne suffit pas ---
# Relevé du 18/11 sur l'API réelle : « iPhone 13 » → coques en 1er ; « Xbox Series S » → jeux avant consoles ; « iPad Air »
# → tablettes en 4e ; « Galaxy Tab S8 » → aucune catégorie de tablette. On garde donc, par catégorie de l'app, la ou les
# catégories eBay.fr qui conviennent (identifiants relevés le 18/11 dans l'arbre EBAY_FR), et on écarte pièces et accessoires.
RAW_SUGGESTIONS = 12  # on lit plus de suggestions qu'on n'en rend, pour retrouver la bonne
TARGET_IDS = {
    "smartphone": {"9355"},
    "console": {"139971"},
    "jeu_video": {"139973"},
    "tablette": {"171485"},
    "informatique": {"177", "111422", "111418", "179"},  # portables, Macs portables, Macs de bureau, PC de bureau
}
ROOTS = {
    "smartphone": "Téléphonie, mobilité", "console": "Jeux vidéo, consoles", "jeu_video": "Jeux vidéo, consoles",
    "tablette": "Informatique, réseaux", "informatique": "Informatique, réseaux",
}
# Quand eBay ne propose pas la bonne catégorie, on la donne nous-mêmes (une seule bonne réponse possible).
DEFAULT_CATEGORY = {
    "smartphone": {"id": "9355", "name": "Téléphones mobiles", "path": "Téléphonie, mobilité > Téléphones mobiles"},
    "console": {"id": "139971", "name": "Consoles", "path": "Jeux vidéo, consoles > Consoles"},
    "jeu_video": {"id": "139973", "name": "Jeux", "path": "Jeux vidéo, consoles > Jeux"},
    "tablette": {"id": "171485", "name": "Tablettes, liseuses", "path": "Informatique, réseaux > Tablettes, liseuses"},
}
# Un accessoire (manette, casque) se range dans « Accessoires » : là, l'ordre d'eBay reste bon.
ACCESSORY_WORDS = {"manette", "manettes", "controller", "joy", "joycon", "dualsense", "dualshock", "casque", "casques", "headset"}


def _norm(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", text.lower()) if not unicodedata.combining(c))


def pick_categories(cats: list[dict], category: Optional[str], product: str) -> list[dict]:
    """Garde les catégories eBay qui correspondent à la catégorie de l'app. Sans catégorie connue : ordre d'eBay."""
    if category not in TARGET_IDS:
        return cats[:MAX_CATEGORIES]
    accessory = bool(set(re.findall(r"[a-z0-9]+", _norm(product))) & ACCESSORY_WORDS)
    targets = set() if accessory else TARGET_IDS[category]

    def bad(c: dict) -> bool:
        n = _norm(c["path"])
        return ("piece" in n or "lots mixtes" in n or _norm(c["name"]) == "autres" or (not accessory and "accessoire" in n))

    first = [c for c in cats if c["id"] in targets]
    rest = [c for c in cats if c["id"] not in targets and c["path"].startswith(ROOTS[category]) and not bad(c)]
    if not first and not accessory and category in DEFAULT_CATEGORY:
        first = [DEFAULT_CATEGORY[category]]
    return (first + rest)[:MAX_CATEGORIES] or cats[:MAX_CATEGORIES]


async def suggest_category(product: str, category: Optional[str] = None, client: Optional[httpx.AsyncClient] = None) -> dict:
    """Rend {state, categories}. state : ok | aucun_resultat | indisponible (sandbox). category : celle de l'app (smartphone…)."""
    if not configured():
        raise EbayNotConfigured()
    if _host() == HOSTS["sandbox"]:
        return {"state": "indisponible", "categories": []}
    own = client is None
    client = client or httpx.AsyncClient(timeout=TIMEOUT_S)
    try:
        token = await _get_token(client)
        tree = await _category_tree_id(client, token)
        r = await client.get(
            f"{_host()}/commerce/taxonomy/v1/category_tree/{tree}/get_category_suggestions",
            headers={"Authorization": f"Bearer {token}"},
            params={"q": product},
        )
        if r.status_code != 200:
            raise EbayError(f"suggestion de catégorie refusée ({r.status_code})")
        categories = pick_categories(parse_categories(r.json(), RAW_SUGGESTIONS), category, product)
    except (httpx.HTTPError, ValueError) as e:  # ValueError : réponse qui n'est pas du JSON
        raise EbayError(type(e).__name__) from e
    finally:
        if own:
            await client.aclose()
    return {"state": "ok" if categories else "aucun_resultat", "categories": categories}
