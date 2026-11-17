"""Test des agents H sur les sites boutiques.

Exemples :
  .venv/bin/python -m agents.test_agents --site troc --product "Xiaomi Redmi Note 10S" --category smartphone
  .venv/bin/python -m agents.test_agents --all --product "Nintendo Switch" --category console

Chaque run ajoute une ligne à mesures/agent_runs.csv (journal de l'Agent API).
Le journal ne garde que des chiffres (statut, durée, tokens, nombre de prix) :
aucune annonce relevée n'est conservée.
"""

from __future__ import annotations

import argparse
import csv
import statistics
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from hai_agents import Client

from agents.price_agent import AGENT, RunResult, run_site
from agents.sites import CATEGORIES, SITES

ROOT = Path(__file__).resolve().parent.parent
LOG = ROOT / "mesures" / "agent_runs.csv"
FIELDS = [
    "date_utc", "site", "product", "agent", "status", "outcome", "error_code", "available",
    "duration_s", "steps", "input_tokens", "cached_tokens", "output_tokens",
    "n_prices", "forced_answer", "cancelled", "session_id", "note",
]
_print_lock = threading.Lock()


def log(msg: str) -> None:
    with _print_lock:
        print(msg, flush=True)


def append_log(r: RunResult) -> None:
    LOG.parent.mkdir(exist_ok=True)
    new = not LOG.exists()
    with LOG.open("a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new:
            w.writeheader()
        w.writerow({
            "date_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "site": r.site, "product": r.product, "agent": AGENT,
            "status": r.status, "outcome": r.outcome, "error_code": r.error_code,
            "available": r.available, "duration_s": r.duration_s, "steps": r.steps,
            "input_tokens": r.input_tokens, "cached_tokens": r.cached_tokens,
            "output_tokens": r.output_tokens, "n_prices": len(r.offers),
            "forced_answer": r.forced_answer, "cancelled": r.cancelled,
            "session_id": r.session_id, "note": (r.note or "")[:200],
        })


def report(r: RunResult) -> None:
    lines = [
        f"\n=== {SITES[r.site]['name']} : {r.status} / {r.outcome} "
        f"({r.duration_s}s, {r.steps} étapes, {r.input_tokens + r.output_tokens} tokens)",
    ]
    if r.error_code:
        lines.append(f"  erreur : {r.error_code}")
    prices = [o.price_eur for o in r.offers]
    for o in r.offers:
        lines.append(f"  {o.price_eur:>8.2f} €  {o.condition or '-':<12} {o.title[:60]}  {o.url or ''}")
    if prices:
        lines.append(f"  {len(prices)} prix, médiane {statistics.median(prices):.2f} €")
    if r.note:
        lines.append(f"  note : {r.note}")
    if r.agent_view_url:
        lines.append(f"  Agent View : {r.agent_view_url}")
    log("\n".join(lines))


def one(client: Client, site: str, product: str, category: str, hint: str | None = None) -> RunResult:
    try:
        r = run_site(client, site, product, category, log=log, hint=hint)
    except Exception as e:  # erreur API : on la journalise aussi
        r = RunResult(site=site, product=product, status="error", note=f"{type(e).__name__}: {e}")
    append_log(r)
    report(r)
    return r


def main() -> None:
    load_dotenv(ROOT / ".env")
    p = argparse.ArgumentParser()
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--site", choices=list(SITES))
    g.add_argument("--all", action="store_true", help="les 4 sites en parallèle")
    p.add_argument("--product", required=True)
    p.add_argument("--category", choices=CATEGORIES, default="smartphone")
    p.add_argument("--hint", default=None, help="description générique, ex. « manette PS5 »")
    a = p.parse_args()

    client = Client()
    sites = list(SITES) if a.all else [a.site]
    with ThreadPoolExecutor(max_workers=len(sites)) as ex:
        results = list(ex.map(lambda s: one(client, s, a.product, a.category, a.hint), sites))

    ok = sum(r.available for r in results)
    log(f"\nRésumé : {ok}/{len(results)} sites disponibles. Journal : {LOG.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
