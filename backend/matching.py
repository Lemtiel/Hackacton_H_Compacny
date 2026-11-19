"""Tri des annonces relevées : ne garder que le même modèle que l'objet cherché. Notre code, sans IA.

L'agent reçoit la consigne « même modèle exact », mais il ne la tient pas toujours
(test du 16/11 : 8 Switch Lite rendues pour « Nintendo Switch »). On contrôle donc les titres ici.

Une annonce est écartée si son titre :
1. ne contient pas tous les mots du modèle cherché (la marque seule est facultative) ;
2. contient un mot de déclinaison absent de la recherche (Lite, OLED, Pro, Max, Mini...) ;
3. porte un numéro juste après le nom (« Switch 2 » pour « Switch ») ;
4. désigne un accessoire (« Coque pour... », « Manette... ») ;
5. sépare le nom de son numéro (« Playstation 2 Magazine... Tekken 5 » pour « PlayStation 5 »).
Pour eBay seulement, `is_junk_title` écarte aussi pièces détachées, magazines et boîtes vides (test du 18/11 sur la PS5).
"""

from __future__ import annotations

import re
import unicodedata
from urllib.parse import urlsplit, urlunsplit

# Marques : utiles à la recherche, mais souvent absentes des titres (« iPhone 12 64 Go »).
BRANDS = {
    "apple", "samsung", "xiaomi", "nintendo", "sony", "microsoft", "google", "huawei", "honor",
    "oppo", "oneplus", "realme", "motorola", "nokia", "asus", "acer", "lenovo", "hp", "dell", "lg",
}

# Mots qui désignent un autre modèle de la même famille.
VARIANTS = {
    "lite", "oled", "pro", "max", "plus", "mini", "ultra", "slim", "fe", "se", "xl", "air",
    "note", "digital", "digitale", "fold", "flip", "neo", "edge",
    # « PS5 Portal » : lecteur à distance, pas la console (mesure du 19/11)
    "portal",
    # Éditions limitées et collector : autre référence, vendue plus cher (test DualSense du 17/11)
    "limitee", "limited", "collector", "collectors",
}

# Un titre qui commence par l'un de ces mots vend un accessoire, pas l'objet.
ACCESSORY_START = {
    "coque", "housse", "etui", "protection", "verre", "film", "sacoche", "pochette", "manette",
    "joy", "joycon", "dock", "station", "support", "chargeur", "cable", "adaptateur", "batterie",
    "ecran", "vitre", "casque", "volant", "boite", "notice", "stylet", "clavier", "telecommande",
}
GAME_START = {"jeu", "jeux"}

# Mots qui désignent une manette. Quand l'objet cherché est lui-même une manette (« Sony DualSense »,
# « Joy-Con »), un titre qui commence par « Manette » est le bon objet, pas un accessoire (test du 17/11).
CONTROLLER_WORDS = {"manette", "manettes", "controller", "joy", "joycon", "dualsense", "dualshock"}

# Équivalences tenues à la main : une annonce peut nommer l'objet autrement (« Manette PS5 » pour une
# DualSense, « PS5 » pour une PlayStation 5). Si les mots du modèle contiennent la clé, l'une des
# variantes suffit à leur place. Les autres règles (déclinaisons, accessoires) s'appliquent ensuite.
ALIASES: list[tuple[tuple[str, ...], list[tuple[str, ...]]]] = [
    (("dualsense",), [("manette", "ps5"), ("manette", "playstation", "5")]),
    (("dualshock", "4"), [("manette", "ps4"), ("manette", "playstation", "4")]),
    (("playstation", "5"), [("ps5",)]),
    (("playstation", "4"), [("ps4",)]),
    (("joy", "con"), [("joycon",)]),
]

UNITS = {"go", "to", "mo", "pouces", "pouce"}

# Annonces qui ne vendent pas l'objet : pièces, magazines, boîtes vides. Relevé sur eBay le 18/11 pour « PlayStation 5 » :
# 58 % des annonces gardées étaient de ce type (médiane 78,70 € pour une console à ~300 €). Appliqué aux annonces eBay
# seulement : les boutiques ont leur propre rubrique « pour pièces » que l'utilisateur peut chercher.
JUNK_WORDS = {
    "piece", "pieces", "detache", "detachee", "detachees", "capot", "plasturgie", "epave", "hs",
    "magazine", "magazines", "vide", "pegi", "reparation", "alimentation", "button", "bouton", "eject",
}
JUNK_PHRASES = ("inner box", "pour pieces", "boite seule", "boitier seul")


def is_junk_title(product: str, title: str) -> bool:
    """Vrai si le titre vend des pièces, un magazine ou une boîte vide, sauf si la recherche le demande."""
    have = tokens(title)
    wanted = set(tokens(product))
    text = " ".join(have)
    return any(w in have and w not in wanted for w in JUNK_WORDS) or any(p in text and p not in " ".join(tokens(product)) for p in JUNK_PHRASES)
STOP = {"de", "du", "la", "le", "les", "des", "et", "avec", "en", "a", "d", "l"}


def tokens(text: str) -> list[str]:
    text = unicodedata.normalize("NFKD", text.lower())
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r"(\d)\s*(gb|go)\b", r"\1 go", text)
    text = re.sub(r"(\d)\s*(tb|to)\b", r"\1 to", text)
    # « iPad (9e génération) », « 9ème gen », « 9th generation » : la génération devient le numéro seul (mesure du 19/11).
    text = re.sub(r"\b(\d{1,2})\s*(e|eme|th|nd|rd|st)\s*(generation|gen)\b", r"\1", text)
    # « The Legend of Zelda : … » et « Zelda … » désignent le même jeu (mesure du 19/11).
    text = re.sub(r"\bthe\s+legend\s+of\s+zelda\b", "zelda", text)
    return re.findall(r"[a-z0-9]+", text)


def required_tokens(product: str) -> list[str]:
    toks = [t for t in tokens(product) if t not in STOP]
    model = [t for t in toks if t not in BRANDS]
    return model or toks


def reject_reason(product: str, category: str, title: str) -> str | None:
    """Rend None si le titre correspond à l'objet cherché, sinon la raison de l'écart."""
    need = required_tokens(product)
    have = tokens(title)
    if not need or not have:
        return "titre vide"

    if not _has_model(need, have):
        return "autre modèle"

    wanted = set(tokens(product))
    if any(t in VARIANTS and t not in wanted for t in have):
        return "autre modèle"

    if not _numbers_stick(need, have):
        return "autre modèle"

    # « Nintendo Switch 2 » pour « Nintendo Switch » : un petit nombre collé au nom, sans unité.
    if not need[-1].isdigit() and need[-1] in have:
        i = have.index(need[-1])
        nxt = have[i + 1] if i + 1 < len(have) else ""
        after = have[i + 2] if i + 2 < len(have) else ""
        if nxt.isdigit() and int(nxt) <= 20 and after not in UNITS:
            return "autre modèle"

    starts = ACCESSORY_START if category == "jeu_video" else ACCESSORY_START | GAME_START
    if wanted & CONTROLLER_WORDS:
        # Manette cherchée : « Manette ... pour PS5 » est le bon objet ; « Coque pour manette » ou
        # « Station de charge pour DualSense » restent des accessoires (premier mot).
        if have[0] in starts and have[0] not in wanted and have[0] not in CONTROLLER_WORDS:
            return "accessoire"
        return None
    if (have[0] in starts and have[0] not in wanted) or ("pour" in have and "pour" not in wanted):
        return "accessoire"
    return None


def _numbers_stick(need: list[str], have: list[str]) -> bool:
    """Un petit numéro du modèle (« 5 » de « PlayStation 5 ») doit suivre son mot dans le titre, sauf équivalence (« PS5 »).
    Une année glissée entre les deux (« iPad 2021 9e gen ») ne compte pas."""
    have = [t for t in have if not (len(t) == 4 and t.isdigit() and t.startswith(("19", "20")))] or have
    for i, n in enumerate(need):
        if i == 0 or not n.isdigit() or int(n) > 20 or need[i - 1].isdigit() or need[i - 1] in UNITS:
            continue
        word = need[i - 1]
        if any(a == word and b == n for a, b in zip(have, have[1:])):
            continue
        if any(all(k in need for k in key) and any(all(t in have for t in alt) for alt in alts) for key, alts in ALIASES):
            continue
        return False
    return True


def _has_model(need: list[str], have: list[str]) -> bool:
    """Tous les mots du modèle sont dans le titre, directement ou par une équivalence connue."""
    have_set = set(have)
    if all(t in have_set for t in need):
        return True
    for key, alts in ALIASES:
        if all(k in need for k in key):
            rest = [t for t in need if t not in key]
            for alt in alts:
                if all(t in have_set for t in rest) and all(t in have_set for t in alt):
                    return True
    return False


def filter_offers(product: str, category: str, offers: list) -> tuple[list, int]:
    """Sépare les annonces gardées du nombre d'annonces écartées."""
    kept = [o for o in offers if reject_reason(product, category, o.title) is None]
    return kept, len(offers) - len(kept)


# Les cinq états de l'interface, du pire au meilleur. L'écart de rang mesure la distance entre deux états.
GRADE_ORDER = ["pieces", "correct", "bon", "tres_bon", "comme_neuf"]

# Libellés des boutiques, ramenés aux cinq états. Ordre important : les libellés les plus longs d'abord
# (« tres bon » avant « bon », « etat correct » avant « correct »). Chaque boutique note à sa façon :
#   Certideal : Correct, Très bon état, Parfait état, Premium (note d'agent du 18/11)
#   Swappie   : Bon état, Très bon état, Parfait état, Premium (note d'agent du 18/11)
#   Gamecash  : n'affiche pas « Bon état » (issue #23) ; l'annonce sans état reste possible, voir rank_by_condition
# Un libellé inconnu rend None : l'offre est gardée en dernier recours, jamais au même rang qu'un état identique.
GRADE_LABELS = [
    ("pieces", ("pour pieces", "hors service", "non fonctionnel", "en panne", "hs")),
    ("comme_neuf", ("comme neuf", "parfait etat", "etat parfait", "premium", "grade s", "a+", "neuf")),
    ("tres_bon", ("tres bon etat", "tres bon", "excellent etat", "excellent", "grade a")),
    ("correct", ("etat correct", "correct", "acceptable", "satisfaisant", "etat moyen", "use", "grade c")),
    ("bon", ("bon etat", "bon", "grade b")),
]

# En dessous de ce nombre d'offres au même état, on complète avec les états voisins (règle des Specs : 3 prix par site).
MIN_SAME_CONDITION = 3


def condition_grade(text: str) -> str | None:
    """Ramène les libellés usuels des boutiques aux cinq états de l'interface. None si le libellé est inconnu."""
    value = " " + " ".join(tokens(text.replace("+", " plus "))) + " "
    value = value.replace(" a plus ", " a+ ")
    for grade, labels in GRADE_LABELS:
        if any(f" {label} " in value for label in labels):
            return grade
    return None


def _verifiable_url(url: str) -> str | None:
    """Adresse canonique d'une fiche produit, ou None si ce n'est pas une fiche (accueil, vide, autre protocole)."""
    try:
        parsed = urlsplit(url)
    except ValueError:
        return None
    if parsed.scheme not in ("http", "https") or not parsed.netloc or parsed.path in ("", "/"):
        return None
    return urlunsplit((parsed.scheme.lower(), parsed.netloc.lower(), parsed.path.rstrip("/"), parsed.query, ""))


def rank_by_condition(offers: list, target_condition: str | None = None,
                      minimum: int = MIN_SAME_CONDITION) -> tuple[list[tuple[object, str]], int]:
    """Classe les offres par proximité d'état au lieu d'exclure tout ce qui n'a pas exactement l'état demandé.

    Rend ([(offre, correspondance)], nombre d'écartées), correspondance valant :
      « exact »  : même état que celui demandé ;
      « proche » : un cran au-dessus ou en dessous, ajouté seulement s'il manque des offres au même état ;
      « inconnu » : boutique qui n'affiche pas d'état (ou libellé inconnu), en dernier recours.
    Toujours écartées : offre sans fiche produit vérifiable, doublon, « pour pièces » (sauf si c'est l'état demandé),
    état à deux crans ou plus. Sans état demandé, toutes les offres vérifiables sont « exact ».
    """
    target = condition_grade(target_condition or "") if target_condition else None
    tiers: dict[str, list] = {"exact": [], "proche": [], "inconnu": []}
    seen: set[str] = set()
    rejected = 0
    for offer in offers:
        canonical = _verifiable_url(str(getattr(offer, "url", "") or "").strip())
        if canonical is None or canonical in seen:
            rejected += 1
            continue
        seen.add(canonical)
        grade = condition_grade(str(getattr(offer, "condition", "") or ""))
        if target is None:
            tier = "exact"
        elif grade is None:
            tier = "inconnu"
        elif grade == target:
            tier = "exact"
        elif "pieces" in (grade, target):
            tier = None  # une console en panne ne se compare ni à une console qui marche, ni l'inverse
        elif abs(GRADE_ORDER.index(grade) - GRADE_ORDER.index(target)) == 1:
            tier = "proche"
        else:
            tier = None
        if tier is None:
            rejected += 1
        else:
            tiers[tier].append(offer)

    kept = [(o, "exact") for o in tiers["exact"]]
    for tier in ("proche", "inconnu"):
        if len(kept) >= minimum:
            rejected += len(tiers[tier])
        else:
            kept += [(o, tier) for o in tiers[tier]]
    return kept, rejected


def filter_verified_offers(offers: list, target_condition: str | None = None) -> tuple[list, int]:
    """Offres vérifiables et uniques, classées par proximité d'état (voir rank_by_condition)."""
    kept, rejected = rank_by_condition(offers, target_condition)
    return [o for o, _ in kept], rejected
