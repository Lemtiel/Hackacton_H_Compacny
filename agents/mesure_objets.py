"""Mesure sur un jeu d'objets : les chiffres que le jury attend (taux de réussite, latence, écart de prix, cas d'échec).

Entrée : un CSV (par défaut mesures/objets_a_mesurer.csv), une ligne par objet :
  objet                 nom exact, comme on le taperait dans l'app (« Apple iPhone 13 128 Go »)
  categorie             smartphone | console | jeu_video | tablette | informatique
  etat                  Comme neuf | Très bon état | Bon état | État correct | Pour pièces
  prix_vendu_eur        prix RÉELLEMENT VENDU sur eBay, relevé à la main (la référence des Specs) ; vide = pas d'écart calculé
  photos                facultatif : chemins de 1 à 3 photos séparés par « ; » pour mesurer l'identification
  modele_attendu        facultatif : le nom que l'identification doit trouver (sinon « objet »)

Chaque objet passe par le même chemin que l'app : agents H sur les boutiques de la catégorie (en parallèle,
HAI_MAX_PARALLEL au plus), tri par modèle et par état, bloc magasin (médiane, coefficient de rachat), bloc eBay
(API Browse, annonces en cours) pour le prix « vendre seul », comme l'interface. Sans clés eBay ou sans résultat eBay,
le prix « vendre seul » est estimé depuis les boutiques (même hypothèse que l'interface, SELL_ALONE_DISCOUNT).
--parallele N traite N objets en même temps : avec 2 smartphones (5 sites chacun), 10 sessions H tournent ensemble.

Sorties (dans mesures/, datées) :
  mesure_sites_<date>.csv     une ligne par objet et par site : état, nombre de prix, durée, jetons, note de l'agent
  mesure_objets_<date>.csv    une ligne par objet : identification, durée totale, prix, écart à la référence
  et un résumé imprimé : taux de réussite par site, latence médiane, écart médian, référence dans la fourchette.

Lancer :
  .venv/bin/python -m agents.mesure_objets                       # le CSV par défaut
  .venv/bin/python -m agents.mesure_objets --csv mes_objets.csv --limite 3
  .venv/bin/python -m agents.mesure_objets --parallele 2              # 2 objets à la fois (test des 10 agents)

Coût : environ 4 à 6 sessions H par objet (environ 80 s chacune). Ne pas lancer sur la clé de démo pendant une démo.
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import os
import statistics
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

from hai_agents import Client  # noqa: E402

from agents.price_agent import AGENT, run_site  # noqa: E402
from agents.sites import CATEGORIES, SITES, sites_for  # noqa: E402
from backend import ebay, matching, pricing  # noqa: E402
from backend.main import _site_payload  # noqa: E402  (même tri que l'app)

# Même hypothèse que frontend/lib/verdict.ts, tant que le bloc eBay n'a pas ses clés.
SELL_ALONE_DISCOUNT = 0.15
MIN_PRICES_OK = 3  # critère des Specs : une session réussie rapporte au moins 3 prix
PARALLEL = max(1, min(int(os.getenv("HAI_MAX_PARALLEL") or "10"), 10))
_print = threading.Lock()


class Concurrency:
    """Compte les sessions H en cours et retient le pic (preuve du test des 10 agents en parallèle)."""

    def __init__(self) -> None:
        self.lock, self.now, self.peak = threading.Lock(), 0, 0

    def enter(self) -> None:
        with self.lock:
            self.now += 1
            self.peak = max(self.peak, self.now)

    def leave(self) -> None:
        with self.lock:
            self.now -= 1


def ebay_prices(product: str, category: str) -> dict:
    """Bloc eBay de l'app (API Browse). Rend {etat, n, bas, haut, conseille}, ou {etat} si eBay ne répond rien."""
    if not ebay.configured():
        return {"etat": "non_configure"}
    try:
        r = asyncio.run(ebay.search(product, category))
    except Exception as e:  # panne réseau ou quota : la mesure continue sans eBay
        return {"etat": f"erreur : {e}"[:80]}
    b = r.get("block")
    if r.get("state") != "ok" or not b:
        return {"etat": r.get("state") or "aucun_resultat"}
    return {"etat": "ok", "n": b["n_kept"], "bas": b["sell_low"], "haut": b["sell_high"], "conseille": b["sell_price"]}


def log(msg: str) -> None:
    with _print:
        print(msg, flush=True)


def identify(paths: str, expected: str, category: str) -> tuple[str, str, float | None]:
    """Rend (produit trouvé, correct ? oui/non/vide, durée). Vide si aucune photo n'est donnée."""
    files = [p.strip() for p in (paths or "").split(";") if p.strip()]
    if not files:
        return "", "", None
    from backend import photo

    t = time.monotonic()
    try:
        ident = photo.check_and_identify([Path(f).expanduser().read_bytes() for f in files[:3]])
        found = ident.product
    except Exception as e:  # refus (visage, objet non reconnu) ou panne : compté comme un échec
        return f"échec : {e}"[:120], "non", round(time.monotonic() - t, 1)
    ok = matching.reject_reason(expected, category, found) is None
    return found, "oui" if ok else "non", round(time.monotonic() - t, 1)


def measure(client: Client, obj: dict, slots: threading.Semaphore,
            conc: Concurrency | None = None) -> tuple[dict, list[dict]]:
    product, category, condition = obj["objet"].strip(), obj["categorie"].strip(), (obj.get("etat") or "Bon état").strip()
    sites = sites_for(category)
    t0 = time.monotonic()

    def one(site: str) -> dict:
        with slots:
            if conc:
                conc.enter()
            try:
                r = run_site(client, site, product, category, log=lambda _m: None, condition=condition)
            finally:
                if conc:
                    conc.leave()
        p = _site_payload(site, r, product, category, condition)
        n = len(p["offers"])
        return {
            "objet": product, "site": site, "etat_site": p["state"], "n_prix": n,
            "reussi": "oui" if n >= MIN_PRICES_OK else "non", "duree_s": r.duration_s,
            "jetons": (r.input_tokens or 0) + (r.output_tokens or 0), "ecartees": p.get("n_rejected", 0),
            "prix": " ".join(f"{o['price_eur']:.0f}" for o in p["offers"]), "note_agent": (r.note or "")[:160],
            "_offers": p["offers"],
        }

    with ThreadPoolExecutor(max_workers=len(sites) + 1) as ex:
        eb_future = ex.submit(ebay_prices, product, category)  # eBay répond en 1 à 2 s, en parallèle des agents
        rows = list(ex.map(one, sites))
        eb = eb_future.result()
    total_s = round(time.monotonic() - t0, 1)

    prices = [o["price_eur"] for r in rows for o in r.pop("_offers")]
    block = pricing.shop_block(prices, category)
    found, ident_ok, ident_s = identify(obj.get("photos", ""), (obj.get("modele_attendu") or product).strip(), category)
    ref = float(obj["prix_vendu_eur"]) if (obj.get("prix_vendu_eur") or "").strip() else None
    summary = {
        "objet": product, "categorie": category, "etat": condition,
        "identification": found, "identification_correcte": ident_ok, "identification_s": ident_s if ident_s is not None else "",
        "duree_totale_s": total_s, "sites": len(sites), "sites_reussis": sum(r["reussi"] == "oui" for r in rows),
        "n_prix": len(prices), "prix_vendu_ref": ref if ref is not None else "",
        "ebay_etat": eb["etat"], "ebay_n": eb.get("n", ""),
    }
    if block:
        summary.update({"boutique_mediane": block["shop_median"], "rachat_estime": block["buyback_estimate"]})
    # Prix « vendre seul » : même règle que frontend/lib/verdict.ts (eBay d'abord, sinon boutiques moins 15 %).
    if eb["etat"] == "ok":
        low, high, mid, source = eb["bas"], eb["haut"], eb["conseille"], "ebay"
    elif block:
        k = 1 - SELL_ALONE_DISCOUNT
        low, high = round(block["shop_low"] * k), round(block["shop_median"] * k)
        mid, source = round((low + high) / 2), "boutiques"
    else:
        low = high = mid = source = None
    if mid is not None:
        summary.update({"vendre_seul_bas": low, "vendre_seul_haut": high, "prix_conseille": mid, "source_prix": source})
        if ref:
            summary["ecart_pct"] = round(100 * (mid - ref) / ref, 1)
            summary["ref_dans_fourchette"] = "oui" if low <= ref <= high else "non"
    return summary, rows


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--csv", default=str(ROOT / "mesures" / "objets_a_mesurer.csv"))
    ap.add_argument("--limite", type=int, default=0, help="n'en mesurer que les N premiers")
    ap.add_argument("--parallele", type=int, default=1, help="nombre d'objets mesurés en même temps (défaut : 1)")
    a = ap.parse_args()

    objs = [o for o in csv.DictReader(open(a.csv, encoding="utf-8")) if (o.get("objet") or "").strip()]
    bad = [o["objet"] for o in objs if o.get("categorie", "").strip() not in CATEGORIES]
    if bad:
        raise SystemExit(f"Catégorie inconnue pour : {', '.join(bad)} (attendu : {', '.join(CATEGORIES)})")
    if a.limite:
        objs = objs[: a.limite]
    log(f"{len(objs)} objet(s), agent {AGENT}, {PARALLEL} sessions H en parallèle au plus.")

    client, slots, conc = Client(), threading.Semaphore(PARALLEL), Concurrency()

    def run(i: int, obj: dict) -> tuple[dict, list[dict]]:
        log(f"[{i}/{len(objs)}] {obj['objet']} …")
        s, rows = measure(client, obj, slots, conc)
        log(f"    {obj['objet']} : {s['sites_reussis']}/{s['sites']} sites à ≥ {MIN_PRICES_OK} prix, {s['n_prix']} prix, "
            f"eBay {s['ebay_etat']}, {s['duree_totale_s']} s" + (f", écart {s['ecart_pct']} %" if "ecart_pct" in s else ""))
        return s, rows

    # Les sites d'un objet tournent toujours en parallèle ; --parallele N lance aussi N objets à la fois.
    with ThreadPoolExecutor(max_workers=max(1, a.parallele)) as ex:
        results = list(ex.map(lambda p: run(*p), enumerate(objs, 1)))
    summaries = [s for s, _ in results]
    site_rows = [r for _, rows in results for r in rows]

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%Hh%M")
    out = ROOT / "mesures"
    for name, data in ((f"mesure_sites_{stamp}.csv", site_rows), (f"mesure_objets_{stamp}.csv", summaries)):
        cols = list(dict.fromkeys(k for row in data for k in row))
        with open(out / name, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            w.writerows(data)
        log(f"Écrit : mesures/{name}")

    # Résumé : les chiffres du pitch, avec leurs cas d'échec.
    log("\n=== Résumé ===")
    for site in SITES:
        rs = [r for r in site_rows if r["site"] == site]
        if rs:
            ok = sum(r["reussi"] == "oui" for r in rs)
            fails = sum(r["etat_site"] == "indisponible" for r in rs)
            log(f"{SITES[site]['name']:16} {ok}/{len(rs)} sessions à ≥ {MIN_PRICES_OK} prix ({100 * ok / len(rs):.0f} %), "
                f"{fails} indisponible(s), durée médiane {statistics.median(r['duree_s'] for r in rs):.0f} s")
    allr = len(site_rows)
    if allr:
        ok = sum(r["reussi"] == "oui" for r in site_rows)
        log(f"Toutes boutiques : {ok}/{allr} sessions réussies ({100 * ok / allr:.0f} %, objectif des Specs ≥ 80 %)")
    log(f"Pic de sessions H simultanées : {conc.peak} (plafond {PARALLEL})")
    if summaries:
        log(f"Durée médiane d'une estimation : {statistics.median(s['duree_totale_s'] for s in summaries):.0f} s (objectif < 120 s)")
    ecarts = [abs(s["ecart_pct"]) for s in summaries if "ecart_pct" in s]
    if ecarts:
        inside = sum(s.get("ref_dans_fourchette") == "oui" for s in summaries if "ecart_pct" in s)
        log(f"Écart médian prix conseillé / prix vendu : {statistics.median(ecarts):.1f} % (objectif ≤ 15 %) ; "
            f"référence dans la fourchette : {inside}/{len(ecarts)} (objectif ≥ 80 %)")
    idents = [s for s in summaries if s["identification_correcte"]]
    if idents:
        good = sum(s["identification_correcte"] == "oui" for s in idents)
        log(f"Identification correcte : {good}/{len(idents)} (objectif ≥ 90 %)")
    no_price = [s["objet"] for s in summaries if not s["n_prix"]]
    if no_price:
        log(f"Cas d'échec, aucun prix : {', '.join(no_price)}")


if __name__ == "__main__":
    main()
