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
import statistics
import time
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

# Occasion seule : 3000 (occasion), 4000 (très bon), 5000 (bon), 6000 (acceptable). Exclus : neuf (1000, 1500), « pour pièces »
# (7000) et reconditionné (2000 à 2030, 2500), vendu par des professionnels : mesuré le 18/11, il fait monter le prix conseillé
# d'un iPhone 13 de 222 à 242 € alors que le bloc parle de « vendre seul ».
USED_CONDITION_IDS = "3000|4000|5000|6000"

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


# Console : les parasites restants (jeux, pièces, manettes, casques) coûtent 10 à 135 €, les vraies consoles 300 € et plus.
# Les mots-clés ne suffisent pas (relevé du 18/11 sur « PlayStation 5 » : 7 consoles sur 29 annonces gardées). On écarte donc,
# pour les consoles seulement, ce qui coûte moins de 40 % du 3e quartile des prix gardés, quand il y a assez d'annonces.
PRICE_FLOOR_RATIO = 0.4
PRICE_FLOOR_MIN_ITEMS = 8


def drop_cheap_outliers(items: list, category: str, product: str) -> list:
    if category != "console" or len(items) < PRICE_FLOOR_MIN_ITEMS:
        return items
    if is_accessory(product):  # manette, casque : prix bas normaux
        return items
    q3 = statistics.quantiles([i.price_eur for i in items], n=4)[2]
    return [i for i in items if i.price_eur >= PRICE_FLOOR_RATIO * q3]


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


def search_category(product: str, category: str) -> str:
    """Catégorie eBay où chercher (une seule acceptée par l'API). Sans elle, « Sony PlayStation 5 » ramenait surtout
    des jeux PS5 vendus 16 à 20 € : prix conseillé de 18 € pour une console (mesure du 19/11)."""
    if category == "informatique" and "macbook" in matching.tokens(product):
        return "111422"  # Ordinateurs Apple portables
    return REFERENCE_CATEGORIES.get(category, REFERENCE_CATEGORIES["smartphone"])["id"]


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
                "category_ids": search_category(product, category),
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
    items_ok = [i for i in items if not matching.is_junk_title(product, i.title)]
    kept, n_rejected = matching.filter_offers(product, category, items_ok)
    n_rejected += len(items) - len(items_ok)
    n_before = len(kept)
    kept = drop_cheap_outliers(kept, category, product)
    n_rejected += n_before - len(kept)
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
#
# eBay rend jusqu'à 10 suggestions, et la première est souvent fausse pour nos objets (appel réel du 18/11 :
# « Téléphones mobiles: pièces » pour Redmi Note 10S, « coques » pour Galaxy S21, « pièces de rechange »
# pour MacBook Air M1). rank_categories les trie donc avec notre catégorie (notre code, sans IA).

MAX_CATEGORIES = 3

# Catégorie eBay de référence de chacune de nos catégories (identifiants relevés dans les réponses réelles
# du 18/11, arbre 71 d'EBAY_FR), et la famille eBay où chercher.
REFERENCE_CATEGORIES = {
    "smartphone": {"id": "9355", "name": "Téléphones mobiles", "path": "Téléphonie, mobilité > Téléphones mobiles"},
    "console": {"id": "139971", "name": "Consoles", "path": "Jeux vidéo, consoles > Consoles"},
    "jeu_video": {"id": "139973", "name": "Jeux", "path": "Jeux vidéo, consoles > Jeux"},
    "tablette": {"id": "171485", "name": "Tablettes, liseuses", "path": "Informatique, réseaux > Tablettes, liseuses"},
    "informatique": {"id": "177", "name": "Ordinateurs portables",
                     "path": "Informatique, réseaux > Portables, netbooks > Ordinateurs portables"},
}

# Plusieurs catégories eBay conviennent à « Informatique » : ordinateurs portables, Macs portables, Macs de bureau, PC de bureau.
# Une seule catégorie de référence mettrait « Ordinateurs portables » devant « Macs de bureau » pour un iMac (relevé du 18/11).
ACCEPTED_IDS = {"informatique": {"177", "111422", "111418", "179"}}

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


def parse_categories(payload: dict) -> list[dict]:
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
    return out


def is_accessory(product: str) -> bool:
    """L'objet est lui-même un accessoire : « Manette DualSense », « Sony DualSense », « Joy-Con », « Coque iPhone »."""
    toks = matching.tokens(product)
    return bool(toks) and (toks[0] in matching.ACCESSORY_START or any(t in matching.CONTROLLER_WORDS for t in toks))


def rank_categories(suggestions: list[dict], product: str, category: Optional[str]) -> list[dict]:
    """Trie les suggestions d'eBay pour notre objet. Rend 3 catégories au plus, la meilleure en premier.

    1. On écarte les catégories de pièces détachées et de collection : un objet en panne se publie dans sa
       catégorie normale, avec l'état « pour pièces ».
    2. On écarte les accessoires, sauf si l'objet en est un lui-même.
    3. Avec notre catégorie : on ne garde que la famille eBay de l'objet (Téléphonie, Jeux vidéo, Informatique),
       la catégorie de référence passe en premier, et elle sert de secours s'il ne reste rien.
    """
    accessory = is_accessory(product)
    ref = REFERENCE_CATEGORIES.get(category or "")
    root = ref["path"].split(" > ")[0] if ref else None
    kept = []
    for c in suggestions:
        segments = [" ".join(matching.tokens(s)) for s in c["path"].split(" > ")]
        if any("piece" in s for s in segments) or "collections" in segments:
            continue
        if not accessory and any("accessoire" in s for s in segments):
            continue
        if root and not c["path"].startswith(root + " > "):
            continue
        kept.append(c)
    if ref and not accessory:
        accepted = ACCEPTED_IDS.get(category or "", {ref["id"]})
        kept.sort(key=lambda c: c["id"] not in accepted)  # tri stable : les bonnes catégories en tête, dans l'ordre d'eBay
        if not kept:
            kept = [dict(ref)]
    return kept[:MAX_CATEGORIES]


async def suggest_category(product: str, category: Optional[str] = None,
                           client: Optional[httpx.AsyncClient] = None) -> dict:
    """Rend {state, categories}. state : ok | aucun_resultat | indisponible (sandbox).
    category : notre catégorie (smartphone, console...), pour trier les suggestions d'eBay."""
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
        categories = rank_categories(parse_categories(r.json()), product, category)
    except (httpx.HTTPError, ValueError) as e:  # ValueError : réponse qui n'est pas du JSON
        raise EbayError(type(e).__name__) from e
    finally:
        if own:
            await client.aclose()
    return {"state": "ok" if categories else "aucun_resultat", "categories": categories}
