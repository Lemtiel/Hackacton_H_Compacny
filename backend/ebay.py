"""Bloc « Vendre seul (eBay) ». API Browse officielle d'eBay, notre code, sans IA.

Règles (CLAUDE.md, règles 4 et 5) :
- les prix eBay restent dans ce bloc : ils ne passent ni dans pricing.shop_block, ni dans un modèle de texte ;
- on ne garde que le titre, le prix, l'état et le lien. Le pseudonyme du vendeur et le reste de la réponse
  sont jetés dès la lecture ;
- rien n'est conservé : ni cache des résultats, ni journal des annonces. Seul le jeton OAuth reste en mémoire.

Limite connue : l'API Browse rend les annonces EN COURS, donc des prix demandés et non des prix de vente.
D'où la décote appliquée à la médiane.
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
