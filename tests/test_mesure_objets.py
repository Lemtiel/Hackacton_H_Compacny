"""Script de mesure (#8), sans aucun appel réseau : bloc eBay pris comme dans l'app, objets en parallèle,
pic de sessions H simultanées.

Lancer : .venv/bin/python tests/test_mesure_objets.py
"""

import os
import sys
import threading
import time
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("HAI_API_KEY", "cle-de-test")

from agents import mesure_objets as m  # noqa: E402

total = failed = 0


def check(label: str, ok: bool) -> None:
    global total, failed
    total += 1
    if not ok:
        failed += 1
    print(("OK   " if ok else "ÉCHEC ") + label)


def fake_run_site(client, site, product, category, log, condition):
    time.sleep(0.2)  # laisse les sessions se chevaucher
    return SimpleNamespace(duration_s=0.2, input_tokens=10, output_tokens=5, note="ok")


def fake_payload(site, r, product, category, condition):
    return {"state": "ok", "offers": [{"price_eur": p} for p in (200.0, 210.0, 220.0)], "n_rejected": 0}


m.run_site, m._site_payload = fake_run_site, fake_payload


def with_ebay(result):
    m.ebay_prices = lambda product, category: result


with_ebay({"etat": "ok", "n": 40, "bas": 230, "haut": 280, "conseille": 260})
s, rows = m.measure(None, {"objet": "Apple iPhone 13 128 Go", "categorie": "smartphone", "etat": "Bon état",
                           "prix_vendu_eur": "250"}, threading.Semaphore(10))
check("eBay répond : prix « vendre seul » pris chez eBay (260 €)", s["source_prix"] == "ebay" and s["prix_conseille"] == 260)
check("eBay : état et nombre d'annonces notés", s["ebay_etat"] == "ok" and s["ebay_n"] == 40)
check("écart au prix vendu (250 €) : +4 %, référence dans la fourchette", s["ecart_pct"] == 4.0 and s["ref_dans_fourchette"] == "oui")
check("une ligne par site du smartphone, toutes réussies", len(rows) == len(m.sites_for("smartphone")) and all(r["reussi"] == "oui" for r in rows))

with_ebay({"etat": "non_configure"})
s, _ = m.measure(None, {"objet": "Nintendo Switch", "categorie": "console", "etat": "Bon état"}, threading.Semaphore(10))
check("sans eBay : prix estimé depuis les boutiques", s["source_prix"] == "boutiques" and s["ebay_etat"] == "non_configure")
check("sans prix de référence : pas d'écart calculé", "ecart_pct" not in s)

with_ebay({"etat": "aucun_resultat"})
conc, slots = m.Concurrency(), threading.Semaphore(10)
objs = [{"objet": n, "categorie": "smartphone", "etat": "Bon état"} for n in ("Apple iPhone 13 128 Go", "Apple iPhone 12 64 Go")]
threads = [threading.Thread(target=m.measure, args=(None, o, slots, conc)) for o in objs]
[t.start() for t in threads]
[t.join() for t in threads]
check("2 smartphones en parallèle : pic de 10 sessions H", conc.peak == 10)
check("toutes les sessions terminées : compteur revenu à 0", conc.now == 0)

conc = m.Concurrency()
m.measure(None, {"objet": "Apple iPhone 13 128 Go", "categorie": "smartphone"}, threading.Semaphore(3), conc)
check("plafond à 3 respecté", conc.peak == 3)

print(f"{total - failed}/{total} vérifications correctes")
sys.exit(1 if failed else 0)
