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
        "sells": ["smartphone", "console", "jeu_video", "tablette", "informatique"],
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
        "sells": ["console", "jeu_video"],  # pas de téléphones (test du 16/11)
        "start_urls": {"default": "https://www.gamecash.fr/"},
    },
    "troc": {
        "name": "Troc.com",
        "search_allowed": True,
        "sells": ["smartphone", "console", "jeu_video", "tablette", "informatique"],
        "start_urls": {"default": "https://www.troc.com/fr"},
    },
    "cashconverters": {
        "name": "Cash Converters",
        "search_allowed": True,
        "sells": ["smartphone", "console", "jeu_video", "tablette", "informatique"],
        "start_urls": {"default": "https://www.cashconverters.fr/"},
    },
}

CATEGORIES = ["smartphone", "console", "jeu_video", "tablette", "informatique"]


def start_url(site_key: str, category: str) -> str:
    urls = SITES[site_key]["start_urls"]
    return urls.get(category) or urls.get("default") or next(iter(urls.values()))


def sites_for(category: str) -> list[str]:
    """Sites qui vendent ce type d'objet. Les autres affichent « aucun résultat » sans lancer d'agent."""
    return [k for k, v in SITES.items() if category in v["sells"]]
