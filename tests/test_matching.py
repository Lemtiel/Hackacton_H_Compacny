"""Cas types du tri des annonces. Lancer :  .venv/bin/python tests/test_matching.py"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.matching import reject_reason  # noqa: E402

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
print(f"{len(CASES) - failed}/{len(CASES)} cas corrects")
sys.exit(1 if failed else 0)
