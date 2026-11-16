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
]

failed = 0
for product, category, title, keep in CASES:
    reason = reject_reason(product, category, title)
    if (reason is None) != keep:
        failed += 1
        print(f"ÉCHEC  {product!r} / {title!r} : attendu {'gardée' if keep else 'écartée'}, obtenu {reason or 'gardée'}")
print(f"{len(CASES) - failed}/{len(CASES)} cas corrects")
sys.exit(1 if failed else 0)
