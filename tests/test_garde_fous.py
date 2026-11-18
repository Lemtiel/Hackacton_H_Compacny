"""Garde-fous du serveur, sans aucun appel réseau : arrêt des agents quand l'utilisateur part,
limites d'usage, coefficient de rachat mesuré.

Lancer : .venv/bin/python tests/test_garde_fous.py
"""

import asyncio
import json
import os
import sys
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("HAI_API_KEY", "cle-de-test")

from agents import price_agent  # noqa: E402
from types import SimpleNamespace  # noqa: E402

from backend import main, pricing  # noqa: E402

failed = 0
total = 0


def check(label, ok):
    global failed, total
    total += 1
    if not ok:
        failed += 1
    print(("OK     " if ok else "ÉCHEC  ") + label)


# 1. Une session dont la recherche est abandonnée est annulée au tour suivant, sans attendre 90 s.
class FakeStatus:
    def __init__(self, status):
        self.status, self.steps, self.outcome, self.error_code, self.usage_per_model = status, 1, None, None, []


class FakeHandle:
    id = "s1"

    def __init__(self):
        self.cancelled = False
        self.polls = 0

    def status(self):
        self.polls += 1
        return FakeStatus("cancelled" if self.cancelled else "running")

    def cancel(self):
        self.cancelled = True

    def force_answer(self):
        pass

    def get(self):
        return type("S", (), {"agent_view_url": None, "latest_answer": None})()


class FakeClient:
    def __init__(self):
        self.handle = FakeHandle()

    def start_session(self, **_):
        return self.handle


price_agent.POLL_SECONDS = 0.01
price_agent.TERMINAL = price_agent.TERMINAL | {"cancelled"}
client, stop = FakeClient(), threading.Event()
stop.set()
r = price_agent.run_site(client, "easycash", "Nintendo Switch", "console", log=lambda _m: None, stop=stop)
check("session annulée dès que la recherche est abandonnée", client.handle.cancelled and r.cancelled)
check("annulée en moins de 5 tours de surveillance", client.handle.polls < 5)


# 2. Limites d'usage : le refus part comme un événement du flux, avec un message lisible.
async def first_events(resp):
    out = []
    async for chunk in resp.body_iterator:
        out.append(json.loads(chunk.removeprefix("data: ").strip()))
    return out


class FakeRequest:
    def __init__(self, xff="198.51.100.9, 203.0.113.7", demo_key=""):
        self.headers = {"x-forwarded-for": xff, "x-demo-key": demo_key}
        self.client = None


def search(req, key=""):
    return asyncio.run(main.search(req, product="Nintendo Switch", category="console", demo=False, hint="",
                                   condition="Bon état", box=None, accessories="", details="", key=key))


check("adresse lue à droite : celle vue par le proxy, pas celle déclarée par le client",
      main._client_ip(FakeRequest()) == "203.0.113.7")
check("sans en-tête de proxy : adresse de la connexion", main._client_ip(FakeRequest(xff="")) == "inconnue")

main._running = main.MAX_SEARCHES
ev = asyncio.run(first_events(search(FakeRequest())))
check("plafond de recherches simultanées : refus « agents tous occupés »", ev[0]["type"] == "error" and "occupés" in ev[0]["message"])
check("le flux refusé se termine par « done »", ev[-1]["type"] == "done")
check("un refus ne prend pas de place", main._running == main.MAX_SEARCHES)
main._running = 0

resp = search(FakeRequest(xff="198.51.100.20"))  # flux créé mais jamais lu : navigateur parti avant le 1er octet
del resp
check("flux jamais démarré : aucune place prise (pas de compteur bloqué)", main._running == 0)

ip = "203.0.113.50"
main._hits[("search", ip)].extend([__import__("time").time()] * main.SEARCH_PER_HOUR)
ev = asyncio.run(first_events(search(FakeRequest(xff=ip))))
check(f"limite par IP ({main.SEARCH_PER_HOUR} par heure) : refus", ev[0]["type"] == "error" and "beaucoup" in ev[0]["message"])

os.environ["DEMO_KEY"] = "cle-demo-test"
check("clé de démo correcte acceptée", main._demo_key_ok("cle-demo-test"))
check("clé de démo fausse ou vide refusée", not main._demo_key_ok("autre") and not main._demo_key_ok(""))
main._running = main.MAX_SEARCHES  # la clé lève la limite par IP, pas le plafond global : rien ne démarre
ev = asyncio.run(first_events(search(FakeRequest(xff=ip), key="cle-demo-test")))
check("avec la clé, la limite par IP ne bloque plus (seul le plafond global répond)", "occupés" in ev[0]["message"])
main._running = 0
del os.environ["DEMO_KEY"]

# 3. Coefficient de rachat mesuré : 0,59 par défaut, puis par catégorie (docs/calibrage-rachat.md).
b = pricing.shop_block([150, 166, 180])
check("rachat = médiane × 0,59 (166 € → 97,94 €)", pricing.BUYBACK_COEF == 0.59 and b["buyback_estimate"] == 97.94)
b = pricing.shop_block([150, 166, 180], "smartphone")
check("smartphone : médiane × 0,60 (166 € → 99,60 €), coef renvoyé", b["buyback_estimate"] == 99.6 and b["coef"] == 0.60)
b = pricing.shop_block([20, 25, 30], "jeu_video")
check("jeu vidéo : médiane × 0,43 (25 € → 10,75 €)", b["buyback_estimate"] == 10.75)
b = pricing.shop_block([100, 110, 120], "console")
check("console sous 300 € : médiane × 0,44 (110 € → 48,40 €)", b["buyback_estimate"] == 48.4)
b = pricing.shop_block([500, 550, 600], "console")
check("console à 300 € et plus : médiane × 0,74 (550 € → 407 €)", b["buyback_estimate"] == 407.0)
b = pricing.shop_block([150, 166, 180], "montre")
check("catégorie inconnue : 0,59 par défaut", b["coef"] == 0.59 and b["buyback_estimate"] == 97.94)

# 4. Une session coupée au délai qui a déjà rendu des offres valides : on les garde (Easy Cash, 18/11).
from agents.price_agent import Offer  # noqa: E402


def result(status, cancelled, offers):
    return SimpleNamespace(status=status, cancelled=cancelled, offers=offers, duration_s=95.0, steps=12)


good = [Offer(title="Console Nintendo Switch", price_eur=170, condition="Bon état", url="https://shop.example/switch-1"),
        Offer(title="Console Nintendo Switch grise", price_eur=240, condition="Bon état", url="https://shop.example/switch-2")]
p = main._site_payload("easycash", result("idle", True, good), "Nintendo Switch", "console", "Bon état")
check("coupée au délai mais 2 offres valides rendues : site « ok », 2 prix gardés", p["state"] == "ok" and len(p["offers"]) == 2)
p = main._site_payload("easycash", result("interrupted", True, []), "Nintendo Switch", "console", "Bon état")
check("coupée sans aucune offre : « indisponible »", p["state"] == "indisponible")
p = main._site_payload("easycash", result("failed", False, []), "Nintendo Switch", "console", "Bon état")
check("session en échec sans offre : « indisponible »", p["state"] == "indisponible")
bad = [Offer(title="Nintendo Switch Lite", price_eur=120, condition="Bon état", url="https://shop.example/lite")]
p = main._site_payload("easycash", result("idle", True, bad), "Nintendo Switch", "console", "Bon état")
check("coupée, mais offres d'un autre modèle : elles restent écartées (« aucun_resultat »)", p["state"] == "aucun_resultat" and p["offers"] == [])
gc = [Offer(title="Console Nintendo Switch", price_eur=p_, condition="Occasion reconditionnée", url=f"https://gamecash.example/s{p_}") for p_ in (166, 174, 179, 194)]
p = main._site_payload("gamecash", result("completed", False, gc), "Nintendo Switch", "console", "Bon état")
check("Gamecash (« Occasion reconditionnée », sans grade) : 4 prix gardés, plus 0", p["state"] == "ok" and len(p["offers"]) == 4)

print(f"{total - failed}/{total} vérifications correctes")
sys.exit(1 if failed else 0)
