"""Sites boutiques consultés par les agents H.

Ajouter un site = ajouter une entrée ici. Aucune autre ligne de code propre au site.
Seuls les sites validés dans CONTEXT.md (cadre légal) ont leur place ici.
"""

SITES = {
    "easycash": {
        "name": "Easy Cash",
        # robots.txt interdit /search/, /catalog/, *q=*, ?sort=, ?facets=...
        # Les pages de catégorie de bons-plans.easycash.fr sont autorisées.
        "search_allowed": False,
        "start_urls": {
            "smartphone": "https://bons-plans.easycash.fr/telephonie/smartphones",
            "console": "https://bons-plans.easycash.fr/consoles",
            "jeu_video": "https://bons-plans.easycash.fr/jeux-video",
            "tablette": "https://bons-plans.easycash.fr/tablette",
            "informatique": "https://bons-plans.easycash.fr/informatique",
        },
    },
    "gamecash": {
        "name": "Gamecash",
        "search_allowed": True,
        "start_urls": {"default": "https://www.gamecash.fr/"},
    },
    "troc": {
        "name": "Troc.com",
        "search_allowed": True,
        "start_urls": {"default": "https://www.troc.com/fr"},
    },
    "cashconverters": {
        "name": "Cash Converters",
        "search_allowed": True,
        "start_urls": {"default": "https://www.cashconverters.fr/"},
    },
}

CATEGORIES = ["smartphone", "console", "jeu_video", "tablette", "informatique"]


def start_url(site_key: str, category: str) -> str:
    urls = SITES[site_key]["start_urls"]
    return urls.get(category) or urls.get("default") or next(iter(urls.values()))
