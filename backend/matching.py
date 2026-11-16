"""Tri des annonces relevées : ne garder que le même modèle que l'objet cherché. Notre code, sans IA.

L'agent reçoit la consigne « même modèle exact », mais il ne la tient pas toujours
(test du 16/11 : 8 Switch Lite rendues pour « Nintendo Switch »). On contrôle donc les titres ici.

Une annonce est écartée si son titre :
1. ne contient pas tous les mots du modèle cherché (la marque seule est facultative) ;
2. contient un mot de déclinaison absent de la recherche (Lite, OLED, Pro, Max, Mini...) ;
3. porte un numéro juste après le nom (« Switch 2 » pour « Switch ») ;
4. désigne un accessoire (« Coque pour... », « Manette... »).
"""

from __future__ import annotations

import re
import unicodedata

# Marques : utiles à la recherche, mais souvent absentes des titres (« iPhone 12 64 Go »).
BRANDS = {
    "apple", "samsung", "xiaomi", "nintendo", "sony", "microsoft", "google", "huawei", "honor",
    "oppo", "oneplus", "realme", "motorola", "nokia", "asus", "acer", "lenovo", "hp", "dell", "lg",
}

# Mots qui désignent un autre modèle de la même famille.
VARIANTS = {
    "lite", "oled", "pro", "max", "plus", "mini", "ultra", "slim", "fe", "se", "xl", "air",
    "note", "digital", "digitale", "fold", "flip", "neo", "edge",
}

# Un titre qui commence par l'un de ces mots vend un accessoire, pas l'objet.
ACCESSORY_START = {
    "coque", "housse", "etui", "protection", "verre", "film", "sacoche", "pochette", "manette",
    "joy", "joycon", "dock", "station", "support", "chargeur", "cable", "adaptateur", "batterie",
    "ecran", "vitre", "casque", "volant", "boite", "notice", "stylet", "clavier", "telecommande",
}
GAME_START = {"jeu", "jeux"}

UNITS = {"go", "to", "mo", "pouces", "pouce"}
STOP = {"de", "du", "la", "le", "les", "des", "et", "avec", "en", "a", "d", "l"}


def tokens(text: str) -> list[str]:
    text = unicodedata.normalize("NFKD", text.lower())
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r"(\d)\s*(gb|go)\b", r"\1 go", text)
    text = re.sub(r"(\d)\s*(tb|to)\b", r"\1 to", text)
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

    missing = [t for t in need if t not in have]
    if missing:
        return "autre modèle"

    wanted = set(tokens(product))
    if any(t in VARIANTS and t not in wanted for t in have):
        return "autre modèle"

    # « Nintendo Switch 2 » pour « Nintendo Switch » : un petit nombre collé au nom, sans unité.
    if not need[-1].isdigit():
        i = have.index(need[-1])
        nxt = have[i + 1] if i + 1 < len(have) else ""
        after = have[i + 2] if i + 2 < len(have) else ""
        if nxt.isdigit() and int(nxt) <= 20 and after not in UNITS:
            return "autre modèle"

    starts = ACCESSORY_START if category == "jeu_video" else ACCESSORY_START | GAME_START
    if (have[0] in starts and have[0] not in wanted) or ("pour" in have and "pour" not in wanted):
        return "accessoire"
    return None


def filter_offers(product: str, category: str, offers: list) -> tuple[list, int]:
    """Sépare les annonces gardées du nombre d'annonces écartées."""
    kept = [o for o in offers if reject_reason(product, category, o.title) is None]
    return kept, len(offers) - len(kept)
