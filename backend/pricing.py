"""Calcul du bloc « Revendre en magasin ». Notre code, sans IA.

Uniquement les prix des boutiques. Les prix eBay ne passent jamais ici (licence eBay) :
ils auront leur propre bloc, calculé à part.
"""

from __future__ import annotations

import statistics
from typing import Optional

# Part du prix de revente en boutique que le magasin offre au vendeur, par catégorie.
# Mesuré les 17 et 18/11 chez Easy Cash sur 30 objets : même modèle, même capacité, même état (« bon état »),
# coefficient = offre de rachat ÷ prix de vente, médiane par catégorie.
# Détail : docs/calibrage-rachat.md et mesures/calibrage_rachat_easycash_30_objets.csv (issue #11).
BUYBACK_COEF = 0.59  # par défaut, si la catégorie est absente ou inconnue (première mesure, 17/11)
BUYBACK_COEF_BY_CATEGORY = {
    "informatique": 0.67,  # 3 objets
    "smartphone": 0.60,  # 7 objets
    "tablette": 0.50,  # 3 objets
    "jeu_video": 0.43,  # 9 objets
}
# Les consoles se séparent selon leur prix : récentes et chères (PS5, Xbox Series X) 63 à 78 %,
# anciennes et moins chères (PS4, Switch) 38 à 47 %.
CONSOLE_PRICE_THRESHOLD = 300.0
CONSOLE_COEF_LOW = 0.44  # médiane de 5 consoles sous 300 €
CONSOLE_COEF_HIGH = 0.74  # médiane de 3 consoles à 300 € et plus


def buyback_coef(category: Optional[str], shop_median: float) -> float:
    """Coefficient de rachat pour une catégorie ; le prix médian en boutique départage les consoles."""
    if category == "console":
        return CONSOLE_COEF_HIGH if shop_median >= CONSOLE_PRICE_THRESHOLD else CONSOLE_COEF_LOW
    return BUYBACK_COEF_BY_CATEGORY.get(category or "", BUYBACK_COEF)


def remove_outliers(prices: list[float]) -> list[float]:
    """Garde les prix entre la moitié et le double de la médiane, à partir de 3 prix.

    Règle simple et robuste sur de petits échantillons : elle écarte l'accessoire à 15 €
    comme le lot à 900 €, sans dépendre des quartiles.
    """
    if len(prices) < 3:
        return list(prices)
    med = statistics.median(prices)
    kept = [p for p in prices if med / 2 <= p <= med * 2]
    return kept or list(prices)


def shop_block(prices: list[float], category: Optional[str] = None) -> Optional[dict]:
    prices = [p for p in prices if p and p > 0]
    if not prices:
        return None
    kept = remove_outliers(prices)
    median = statistics.median(kept)
    coef = buyback_coef(category, median)
    return {
        "n_prices": len(prices),
        "n_kept": len(kept),
        "shop_low": round(min(kept), 2),
        "shop_high": round(max(kept), 2),
        "shop_median": round(median, 2),
        "coef": coef,
        "buyback_estimate": round(median * coef, 2),
        "buyback_low": round(min(kept) * coef, 2),
        "buyback_high": round(max(kept) * coef, 2),
    }
