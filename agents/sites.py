"""Sites boutiques consultés par les agents H.

Ajouter un site = ajouter une entrée ici. Aucune autre ligne de code propre au site.
Seuls les sites validés dans CONTEXT.md (cadre légal) ont leur place ici.

Page de départ (mesure du 19/11 : partir de l'accueil coûtait l'essentiel des 90 s) :
- « search_url » : la page de résultats du site, au format de son propre formulaire, quand robots.txt l'autorise ;
- « model_pages » : pages de catégorie par modèle, relevées dans les menus du site le 19/11 ; la plus proche du nom
  de l'objet est choisie par correspondance de mots (pick_model_page), sinon la catégorie générale.
"""

import re
from urllib.parse import quote_plus

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
        "model_pages": {
            "smartphone": [f"https://bons-plans.easycash.fr/telephonie/smartphones/{p}" for p in (
                "apple", "samsung", "google", "xiaomi-reconditionne", "oneplus", "oppo", "huawei",
                "apple/iphone-11", "apple/iphone-11-pro-reconditionne", "apple/iphone-11-pro-max-reconditionne",
                "apple/iphone-12-reconditionne", "apple/iphone-12-iphone-12-mini-reconditionne",
                "apple/iphone-12-pro-12-pro-max-reconditionne", "apple/iphone-12-pro-max-reconditionne",
                "apple/iphone-13-reconditionne", "apple/iphone-13-mini-reconditionne", "apple/iphone-13-pro-reconditionne",
                "apple/iphone-13-pro-max-reconditionne", "apple/iphone-14-reconditionne", "apple/iphone-14-plus-reconditionne",
                "apple/iphone-14-pro-reconditionne", "apple/iphone-14-pro-max-reconditionne", "apple/iphone-15-reconditionne",
                "apple/iphone-15-plus-reconditionne", "apple/iphone-15-pro-reconditionne", "apple/iphone-15-pro-max-reconditionne",
                "apple/iphone-16-reconditionne", "apple/iphone-16-plus-reconditionne", "apple/iphone-16-pro-reconditionne",
                "apple/iphone-16-pro-max-reconditionne", "apple/iphone-16e-reconditionne", "apple/iphone-se-2020",
                "apple/iphone-se-2022", "apple/iphone-xr-reconditionne", "apple/iphone-xs-reconditionne",
                "samsung/galaxy-s20-s20-5g", "samsung/galaxy-s20-ultra", "samsung/galaxy-s21-5g-s21-5g-plus-s21-5g-ultra",
                "samsung/galaxy-s21-plus", "samsung/galaxy-s21-ultra", "samsung/galaxy-s22", "samsung/galaxy-s22-plus",
                "samsung/galaxy-s22-ultra", "samsung/galaxy-s23-reconditionne", "samsung/galaxy-s23-plus-reconditionne",
                "samsung/galaxy-s23-ultra-reconditionne", "samsung/galaxy-s24-reconditionne",
                "samsung/galaxy-s24-plus-reconditionne", "samsung/galaxy-s24-ultra-reconditionne",
                "samsung/galaxy-s25-reconditionne", "samsung/galaxy-s25-ultra-reconditionne",
                "samsung/galaxy-a52-reconditionne", "samsung/galaxy-a53-reconditionne",
            )],
            "console": [f"https://bons-plans.easycash.fr/consoles/{p}" for p in (
                "nintendo/switch", "nintendo/switch-oled", "nintendo/switch-lite", "nintendo/switch-2",
                "sony/ps4", "sony/ps4-slim", "sony/ps4-pro", "sony/ps5", "sony/ps5-slim", "sony/ps5-pro",
                "microsoft/xbox-one", "microsoft/xbox-one-s", "microsoft/xbox-one-x",
                "microsoft/xbox-series-s", "microsoft/xbox-series-x",
            )],
            "jeu_video": [f"https://bons-plans.easycash.fr/jeux-video/{p}" for p in (
                "nintendo/switch", "nintendo/switch-2", "sony/ps4", "sony/ps5",
                "microsoft/xbox-one", "microsoft/xbox-series-x",
            )],
            "tablette": [f"https://bons-plans.easycash.fr/tablette/{p}" for p in (
                "apple", "samsung", "apple/ipad-air", "apple/ipad-mini", "apple/ipad-pro",
            )],
            "informatique": [f"https://bons-plans.easycash.fr/informatique/ordinateur-portable/{p}" for p in (
                "macbook", "macbook/macbook-air-occasion-reconditionne", "macbook/macbook-pro-occasion-reconditionne",
            )],
        },
    },
    "gamecash": {
        "name": "Gamecash",
        "search_allowed": True,
        # robots.txt vide ; formulaire du site : /recherche.html?h=1&searchTxt=…
        "search_url": "https://www.gamecash.fr/recherche.html?h=1&searchTxt={q}",
        "sells": ["console", "jeu_video"],  # pas de téléphones (test du 16/11)
        "start_urls": {"default": "https://www.gamecash.fr/"},
    },
    "cashconverters": {
        "name": "Cash Converters",
        "search_allowed": True,
        # robots.txt n'interdit que /admin/ ; formulaire du site : /p/search?q=…
        "search_url": "https://www.cashconverters.fr/p/search?q={q}",
        "sells": ["smartphone", "console", "jeu_video", "tablette", "informatique"],
        "start_urls": {"default": "https://www.cashconverters.fr/"},
    },
    # Ajoutés le 17/11 après lecture du robots.txt et des CGU (JOURNAL.md, « sources de prix élargies »).
    "certideal": {
        "name": "Certideal",
        # robots.txt interdit search_query, controller=search, /recherche, ?orderby, ?n= :
        # navigation par les pages de catégorie seulement. CGU : aucune clause contre l'accès automatisé.
        "search_allowed": False,
        "sells": ["smartphone", "tablette", "informatique"],
        "start_urls": {
            "smartphone": "https://certideal.com/",
            "tablette": "https://certideal.com/ipad-reconditionnes-118",
            "informatique": "https://certideal.com/macbook-142",
        },
        "model_pages": {
            "smartphone": [f"https://certideal.com/{p}" for p in (
                "iphone-reconditionnes-82", "samsung-reconditionnes-90",
                "iphone-11-reconditionnes-213", "iphone-11-pro-reconditionnes-245", "iphone-11-pro-max-reconditionnes-248",
                "iphone-12-reconditionne-261", "iphone-12-mini-reconditionnes-264", "iphone-12-pro-reconditionne-266",
                "iphone-12-pro-max-reconditionne-276", "iphone-13-reconditionne-288", "iphone-13-mini-reconditionne-289",
                "iphone-13-pro-reconditionne-301", "iphone-13-pro-max-reconditionne-302", "iphone-14-312",
                "iphone-14-plus-386", "iphone-14-pro-410", "iphone-14-pro-max-326", "iphone-15-reconditionne-372",
                "iphone-15-plus-415", "iphone-15-pro-416", "iphone-15-pro-max-409", "iphone-16-545", "iphone-16-plus-546",
                "iphone-16-pro-544", "iphone-16-pro-max-543", "iphone-16e-578", "iphone-se-2-2020-249",
                "iphone-se-3-2022-392", "iphone-xr-reconditionnes-205", "iphone-xs-reconditionnes-207",
                "samsung-galaxy-s21-391", "samsung-galaxy-s21-fe-468", "samsung-galaxy-s21-plus-403",
                "samsung-galaxy-s21-ultra-549", "samsung-galaxy-s22-405", "samsung-galaxy-s22-plus-466",
                "samsung-galaxy-s22-ultra-467", "samsung-galaxy-s23-465", "samsung-galaxy-s23-fe-457",
                "samsung-galaxy-s23-ultra-464", "samsung-galaxy-s24-455", "samsung-galaxy-s24-ultra-671",
                "samsung-galaxy-a53-470", "samsung-galaxy-a54-462", "samsung-galaxy-a55-469",
            )],
            "tablette": [f"https://certideal.com/{p}" for p in (
                "ipad-349", "ipad-air-348", "ipad-mini-350", "ipad-pro-347",
            )],
            "informatique": [f"https://certideal.com/{p}" for p in (
                "macbook-air-148", "macbook-pro-149",
            )],
        },
    },
    "swappie": {
        "name": "Swappie",
        # robots.txt interdit les filtres (?grades=, ?minPrice=, ?sorting=...) : pas de filtres ni de tri.
        # CGU : aucune clause contre l'accès automatisé. Derrière Cloudflare : sort de la liste si l'agent est bloqué.
        "search_allowed": False,
        "sells": ["smartphone", "tablette"],
        # Swappie ne vend que des iPhone et des iPad (constaté par l'agent le 19/11 sur un Galaxy S21).
        "only_if_words": ["iphone", "ipad"],
        "start_urls": {"default": "https://swappie.com/fr/"},
    },
}

# En pause depuis le 19/11 : 0 prix sur 10 objets (sa recherche répond « aucun produit » à chaque essai), alors que
# l'offre H gratuite ne laisse que 3 agents à la fois. Remettre l'entrée dans SITES pour le réactiver.
PAUSED_SITES = {
    "troc": {
        "name": "Troc.com",
        "search_allowed": True,
        # robots.txt n'interdit que /ajax/ ; formulaire du site : /fr/resultats-recherche?search-text=…
        "search_url": "https://www.troc.com/fr/resultats-recherche?search-text={q}",
        "sells": ["smartphone", "console", "jeu_video", "tablette", "informatique"],
        "start_urls": {"default": "https://www.troc.com/fr"},
    },
}

CATEGORIES = ["smartphone", "console", "jeu_video", "tablette", "informatique"]


# Mots d'une adresse qui ne désignent pas un modèle.
NEUTRAL = {
    "reconditionne", "reconditionnes", "reconditionnee", "occasion", "pas", "cher", "series", "5g", "fr",
    "consoles", "console", "telephonie", "smartphones", "tablette", "informatique", "jeux", "video",
    "ordinateur", "portable", "https", "www", "com", "bons", "plans", "easycash", "certideal",
}
_ALIASES = [(("playstation", "5"), "ps5"), (("playstation", "4"), "ps4")]


def _words(text: str) -> list[str]:
    from backend.matching import tokens  # même découpage que le tri des annonces

    return tokens(text)


def _product_words(product: str) -> set[str]:
    words = set(_words(product))
    for key, alias in _ALIASES:
        if all(k in words for k in key):
            words.add(alias)
    return words


def _segments(slug: list[str]) -> list[list[str]]:
    """« iphone-12-iphone-12-mini » couvre deux modèles : un segment par modèle, coupé au premier mot répété."""
    segs, cur = [], []
    for t in slug:
        if t in cur:
            segs.append(cur)
            cur = []
        cur.append(t)
    return segs + [cur]


def pick_model_page(pages: list[str], product: str) -> str | None:
    """Page de catégorie la plus proche de l'objet, ou None. Une page n'est retenue que si l'un de ses segments
    ne contient que des mots de l'objet, une marque ou un mot neutre : « iphone-13-pro » ne sert jamais pour
    « iPhone 13 ». Score : mots de l'objet retrouvés (une marque compte pour moitié)."""
    from backend.matching import BRANDS

    want = _product_words(product)
    best, best_score = None, 0.0
    for url in pages:
        path = re.sub(r"^https?://[^/]+/", "", url)
        slug = [t for t in _words(path.replace("/", " ").replace("-", " "))]
        if slug and slug[-1].isdigit() and len(slug[-1]) >= 3:  # identifiant de catégorie (« -288 »)
            slug = slug[:-1]
        for seg in _segments(slug):
            if any(t not in want and t not in NEUTRAL and t not in BRANDS for t in seg):
                continue
            score = sum(0.5 if t in BRANDS else 1.0 for t in set(seg) if t in want)
            if score > best_score:
                best, best_score = url, score
    return best


def start_url(site_key: str, category: str, product: str | None = None) -> str:
    """Page où l'agent commence : résultats de recherche, page du modèle, sinon catégorie générale."""
    site = SITES[site_key]
    if product and site.get("search_url"):
        # La capacité (« 128 Go ») vide souvent les résultats : l'agent la vérifie ensuite sur chaque fiche.
        q = re.sub(r"\b\d+\s*(go|gb|to|tb)\b", " ", product, flags=re.I)
        return site["search_url"].format(q=quote_plus(" ".join(q.split())))
    if product:
        page = pick_model_page(site.get("model_pages", {}).get(category, []), product)
        if page:
            return page
    urls = site["start_urls"]
    return urls.get(category) or urls.get("default") or next(iter(urls.values()))


def sites_for(category: str, product: str | None = None) -> list[str]:
    """Sites qui vendent ce type d'objet (et cette marque, pour Swappie). Les autres ne lancent pas d'agent."""
    words = set(_words(product)) if product else None
    return [k for k, v in SITES.items() if category in v["sells"]
            and (words is None or not v.get("only_if_words") or words & set(v["only_if_words"]))]
