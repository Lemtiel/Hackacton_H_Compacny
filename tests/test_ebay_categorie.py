"""Catégorie eBay suggérée (aide à la publication) sur une réponse simulée de l'API Taxonomy (aucun appel réseau).

Lancer : .venv/bin/python tests/test_ebay_categorie.py
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


def suggestion(cat_id, name, ancestors):
    # Ancêtres dans l'ordre rendu par eBay : du parent direct vers la racine.
    return {
        "category": {"categoryId": cat_id, "categoryName": name},
        "categoryTreeNodeAncestors": [
            {"categoryId": str(i), "categoryName": a, "categoryTreeNodeLevel": lvl, "categorySubtreeNodeHref": "https://api.ebay.com/x"}
            for i, (a, lvl) in enumerate(ancestors)
        ],
        "categoryTreeNodeLevel": len(ancestors) + 1,
        "relevancy": "interne",
    }


PAYLOAD = {"categoryTreeId": "71", "categoryTreeVersion": "999", "categorySuggestions": [
    suggestion("139971", "Consoles", [("Jeux vidéo, consoles", 1), ("Root", 0)]),
    suggestion("54968", "Accessoires", [("Jeux vidéo, consoles", 1)]),
    {"category": {"categoryName": "sans identifiant"}},  # illisible : écartée
    suggestion("139973", "Jeux vidéo", [("Jeux vidéo, consoles", 1)]),
    suggestion("1", "En trop", []),  # au-delà de 3 suggestions
]}

calls = []
mode = {"suggestions": PAYLOAD}


def handler(request: httpx.Request) -> httpx.Response:
    calls.append(request)
    if request.url.path == "/identity/v1/oauth2/token":
        return httpx.Response(200, json={"access_token": "jeton", "expires_in": 7200})
    assert request.headers["Authorization"] == "Bearer jeton"
    if request.url.path == "/commerce/taxonomy/v1/get_default_category_tree_id":
        assert request.url.params["marketplace_id"] == "EBAY_FR"
        return httpx.Response(200, json={"categoryTreeId": "71", "categoryTreeVersion": "999"})
    if request.url.path == "/commerce/taxonomy/v1/category_tree/71/get_category_suggestions":
        if mode["suggestions"] is None:
            return httpx.Response(500, text="erreur eBay")
        return httpx.Response(200, json=mode["suggestions"])
    return httpx.Response(404)


async def main():
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        res = await ebay.suggest_category("Nintendo Switch", client=client)
        res2 = await ebay.suggest_category("Nintendo Switch", client=client)
        mode["suggestions"] = {"categorySuggestions": []}
        empty = await ebay.suggest_category("objet inconnu", client=client)
        mode["suggestions"] = None
        try:
            await ebay.suggest_category("Nintendo Switch", client=client)
            error = False
        except ebay.EbayError:
            error = True
    n_calls = len(calls)
    os.environ["EBAY_ENV"] = "sandbox"
    sandbox = await ebay.suggest_category("Nintendo Switch")
    os.environ["EBAY_ENV"] = "production"
    del os.environ["EBAY_CLIENT_ID"]
    try:
        await ebay.suggest_category("Nintendo Switch")
        not_configured = False
    except ebay.EbayNotConfigured:
        not_configured = True
    return res, res2, empty, error, n_calls, sandbox, not_configured


res, res2, empty, error, n_calls, sandbox, not_configured = asyncio.run(main())
failed = 0
total = 0


def check(label, ok):
    global failed, total
    total += 1
    if not ok:
        failed += 1
    print(("OK     " if ok else "ÉCHEC  ") + label)


cats = res["categories"]
dump = json.dumps(res, ensure_ascii=False)
check("état ok", res["state"] == "ok")
check("3 suggestions au plus, l'illisible écartée", [c["id"] for c in cats] == ["139971", "54968", "139973"])
check("première suggestion : Consoles", cats[0]["name"] == "Consoles")
check("chemin de la racine vers la catégorie, sans « Root »", cats[0]["path"] == "Jeux vidéo, consoles > Consoles")
check("champs gardés : id, nom, chemin", all(set(c) == {"id", "name", "path"} for c in cats))
check("rien d'autre de la réponse eBay", "relevancy" not in dump and "Href" not in dump and "Version" not in dump)
check("question posée avec le nom de l'objet", calls[2].url.params["q"] == "Nintendo Switch")
check("jeton et arbre réutilisés au 2e appel (4 requêtes, pas 6)", res2["state"] == "ok" and sum(
    1 for c in calls[:4] if c.url.path.endswith(("oauth2/token", "get_default_category_tree_id"))) == 2)
check("aucune suggestion : aucun_resultat", empty == {"state": "aucun_resultat", "categories": []})
check("erreur eBay : EbayError (la route rend « indisponible »)", error)
check("6 requêtes pour 4 suggestions, arbre demandé une seule fois",
      sum(1 for c in calls if c.url.path.endswith("get_default_category_tree_id")) == 1 and n_calls == 6)
check("sandbox : indisponible, sans appel réseau", sandbox == {"state": "indisponible", "categories": []})
check("sans clés : EbayNotConfigured (la route rend « non_configure »)", not_configured)

print(f"{total - failed}/{total} vérifications correctes")
sys.exit(1 if failed else 0)
