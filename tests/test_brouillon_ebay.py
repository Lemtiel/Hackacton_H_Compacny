"""Brouillon eBay par un agent H : la route est fermée sans clé de démo, ne laisse pas les photos sur le disque, ne publie jamais.
Aucun réseau, aucun agent lancé : l'agent est simulé. Lancer :  .venv/bin/python tests/test_brouillon_ebay.py"""

import io
import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ["DEMO_KEY"] = "cle-demo-test"

from fastapi.testclient import TestClient  # noqa: E402

from agents import ebay_draft  # noqa: E402
from backend import main  # noqa: E402

failed = 0
total = 0


def check(label, ok):
    global failed, total
    total += 1
    if not ok:
        failed += 1
    print(("OK     " if ok else "ÉCHEC  ") + label)


# 1. Lien de l'éditeur : même règle que frontend/lib/ebayLink.ts
u = ebay_draft.list_url("Console Nintendo Switch, bon état", "139971", "Bon état")
check("lien : titre, catégorie, état Occasion (3000)", "categoryId=139971" in u and "condition=3000" in u and "mode=AddItem" in u and u.startswith("https://www.ebay.fr/sl/list?"))
check("lien : « Pour pièces » = 7000", "condition=7000" in ebay_draft.list_url("Switch HS", "139971", "Pour pièces"))
check("lien : sans catégorie, pas de categoryId", "categoryId" not in ebay_draft.list_url("Switch", None, "Bon état"))
check("lien : titre coupé à 80 caractères", len(ebay_draft.list_url("x" * 120, "1", "Bon état").split("title=")[1].split("&")[0]) == 80)

# 2. Résultat de l'agent
r = ebay_draft.DraftResult.model_validate({"status": "draft_saved", "photos_uploaded": 3, "description_filled": True, "price_set": True})
check("résultat : brouillon enregistré lu", r.status == "draft_saved" and r.photos_uploaded == 3)
try:
    ebay_draft.DraftResult.model_validate({"status": "published"})
    published_refused = False
except Exception:
    published_refused = True
check("résultat : le statut « published » n'existe pas (jamais de publication)", published_refused)
task = ebay_draft._task("Titre", "Description de test assez longue", 120)
check("consigne : interdit de publier", "NEVER click" in task and "Mettre en vente" in task)
check("consigne : arrêt sur connexion ou vérification", "login_required" in task and "Never type a password" in task)

# 3. Route
client = TestClient(main.app)
jpeg = io.BytesIO()
from PIL import Image  # noqa: E402

Image.new("RGB", (40, 40), (30, 111, 217)).save(jpeg, "JPEG")
photo = ("photo-1.jpg", jpeg.getvalue(), "image/jpeg")
form = {"title": "Apple iPhone 11 noir", "description": "Description de test assez longue", "price": "141", "condition": "Bon état"}


def post(files=None, key="cle-demo-test", **over):
    data = {**form, "key": key, **over}
    return client.post("/api/ebay/draft", data=data, files=files if files is not None else [("files", photo)])


main.EBAY_DRAFT_LOCAL = False
check("fonction désactivée : 404", post().status_code == 404)
main.EBAY_DRAFT_LOCAL = True
check("sans clé de démo : 403", post(key="").status_code == 403)
check("mauvaise clé de démo : 403", post(key="autre").status_code == 403)
check("sans photo : 422", client.post("/api/ebay/draft", data={**form, "key": "cle-demo-test"}).status_code == 422)
check("fichier qui n'est pas une image : 422", post(files=[("files", ("a.txt", b"hello", "text/plain"))]).status_code == 422)
check("prix négatif : 422", post(price="-3").status_code == 422)

ebay_draft.chrome_ready = lambda: False
check("Chrome eBay fermé : 409 avec la marche à suivre", (lambda r: r.status_code == 409 and "ebay_chrome.sh" in r.json()["detail"])(post()))

# Parcours complet, agent simulé
seen_paths = []


def fake_run(client_, *, photos, title, description, price, category_id, condition, emit, stop):
    seen_paths.extend(photos)
    check("agent simulé : les photos existent pendant la session", all(Path(p).exists() for p in photos))
    emit({"type": "step", "label": "L'agent ouvre l'éditeur eBay", "steps": 1})
    return ebay_draft.DraftResult(status="draft_saved", photos_uploaded=len(photos), description_filled=True, price_set=True, draft_url="https://www.ebay.fr/lstng?draftId=1")


ebay_draft.chrome_ready = lambda: True
ebay_draft.run_draft = fake_run
r = post()
events = [json.loads(l[5:]) for l in r.text.splitlines() if l.startswith("data:")]
types = [e["type"] for e in events]
check("flux : start, step, result, done dans l'ordre", types == ["start", "step", "result", "done"])
check("flux : résultat « brouillon enregistré », jamais « publié »", events[2]["status"] == "draft_saved" and "published" not in r.text)
check("photos effacées du disque après la session", seen_paths and not any(Path(p).exists() for p in seen_paths))
check("verrou « un seul brouillon à la fois » libéré", main._draft_running is False)
check("aucun dossier temporaire oublié", not [d for d in Path(tempfile.gettempdir()).glob("snapncash-draft-*")])

print(f"{total - failed}/{total} vérifications correctes")
sys.exit(1 if failed else 0)
