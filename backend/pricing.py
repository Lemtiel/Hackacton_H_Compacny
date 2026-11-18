"""Calcul du bloc « Revendre en magasin ». Notre code, sans IA.

Uniquement les prix des boutiques. Les prix eBay ne passent jamais ici (licence eBay) :
ils auront leur propre bloc, calculé à part.
"""

from __future__ import annotations

import statistics
from typing import Optional

# Part du prix de revente en boutique que le magasin offre au vendeur.
# Mesuré le 17/11 chez Easy Cash sur 7 objets (6 smartphones, 1 console), même modèle, même capacité, même état :
# médiane 59,2 % (mesures/calibrage_rachat_easycash_2026-11-17.csv, PR #18, issue #11). Remplace l'hypothèse de 40 %.
BUYBACK_COEF = 0.59


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


def shop_block(prices: list[float]) -> Optional[dict]:
    prices = [p for p in prices if p and p > 0]
    if not prices:
        return None
    kept = remove_outliers(prices)
    median = statistics.median(kept)
    return {
        "n_prices": len(prices),
        "n_kept": len(kept),
        "shop_low": round(min(kept), 2),
        "shop_high": round(max(kept), 2),
        "shop_median": round(median, 2),
        "coef": BUYBACK_COEF,
        "buyback_estimate": round(median * BUYBACK_COEF, 2),
        "buyback_low": round(min(kept) * BUYBACK_COEF, 2),
        "buyback_high": round(max(kept) * BUYBACK_COEF, 2),
    }
