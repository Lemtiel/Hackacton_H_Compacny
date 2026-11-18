"""Cas types du tri des annonces. Lancer :  .venv/bin/python tests/test_matching.py"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from types import SimpleNamespace

from backend.matching import condition_grade, filter_verified_offers, is_junk_title, rank_by_condition, reject_reason  # noqa: E402

CASES = [
    # (objet cherché, catégorie, titre de l'annonce, gardée ?)
    ("Nintendo Switch", "console", "Console Nintendo Switch 32 Go néon", True),
    ("Nintendo Switch", "console", "Switch V2 grise avec 2 Joy-Con", True),
    ("Nintendo Switch", "console", "Pack Nintendo Switch + Mario Kart 8", True),
    ("Nintendo Switch", "console", "Nintendo Switch Lite turquoise", False),
    ("Nintendo Switch", "console", "Console Nintendo Switch OLED blanche", False),
    ("Nintendo Switch", "console", "Nintendo Switch 2", False),
    ("Nintendo Switch", "console", "Manette Pro Nintendo Switch", False),
    ("Nintendo Switch", "console", "Housse de transport pour Switch", False),
    ("Nintendo Switch", "console", "Jeu Switch Zelda Breath of the Wild", False),
    ("Nintendo Switch OLED", "console", "Console Nintendo Switch OLED blanche", True),
    ("Nintendo Switch OLED", "console", "Nintendo Switch 32 Go", False),
    ("Apple iPhone 12", "smartphone", "iPhone 12 64Go noir", True),
    ("Apple iPhone 12", "smartphone", "APPLE IPHONE 12 128 GB", True),
    ("Apple iPhone 12", "smartphone", "iPhone 12 Pro 128 Go", False),
    ("Apple iPhone 12", "smartphone", "iPhone 12 mini 64 Go", False),
    ("Apple iPhone 12", "smartphone", "iPhone 13 128 Go", False),
    ("Apple iPhone 12", "smartphone", "Coque iPhone 12 silicone", False),
    # Le numéro du modèle doit suivre son nom : « Tekken 5 » sur une annonce PlayStation 2 n'est pas une PS5.
    ("PlayStation 5", "console", "Playstation 2 Magazine [n°99 J/A 2005] PS2 Black God of War Tekken 5", False),
    ("PlayStation 5", "console", "Sony PlayStation 5 console 825GB CFI-1016A", True),
    ("PlayStation 5", "console", "Sony PS5 Blu-Ray Edition Console - Blanc", True),
    ("PlayStation 5", "console", "Console Sony Playstation 5 1 To", True),
    ("PlayStation 5", "console", "Console Sony Playstation 5 Slim 1 To", False),  # Slim = déclinaison, autre modèle (règle existante)
    ("Apple iPhone 12", "smartphone", "iPhone 12 128 Go reconditionné", True),
    ("Google Pixel 7", "smartphone", "Pixel 7 128 Go Obsidian", True),
    ("Google Pixel 7", "smartphone", "Pixel 6 Pro 7 jours en boutique", False),
    ("Apple iPhone 12 64 Go", "smartphone", "iPhone 12 64GB bleu", True),
    ("Apple iPhone 12 64 Go", "smartphone", "iPhone 12 128 Go bleu", False),
    ("Xiaomi Redmi Note 10S", "smartphone", "Xiaomi Redmi Note 10S 128 Go", True),
    ("Xiaomi Redmi Note 10S", "smartphone", "Redmi Note 10 Pro", False),
    ("Sony PlayStation 4", "console", "PlayStation 4 500 Go + manette", True),
    ("Sony PlayStation 4", "console", "PlayStation 4 Pro 1 To", False),
    ("Sony PlayStation 4", "console", "PlayStation 4 Slim 500 Go", False),
    ("Zelda Breath of the Wild", "jeu_video", "Jeu Zelda Breath of the Wild Switch", True),
    # Manette cherchée (test réel du 17/11 : les manettes étaient écartées comme « accessoire »)
    ("Sony DualSense", "console", "Manette PS5 DualSense blanche", True),
    ("Sony DualSense", "console", "Manette Sony DualSense PS5", True),
    ("Sony DualSense", "console", "Manette sans fil DualSense pour PS5", True),
    ("Sony DualSense", "console", "Manette Playstation 5 Dualsense", True),
    ("Sony DualSense", "console", "Sony DualSense Midnight Black", True),
    ("Sony DualSense", "console", "DualSense Edge", False),
    ("Sony DualSense", "console", "Manette sans fil Sony DualSense Édition limitée God of War", False),
    ("Nintendo Switch OLED", "console", "Nintendo Switch OLED édition collector Zelda", False),
    ("Sony DualSense", "console", "Coque silicone pour manette DualSense", False),
    ("Sony DualSense", "console", "Station de charge pour DualSense", False),
    ("Sony DualSense", "console", "Chargeur manette DualSense", False),
    ("Nintendo Joy-Con", "console", "Manette Joy-Con gauche et droite Nintendo Switch", True),
    ("Nintendo Joy-Con", "console", "Joy-Con Nintendo Switch néon", True),
    # Équivalences (17/11) : l'annonce nomme l'objet autrement
    ("Sony DualSense", "console", "Manette PS5 sans fil blanche", True),
    ("Sony DualSense", "console", "Manette PlayStation 5 Midnight Black", True),
    ("Sony DualSense", "console", "Coque manette PS5", False),
    ("Sony DualSense", "console", "Chargeur double manette PS5", False),
    ("Sony DualSense", "console", "Manette PS4 sans fil", False),
    ("Sony DualSense", "console", "Volant PS5 Logitech", False),
    ("Sony DualShock 4", "console", "Manette PS4 noire V2", True),
    ("Sony PlayStation 5", "console", "Console PS5 825 Go lecteur", True),
    ("Sony PlayStation 5", "console", "Console PS5 Slim", False),
    ("Sony PlayStation 5", "console", "PS5 Digital Edition", False),
    ("Sony PlayStation 5", "console", "Manette PS5 DualSense", False),
    ("Sony PlayStation 4", "console", "PS4 500 Go noire", True),
    ("Nintendo Joy-Con", "console", "Paire de Joycon Nintendo Switch", True),
    # Console cherchée : la manette reste un accessoire
    ("Sony PlayStation 5", "console", "Manette DualSense pour PlayStation 5", False),
]

failed = 0
for product, category, title, keep in CASES:
    reason = reject_reason(product, category, title)
    if (reason is None) != keep:
        failed += 1
        print(f"ÉCHEC  {product!r} / {title!r} : attendu {'gardée' if keep else 'écartée'}, obtenu {reason or 'gardée'}")

def offer(condition, slug):
    return SimpleNamespace(condition=condition, url=f"https://example.com/produit/{slug}" if slug else "https://example.com/")


checks = 0


def check(label, got, expected):
    global failed, checks
    checks += 1
    if got != expected:
        failed += 1
        print(f"ÉCHEC  {label} : attendu {expected!r}, obtenu {got!r}")


# Libellés des boutiques ramenés aux cinq états (Certideal, Swappie : notes d'agent du 18/11)
for label, grade in [
    ("Bon état", "bon"), ("Très bon état", "tres_bon"), ("Très bon", "tres_bon"), ("Excellent", "tres_bon"),
    ("Correct", "correct"), ("État correct", "correct"), ("Parfait état", "comme_neuf"), ("Premium", "comme_neuf"),
    ("Comme neuf", "comme_neuf"), ("Grade B", "bon"), ("Grade A", "tres_bon"), ("Pour pièces", "pieces"),
    ("Occasion", None), ("", None),
]:
    check(f"libellé {label!r}", condition_grade(label), grade)

# Issue #23 : assez d'offres au même état -> les autres états sont écartés, comme avant
ranked, rejected = rank_by_condition([
    offer("Bon état", "a"), offer("Bon état", "b"), offer("Grade B", "c"),
    offer("Très bon état", "d"), offer(None, "e"),
], "Bon état")
check("3 offres au même état", [m for _, m in ranked], ["exact", "exact", "exact"])
check("3 offres au même état, écartées", rejected, 2)

# Issue #23 : une seule offre au même état -> on complète avec les états voisins, puis les offres sans état
ranked, rejected = rank_by_condition([
    offer("Bon état", "a"),
    offer("Très bon état", "b"),       # voisin au-dessus
    offer("Correct", "c"),             # voisin en dessous
    offer("Premium", "d"),             # deux crans au-dessus : écartée
    offer("Pour pièces", "e"),         # jamais comparable à un objet qui marche
    offer(None, "f"),                  # boutique sans état affiché
    offer("Bon état", "a"),            # doublon
    offer("Bon état", None),           # pas de fiche produit
], "Bon état")
check("complément par états voisins", [m for _, m in ranked], ["exact", "proche", "proche"])
check("complément par états voisins, écartées", rejected, 5)

# Gamecash (18/11) : aucun état affiché -> les offres restent, marquées « inconnu », au lieu de 0 prix
ranked, rejected = rank_by_condition([offer(None, "a"), offer("", "b"), offer("Occasion", "c")], "Bon état")
check("boutique sans état", [m for _, m in ranked], ["inconnu", "inconnu", "inconnu"])
check("boutique sans état, écartées", rejected, 0)

# Objet « pour pièces » : seules les offres pour pièces comptent
ranked, rejected = rank_by_condition([offer("Pour pièces", "a"), offer("État correct", "b")], "Pour pièces")
check("pour pièces", [m for _, m in ranked], ["exact"])

# Compatibilité : filter_verified_offers rend les offres seules
verified, rejected = filter_verified_offers([offer("Bon état", "a"), offer("Correct", "b")], "Bon état")
check("filter_verified_offers", (len(verified), rejected), (2, 0))


# Rebuts propres à eBay : pièces, magazines, boîtes vides (relevé du 18/11 sur « PlayStation 5 »).
JUNK = [
    ("PlayStation 5", "PIECES DÉTACHÉES PARTS CONSOLE SONY PS5 PLAYSTATION 5", True),
    ("PlayStation 5", "PLAYSTATION 5 - PS5 BOITE vide uniquement - inner box - (CFI-1216A)", True),
    ("PlayStation 5", "Sony PS5 réparation HDMI", True),
    ("PlayStation 5", "POWER EJECT BUTTON EDS-020 SONY PS5 PLAYSTATION 5 CFI-1116A", True),
    ("PlayStation 5", "Playstation PS2 Magazine n°99 Tekken 5", True),
    ("PlayStation 5", "EA SPORTS FC 25 Football Sony PlayStation 5 PS5 PAL PEGI 3", True),
    ("PlayStation 5", "Sony PlayStation 5 console 825GB CFI-1016A | FW 2.00", False),
    ("PlayStation 5", "Sony PS5 Standard Edition 845Go + SSD 1To", False),
    ("Nintendo Switch", "Nintendo Switch pour pièces, ne s'allume plus", True),
    ("Nintendo Switch pour pièces", "Nintendo Switch pour pièces, ne s'allume plus", False),  # si l'utilisateur le cherche, on le garde
]
for product, title, expected in JUNK:
    check(f"rebut eBay : {title[:45]}", is_junk_title(product, title), expected)

total = len(CASES) + checks
print(f"{total - failed}/{total} cas corrects")
sys.exit(1 if failed else 0)
