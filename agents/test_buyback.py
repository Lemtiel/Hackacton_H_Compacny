"""Test de l'agent de rachat Easy Cash (issue #11).

Exemples :
  .venv/bin/python -m agents.test_buyback --all
  .venv/bin/python -m agents.test_buyback --product "Apple iPhone 13 128 Go" --category smartphone

--all lance les 11 objets de référence : les 7 relevés à la main le 17/11
(mesures/calibrage_rachat_easycash_2026-11-17.csv) servent de bonne réponse, les 4 autres
testent les autres catégories et le cas « cotation manuelle ».

Chaque run ajoute une ligne à mesures/buyback_runs.csv : seulement des chiffres et l'offre
d'Easy Cash, aucune annonce de particulier.
Coût : une session H par objet (environ 0,03 €), soit environ 0,35 € pour --all.
"""

from __future__ import annotations

import argparse
import csv
import statistics
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from hai_agents import Client

from agents.buyback_agent import AGENT, START_URLS, BuybackResult, run_buyback

ROOT = Path(__file__).resolve().parent.parent
LOG = ROOT / "mesures" / "buyback_runs.csv"
FIELDS = [
    "date_utc", "product", "category", "condition", "agent", "status", "answer_status",
    "offer_eur", "expected_eur", "ecart_pct", "correct", "duration_s", "steps",
    "input_tokens", "cached_tokens", "output_tokens", "forced_answer", "cancelled",
    "session_id", "note",
]

# (produit, catégorie, détails, offre relevée à la main le 17/11 en « Bon état », ou None)
REFERENCE = [
    ("Apple iPhone 11 Noir 64 Go", "smartphone", "Noir, 64 Go", 76.00),
    ("Apple iPhone 12 Noir 64 Go", "smartphone", "Noir, 64 Go", 116.00),
    ("Apple iPhone 13 Minuit 128 Go", "smartphone", "Minuit, 128 Go", 155.00),
    ("Apple iPhone 13 mini Minuit 256 Go", "smartphone", "Minuit, 256 Go", 164.00),
    ("Apple iPhone 14 Minuit 128 Go", "smartphone", "Minuit, 128 Go", 208.00),
    ("Apple iPhone 15 Noir 128 Go", "smartphone", "Noir, 128 Go", 265.00),
    ("Nintendo Switch OLED Noir 64 Go + 2 Joy-Con Blanc", "console", "OLED, 64 Go, Joy-Con blancs", 94.00),
    # Sans bonne réponse : on regarde si l'agent trouve une offre ou repère la cotation manuelle.
    ("Apple iPhone 18 Pro Noir 1 To", "smartphone", "Noir, 1000 Go", None),  # attendu : manual
    ("Apple iPad 9e génération 64 Go Wi-Fi", "tablette", "64 Go, Wi-Fi", None),
    ("Apple MacBook Air M1 8 Go 256 Go", "informatique", "13 pouces, 8 Go RAM, 256 Go SSD", None),
    ("The Legend of Zelda: Breath of the Wild (Nintendo Switch)", "jeu_video", "jeu Switch", None),
]

# Une offre compte comme juste si elle est à 5 % ou 5 € près de la valeur relevée à la main
# (les prix Easy Cash bougent d'un jour à l'autre).
TOLERANCE_PCT = 5.0
TOLERANCE_EUR = 5.0

_print_lock = threading.Lock()


def log(msg: str) -> None:
    with _print_lock:
        print(msg, flush=True)


def check(r: BuybackResult, expected: Optional[float]) -> tuple[Optional[float], Optional[bool]]:
    """Rend (écart en %, juste ?) par rapport à la valeur relevée à la main, si elle existe."""
    if expected is None or not r.has_offer:
        return None, (False if expected is not None else None)
    ecart = round((r.offer_eur - expected) / expected * 100, 1)
    ok = abs(r.offer_eur - expected) <= max(TOLERANCE_EUR, expected * TOLERANCE_PCT / 100)
    return ecart, ok


def append_log(r: BuybackResult, condition: str, expected: Optional[float]) -> None:
    ecart, ok = check(r, expected)
    LOG.parent.mkdir(exist_ok=True)
    new = not LOG.exists()
    with LOG.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new:
            w.writeheader()
        w.writerow({
            "date_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "product": r.product, "category": r.category, "condition": condition, "agent": AGENT,
            "status": r.status, "answer_status": r.answer_status, "offer_eur": r.offer_eur,
            "expected_eur": expected, "ecart_pct": ecart, "correct": ok,
            "duration_s": r.duration_s, "steps": r.steps, "input_tokens": r.input_tokens,
            "cached_tokens": r.cached_tokens, "output_tokens": r.output_tokens,
            "forced_answer": r.forced_answer, "cancelled": r.cancelled,
            "session_id": r.session_id, "note": (r.note or "")[:200],
        })


def report(r: BuybackResult, expected: Optional[float]) -> None:
    ecart, ok = check(r, expected)
    offer = f"{r.offer_eur:.2f} €" if r.offer_eur else "-"
    line = f"\n=== {r.product} : {r.answer_status or r.status}  offre {offer}"
    if expected is not None:
        line += f"  (relevé main {expected:.2f} €, écart {ecart if ecart is not None else '-'} %, {'OK' if ok else 'KO'})"
    line += f"\n    {r.duration_s}s, {r.steps} étapes, {r.input_tokens + r.output_tokens} tokens"
    if r.note:
        line += f"\n    note : {r.note}"
    if r.agent_view_url:
        line += f"\n    Agent View : {r.agent_view_url}"
    log(line)


def summary(rows: list[tuple[BuybackResult, Optional[float]]]) -> None:
    n = len(rows)
    by = lambda s: sum(1 for r, _ in rows if r.answer_status == s)
    with_truth = [(r, e) for r, e in rows if e is not None]
    correct = sum(1 for r, e in with_truth if check(r, e)[1])
    durations = [r.duration_s for r, _ in rows if r.duration_s]
    tokens = [r.input_tokens + r.output_tokens for r, _ in rows if r.input_tokens]
    log("\n================ RÉSUMÉ ================")
    log(f"Objets testés           : {n}")
    log(f"Offre trouvée           : {by('offer')}")
    log(f"Cotation manuelle       : {by('manual')}")
    log(f"Modèle introuvable      : {by('not_found')}")
    log(f"Bloqué (anti-robot)     : {by('blocked')}")
    log(f"Sans réponse / annulé   : {sum(1 for r, _ in rows if r.answer_status is None or r.cancelled)}")
    if with_truth:
        log(f"Justes vs relevé main   : {correct}/{len(with_truth)} (tolérance {TOLERANCE_PCT:.0f} % ou {TOLERANCE_EUR:.0f} €)")
    if durations:
        log(f"Durée médiane           : {statistics.median(durations):.1f} s (max {max(durations):.1f} s)")
    if tokens:
        log(f"Tokens médians          : {int(statistics.median(tokens))}")
    log(f"Journal                 : {LOG.relative_to(ROOT)}")


def main() -> None:
    p = argparse.ArgumentParser(description="Test de l'agent de rachat Easy Cash")
    p.add_argument("--all", action="store_true", help="lance les 11 objets de référence")
    p.add_argument("--product")
    p.add_argument("--category", choices=sorted(START_URLS), default="smartphone")
    p.add_argument("--details", default="")
    p.add_argument("--condition", default="Bon état")
    p.add_argument("--parallel", type=int, default=3, help="sessions H simultanées (défaut 3, limite du compte)")
    args = p.parse_args()

    if args.all:
        jobs = [(prod, cat, det, exp) for prod, cat, det, exp in REFERENCE]
    elif args.product:
        jobs = [(args.product, args.category, args.details, None)]
    else:
        p.error("donner --all ou --product")

    load_dotenv(ROOT / ".env")
    client = Client()  # lit HAI_API_KEY dans l'environnement

    def one(job):
        prod, cat, det, exp = job
        r = run_buyback(client, prod, cat, args.condition, det, log=log)
        append_log(r, args.condition, exp)
        report(r, exp)
        return r, exp

    with ThreadPoolExecutor(max_workers=max(1, args.parallel)) as pool:
        rows = list(pool.map(one, jobs))
    summary(rows)


if __name__ == "__main__":
    main()
