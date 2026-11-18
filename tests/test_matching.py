"""Cas types du tri des annonces. Lancer :  .venv/bin/python tests/test_matching.py"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from types import SimpleNamespace

from backend.matching import filter_verified_offers, is_junk_title, reject_reason  # noqa: E402

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

verified, rejected = filter_verified_offers([
    SimpleNamespace(condition="Bon état", url="https://example.com/produit/iphone-15"),
    SimpleNamespace(condition="Bon état", url="https://example.com/produit/iphone-15"),  # doublon
    SimpleNamespace(condition=None, url="https://example.com/produit/iphone-15-noir"),
    SimpleNamespace(condition="Très bon état", url="https://example.com/"),
    SimpleNamespace(condition="Correct", url="https://example.com/produit/iphone-15-vert"),
    SimpleNamespace(condition="Très bon état", url="https://example.com/produit/iphone-15-bleu"),
], "Bon état")
if len(verified) != 3 or rejected != 3:  # « Correct » et « Très bon état » sont des voisins de « Bon état » : gardés
    failed += 1
    print(f"ÉCHEC  offres vérifiables : attendu 3 gardées et 3 écartées, obtenu {len(verified)} et {rejected}")

def offer(cond, n):
    return SimpleNamespace(condition=cond, url=f"https://example.com/produit/switch-{n}")

GRADE_CASES = [
    # (état demandé, états des annonces, nombre gardé, pourquoi)
    ("Bon état", ["Bon état", "Très bon état"], 2, "voisin accepté quand il manque des offres"),
    ("Bon état", ["Bon état", "Correct", "Comme neuf"], 2, "à deux crans (Comme neuf) : refusé"),
    ("Bon état", ["Bon état", "Bon état", "Bon état", "Très bon état"], 3, "3 offres exactes : les voisines ne servent plus"),
    ("Bon état", ["Pour pièces", "Hors service"], 0, "pièces jamais mélangé avec un objet qui marche"),
    ("Pour pièces", ["Pour pièces", "Bon état"], 1, "objet à pièces : seulement des pièces"),
    ("Très bon état", ["Grade A", "Grade B", "Grade C"], 2, "libellés en grades : A et B gardés, C à deux crans écarté"),
    ("Bon état", ["Occasion reconditionné"] * 3, 3, "Gamecash : libellé sans grade, lu comme un état moyen"),
    ("Très bon état", ["Occasion reconditionné"], 1, "libellé sans grade : voisin d'un très bon état"),
    ("Comme neuf", ["Occasion reconditionné"], 0, "libellé sans grade : pas assimilé à du comme neuf"),
    ("Pour pièces", ["Occasion reconditionné"], 0, "libellé sans grade : jamais pour pièces"),
    ("Bon état", ["État standard", "Qualité B+"], 0, "libellé illisible : refusé, on ne devine pas"),
]
for target, conds, expected, why in GRADE_CASES:
    got, _ = filter_verified_offers([offer(c, i) for i, c in enumerate(conds)], target)
    if len(got) != expected:
        failed += 1
        print(f"ÉCHEC  états {target!r} / {conds} : attendu {expected} gardée(s), obtenu {len(got)} ({why})")
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
    if is_junk_title(product, title) != expected:
        failed += 1
        print(f"ÉCHEC  rebut eBay {title!r} : attendu {'rebut' if expected else 'gardée'}")
print(f"{len(CASES) + len(JUNK) + len(GRADE_CASES) + 1 - failed}/{len(CASES) + len(JUNK) + len(GRADE_CASES) + 1} cas corrects")
sys.exit(1 if failed else 0)
