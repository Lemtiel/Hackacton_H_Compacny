"""Catégorie eBay suggérée (aide à la publication), sans appel réseau :
- tri des suggestions sur 12 réponses réelles de l'API Taxonomy (tests/ebay_categories_reelles.json, 18/11) ;
- appels simulés : jeton et arbre réutilisés, erreurs, sandbox, sans clés.

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
    suggestion("171833", "Pièces de rechange, outils", [("Jeux vidéo, consoles", 1)]),  # pièces : écartée
    suggestion("139973", "Jeux", [("Jeux vidéo, consoles", 1)]),
    suggestion("139971", "Consoles", [("Jeux vidéo, consoles", 1), ("Root", 0)]),  # référence de « console »
    {"category": {"categoryName": "sans identifiant"}},  # illisible : écartée
    suggestion("182179", "Supports, fixations", [("Accessoires", 2), ("Jeux vidéo, consoles", 1)]),  # accessoire
    suggestion("182175", "Boîtes de jeu originales", [("Jeux vidéo, consoles", 1)]),
    suggestion("260000", "Lots mixtes", [("Jeux vidéo, consoles", 1)]),  # au-delà de 3 suggestions
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
        res = await ebay.suggest_category("Nintendo Switch", "console", client=client)
        res2 = await ebay.suggest_category("Nintendo Switch", "console", client=client)
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
check("pièces, accessoire et illisible écartés, référence en tête, 3 au plus",
      [c["id"] for c in cats] == ["139971", "139973", "182175"])
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

# --- Tri sur les réponses réelles d'eBay (18/11) ---
REAL = json.loads((Path(__file__).resolve().parent / "ebay_categories_reelles.json").read_text(encoding="utf-8"))
for case in REAL["cas"]:
    ranked = ebay.rank_categories(case["suggestions"], case["objet"], case["categorie"])
    got = ranked[0]["path"] if ranked else "rien"
    check(f"réel, {case['objet']} ({case['categorie']}) : {got}", bool(ranked) and ranked[0]["id"] == case["attendu"])
    check(f"réel, {case['objet']} : ni pièces ni collection proposées",
          not any("pièces" in c["path"].lower() or c["path"].startswith("Collections") for c in ranked))

by_name = {c["objet"]: c for c in REAL["cas"]}
redmi = by_name["Redmi Note 10S"]["suggestions"]
check("eBay brut se trompait sur Redmi (1re suggestion : pièces)", "pièces" in redmi[0]["path"])
check("Redmi sans « Téléphones mobiles » dans les suggestions : catégorie de référence en secours",
      [c["id"] for c in ebay.rank_categories(redmi[:3], "Redmi Note 10S", "smartphone")] == ["9355"])
check("accessoire sans suggestion utilisable : rien (pas de secours « Consoles »)",
      ebay.rank_categories(redmi[:3], "Manette DualSense", "console") == [])
check("sans notre catégorie : pièces et accessoires écartés, ordre d'eBay gardé",
      [c["id"] for c in ebay.rank_categories(by_name["MacBook Air M1"]["suggestions"], "MacBook Air M1", None)][:2]
      == ["177", "111422"])
check("objet accessoire : « Joy-Con », « Sony DualSense », « Coque iPhone »",
      all(ebay.is_accessory(p) for p in ("Joy-Con Nintendo", "Sony DualSense", "Coque iPhone 13")))
check("objet non accessoire : « Nintendo Switch », « iPhone 13 », « Zelda »",
      not any(ebay.is_accessory(p) for p in ("Nintendo Switch", "iPhone 13", "Zelda Breath of the Wild")))

print(f"{total - failed}/{total} vérifications correctes")
sys.exit(1 if failed else 0)
