"""Bloc eBay sur une réponse simulée de l'API Browse (aucun appel réseau).

Lancer : .venv/bin/python tests/test_ebay.py
"""

import asyncio
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ["EBAY_CLIENT_ID"] = "id-de-test"
os.environ["EBAY_CLIENT_SECRET"] = "secret-de-test"
os.environ["EBAY_ENV"] = "production"

import httpx  # noqa: E402

from backend import ebay  # noqa: E402


def item(title, value, currency="EUR", seller="vendeur_42"):
    return {
        "itemId": "v1|1|0", "title": title, "price": {"value": str(value), "currency": currency},
        "condition": "Occasion", "conditionId": "3000", "itemWebUrl": "https://www.ebay.fr/itm/1",
        "seller": {"username": seller, "feedbackScore": 120},
        "image": {"imageUrl": "https://i.ebayimg.com/x.jpg"},
    }


PAYLOAD = {"total": 11, "itemSummaries": [
    item("Nintendo Switch 32 Go grise avec Joy-Con", 180),
    item("Console Nintendo Switch V2 + dock", 190),
    item("Nintendo Switch bon état", 200),
    item("Nintendo Switch complète en boîte", 210),
    item("Nintendo Switch rayée", 170),
    item("Nintendo Switch lot 15 jeux", 650),          # aberrant : retiré du calcul
    item("Nintendo Switch Lite turquoise", 120),        # autre modèle
    item("Nintendo Switch OLED blanche", 260),          # autre modèle
    item("Coque pour Nintendo Switch", 12),             # accessoire
    item("Nintendo Switch import", 150, currency="USD"),  # pas en euros
    item("Nintendo Switch", "abc"),                     # prix illisible
]}

calls = []


def handler(request: httpx.Request) -> httpx.Response:
    calls.append(request)
    if request.url.path == "/identity/v1/oauth2/token":
        assert request.headers["Authorization"].startswith("Basic ")
        return httpx.Response(200, json={"access_token": "jeton", "expires_in": 7200})
    if request.url.path == "/buy/browse/v1/item_summary/search":
        assert request.headers["Authorization"] == "Bearer jeton"
        assert request.headers["X-EBAY-C-MARKETPLACE-ID"] == "EBAY_FR"
        return httpx.Response(200, json=PAYLOAD)
    return httpx.Response(404)


async def main():
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        res = await ebay.search("Nintendo Switch", "console", client=client)
        res2 = await ebay.search("Nintendo Switch", "console", client=client)
    return res, res2


res, res2 = asyncio.run(main())
failed = 0
total = 0


def check(label, ok):
    global failed, total
    total += 1
    if not ok:
        failed += 1
    print(("OK     " if ok else "ÉCHEC  ") + label)


b = res["block"]
dump = json.dumps(res, ensure_ascii=False)
check("état ok", res["state"] == "ok")
check("9 annonces lues (USD et prix illisible jetés)", res["n_found"] == 9)
check("3 écartées par le tri (Lite, OLED, coque)", res["n_rejected"] == 3)
check("6 prix, 5 gardés (lot à 650 € retiré)", b["n_prices"] == 6 and b["n_kept"] == 5)
check("médiane affichée 190 €", b["listed_median"] == 190)
check("prix conseillé = 190 × 0,9 = 171 €", b["sell_price"] == 171)
check("fourchette dans l'ordre", b["sell_low"] <= b["sell_price"] <= b["sell_high"])
check("aucun pseudonyme vendeur dans la réponse", "vendeur_42" not in dump and "seller" not in dump)
check("aucune image dans la réponse", "ebayimg" not in dump)
check("champs gardés : titre, prix, état, lien", set(res["items"][0]) == {"title", "price_eur", "condition", "url"})
check("annonces affichées dans la fourchette", all(b["listed_low"] <= i["price_eur"] <= b["listed_high"] for i in res["items"]))
check("jeton réutilisé au 2e appel (3 requêtes, pas 4)", len(calls) == 3 and res2["state"] == "ok")
q = calls[1].url.params
check("filtre : prix fixe, euros, France, occasion", all(s in q["filter"] for s in ("FIXED_PRICE", "priceCurrency:EUR", "itemLocationCountry:FR", "3000")))
check("filtre : ni neuf, ni pièces, ni reconditionné (revendeurs professionnels)",
      not any(i in q["filter"] for i in ("1000", "1500", "7000", "2000", "2010", "2020", "2030", "2500")))
check("moins de 3 prix : pas de fourchette", ebay.ebay_block([100, 120]) is None)

# Plancher de prix des consoles : les jeux, pièces et manettes à 10-135 € ne tirent pas le prix vers le bas.
mix = [ebay.EbayItem(title=f"console {i}", price_eur=p) for i, p in enumerate([12, 15, 17, 20, 33, 94, 135, 414, 516, 618, 731, 782, 833, 925])]
kept = ebay.drop_cheap_outliers(mix, "console", "PlayStation 5")
check("console : les prix sous 40 % du 3e quartile sont écartés", min(i.price_eur for i in kept) >= 414 and len(kept) == 7)
check("console : pas assez d'annonces, rien n'est écarté", len(ebay.drop_cheap_outliers(mix[:6], "console", "PlayStation 5")) == 6)
check("smartphone : pas de plancher", len(ebay.drop_cheap_outliers(mix, "smartphone", "iPhone 13")) == len(mix))
check("manette cherchée : pas de plancher (prix bas normaux)", len(ebay.drop_cheap_outliers(mix, "console", "manette PS5 DualSense")) == len(mix))
print(f"{total - failed}/{total} vérifications correctes")
sys.exit(1 if failed else 0)
