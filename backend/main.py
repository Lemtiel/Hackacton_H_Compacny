"""Serveur Snap N Cash (FastAPI).

  POST /api/identify   photo -> contrôle visage -> identification (marque, modèle, état)
  GET  /api/search     recherche des prix en boutique, résultats envoyés site par site (SSE)
  POST /api/listing    annonce rédigée en 4 formats (Vinted, Leboncoin, eBay, générique)
  GET  /api/ebay       bloc « Vendre seul » : annonces eBay en cours (API Browse), séparées des boutiques
  GET  /api/ebay/category  catégorie eBay suggérée pour publier (API Taxonomy), sans compte utilisateur
  POST /api/studio     photo studio : objet détouré sur fond clair, objet non modifié
  GET  /api/shot/{id}  mode démo : dernière capture d'écran d'un agent, relayée sans être enregistrée

Rien n'est conservé : ni photo, ni annonce relevée. Les résultats ne vivent que le temps de la requête.

Lancer :  .venv/bin/uvicorn backend.main:app --reload --port 8000
"""

from __future__ import annotations

import asyncio
import json
import os
import secrets
import shutil
import tempfile
import threading
import time
from collections import defaultdict, deque
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, Query, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response, StreamingResponse
import httpx
from hai_agents import Client

from agents.price_agent import MAX_SECONDS, run_site
from agents.sites import CATEGORIES, SITES, sites_for
from backend import ebay, listing, matching, photo, pricing, studio

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

MAX_UPLOAD = 8 * 1024 * 1024
# Notre organisation H autorise 10 sessions simultanées (relevé par H Company le 19/11). La variable permet de réduire
# volontairement la consommation, mais jamais de dépasser cette limite.
MAX_PARALLEL = max(1, min(int(os.getenv("HAI_MAX_PARALLEL", "10")), 10))
_slots = threading.Semaphore(MAX_PARALLEL)

# Mode démo : captures d'écran des agents, montrées en direct (règle 9, décision du 19/11). S'active avec DEMO_SHOTS=1
# côté serveur ; l'interface l'affiche par défaut, l'interrupteur de Réglages le coupe.
DEMO_SHOTS = os.getenv("DEMO_SHOTS", "") == "1"
SHOT_TTL_S = 600
# Jeton aléatoire -> (adresse H de la capture, heure d'expiration). En mémoire seulement, aucune image sur disque.
_shots: dict[str, tuple[str, float]] = {}
_shots_lock = threading.Lock()


# Garde-fous d'usage, pour une app en ligne sans compte : chaque recherche lance jusqu'à 6 sessions H payantes,
# chaque photo studio est facturée par fal.ai. Valeurs réglables dans .env.
SEARCH_PER_HOUR = int(os.getenv("SEARCH_PER_HOUR") or "20")  # recherches par adresse IP et par heure
STUDIO_PER_HOUR = int(os.getenv("STUDIO_PER_HOUR") or "40")  # photos studio par adresse IP et par heure
MAX_SEARCHES = int(os.getenv("MAX_SEARCHES") or "4")  # recherches en cours en même temps, toutes adresses confondues
STUDIO_ENABLED = (os.getenv("STUDIO_ENABLED") or "1") == "1"
# Routes facturées (routeur Hugging Face) ou soumises au quota quotidien d'eBay : plafond par IP aussi (revue du 19/11).
# Alignés sur SEARCH_PER_HOUR=200 du Space : une salle partage une IP, et une estimation appelle eBay 2 fois.
IDENTIFY_PER_HOUR = int(os.getenv("IDENTIFY_PER_HOUR") or "400")  # identifications par IP et par heure
LISTING_PER_HOUR = int(os.getenv("LISTING_PER_HOUR") or "400")  # rédactions d'annonce par IP et par heure
EBAY_PER_HOUR = int(os.getenv("EBAY_PER_HOUR") or "800")  # appels eBay par IP et par heure (2 par estimation)
# Brouillon eBay par un agent H dans le Chrome local de l'utilisateur : démo sur son ordinateur seulement, jamais sur le Space
# (le serveur ne peut pas piloter un Chrome distant). Réservé à la clé de démo : il agit sur UN compte eBay.
EBAY_DRAFT_LOCAL = (os.getenv("EBAY_DRAFT_LOCAL") or "0") == "1"
_draft_running = False
_draft_lock = threading.Lock()
_hits: dict[tuple[str, str], deque] = defaultdict(deque)
_hits_lock = threading.Lock()
_running = 0
_running_lock = threading.Lock()


def _client_ip(request: Request) -> str:
    """Adresse du client pour les limites d'usage.

    X-Forwarded-For se lit de droite à gauche : chaque proxy ajoute à la fin l'adresse qui lui parle. La première
    entrée est celle que le client déclare lui-même (falsifiable) ; la dernière est celle que le proxy du Space a
    vue. TRUSTED_PROXIES (défaut 1) = nombre de proxys de confiance devant le serveur."""
    hops = max(1, int(os.getenv("TRUSTED_PROXIES") or "1"))
    fwd = [x.strip() for x in request.headers.get("x-forwarded-for", "").split(",") if x.strip()]
    if len(fwd) >= hops:
        return fwd[-hops]
    return request.client.host if request.client else "inconnue"


DEMO_TOKEN_TTL_S = 3600
_demo_tokens: dict[str, float] = {}  # jeton temporaire -> expiration, en mémoire
_demo_tokens_lock = threading.Lock()


def _demo_key_ok(key: str) -> bool:
    """Clé de démo (DEMO_KEY dans .env) ou jeton temporaire obtenu avec elle : lève la limite par adresse IP, pour que
    la démo ne soit pas bloquée par les autres personnes du même Wi-Fi. Le plafond de recherches simultanées s'applique
    toujours. Le jeton sert à /api/search, dont l'adresse (EventSource, sans en-tête possible) apparaît dans les
    journaux et l'historique : la vraie clé n'y passe plus."""
    expected = os.getenv("DEMO_KEY") or ""
    if not (expected and key):
        return False
    if secrets.compare_digest(key, expected):
        return True
    with _demo_tokens_lock:
        exp = _demo_tokens.get(key)
        return exp is not None and exp > time.time()


def _new_demo_token() -> str:
    now = time.time()
    token = secrets.token_urlsafe(18)
    with _demo_tokens_lock:
        for k in [k for k, exp in _demo_tokens.items() if exp < now]:
            del _demo_tokens[k]
        _demo_tokens[token] = now + DEMO_TOKEN_TTL_S
    return token


def _allow(kind: str, ip: str, per_hour: int) -> bool:
    """Fenêtre glissante d'une heure, en mémoire. True si l'appel est permis (et le compte)."""
    now = time.time()
    with _hits_lock:
        q = _hits[(kind, ip)]
        while q and q[0] < now - 3600:
            q.popleft()
        if len(q) >= per_hour:
            return False
        q.append(now)
        return True


def _limit(request: Request, kind: str, per_hour: int) -> None:
    """Refus 429 au-delà du plafond horaire par IP. La clé de démo (en-tête X-Demo-Key) lève la limite."""
    if _demo_key_ok(request.headers.get("x-demo-key", "")):
        return
    if not _allow(kind, _client_ip(request), per_hour):
        raise HTTPException(429, "Vous avez fait beaucoup de demandes en peu de temps. Réessayez dans un moment.")


def _register_shot(url: str) -> str:
    now = time.time()
    token = secrets.token_urlsafe(16)
    with _shots_lock:
        for k in [k for k, (_, exp) in _shots.items() if exp < now]:
            del _shots[k]
        _shots[token] = (url, now + SHOT_TTL_S)
    return token


app = FastAPI(title="Snap N Cash")

# Interface Next.js (Vercel) sur une autre adresse : origines autorisées dans ALLOWED_ORIGINS, séparées par des virgules.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",") if o.strip()],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.post("/api/demo/token")
def demo_token(request: Request):
    """Échange la clé de démo (en-tête X-Demo-Key, jamais dans l'adresse) contre un jeton valable 1 h."""
    expected = os.getenv("DEMO_KEY") or ""
    key = request.headers.get("x-demo-key", "")
    if not (expected and key and secrets.compare_digest(key, expected)):
        raise HTTPException(403, "Clé de démo absente ou incorrecte.")
    return {"token": _new_demo_token(), "ttl_s": DEMO_TOKEN_TTL_S}


@app.get("/api/health")
def health():
    """Vérifie que les clés sont bien réglées (booléens seulement, jamais les valeurs) : à ouvrir après un déploiement."""
    return {
        "ok": True,
        "agents_h": bool(os.getenv("HAI_API_KEY")),
        "hugging_face": bool(os.getenv("HF_TOKEN")),
        "ebay": ebay.configured(),
        "cle_demo": bool(os.getenv("DEMO_KEY")),
        "studio": STUDIO_ENABLED,
        "max_agents": MAX_PARALLEL,
        "brouillon_ebay": EBAY_DRAFT_LOCAL,
    }


@app.get("/")
def index():
    return FileResponse(Path(__file__).parent / "static" / "index.html")


@app.get("/api/config")
def config():
    return {
        "categories": CATEGORIES,
        "sites": [{"key": k, "name": v["name"], "sells": v["sells"]} for k, v in SITES.items()],
        "max_seconds": MAX_SECONDS,
        "vision_model": (os.getenv("HF_VISION_MODEL") or photo.DEFAULT_VISION_MODEL),
        "identify_ready": bool(os.getenv("HF_TOKEN")),
        "ebay_ready": ebay.configured(),
        "conditions": listing.CONDITIONS,
        "demo_shots": DEMO_SHOTS,
    }


@app.post("/api/identify")
async def identify(request: Request, files: list[UploadFile] = File(None), file: UploadFile = File(None)):
    # Jusqu'à 3 photos du même objet (« files ») ; « file » seul reste accepté par la page de test.
    uploads = [u for u in (files or []) if u] + ([file] if file else [])
    if not uploads:
        raise HTTPException(422, "Aucune photo reçue.")
    _limit(request, "identify", IDENTIFY_PER_HOUR)
    if len(uploads) > photo.MAX_PHOTOS:
        raise HTTPException(422, f"{photo.MAX_PHOTOS} photos au maximum.")
    datas = []
    for u in uploads:
        data = await u.read(MAX_UPLOAD + 1)
        if len(data) > MAX_UPLOAD:
            raise HTTPException(413, "Photo trop lourde (8 Mo maximum).")
        datas.append(data)
    try:
        ident = await asyncio.to_thread(photo.check_and_identify, datas)
    except photo.PhotoError as e:
        raise HTTPException(422, str(e))
    except Exception:
        raise HTTPException(502, "L'identification a échoué. Tapez le nom de l'objet.")
    if not ident.is_object or not ident.product:
        raise HTTPException(422, "Objet non reconnu. Reprenez la photo ou tapez le nom de l'objet.")
    # Marque seule, ou téléphone sans numéro de modèle (« Apple iPhone ») : on demande le modèle exact.
    vague = not ident.model or (
        ident.category in ("smartphone", "tablette") and not any(c.isdigit() for c in ident.product)
    )
    return {**ident.model_dump(), "needs_model": vague or ident.confidence < 0.6}


# Le détourage occupe le processeur plusieurs secondes : une seule photo studio à la fois.
_studio_slot = threading.Semaphore(1)


@app.post("/api/ebay/draft")
async def ebay_draft(
    request: Request,
    files: list[UploadFile] = File(...),
    title: str = Form(..., min_length=2, max_length=80),
    description: str = Form(..., min_length=10, max_length=5000),
    price: float = Form(..., gt=0, lt=100000),
    category_id: str = Form("", max_length=12),
    condition: str = Form("Bon état", max_length=20),
    key: str = Form("", max_length=100),
    consent: str = Form("", max_length=1),
):
    """Un agent H prépare un BROUILLON eBay dans le Chrome local (photos, description, prix) et ne publie jamais.
    Réponse : flux d'événements (progression, puis résultat)."""
    if not EBAY_DRAFT_LOCAL:
        raise HTTPException(404, "Cette fonction n'est pas activée sur ce serveur.")
    if not _demo_key_ok(key or request.headers.get("x-demo-key", "")):
        raise HTTPException(403, "Clé de démo absente ou incorrecte. Rouvrez l'app avec ?cle=VOTRE_CLE dans l'adresse, sans virgule ni point à la fin.")
    # L'utilisateur autorise l'agent à agir dans son navigateur connecté à eBay, à chaque brouillon (écran de consentement).
    if consent != "1":
        raise HTTPException(403, "Autorisation manquante : validez l'écran d'autorisation avant de lancer l'agent.")
    if not 1 <= len(files) <= 10:
        raise HTTPException(422, "Entre 1 et 10 photos.")
    blobs: list[tuple[bytes, str]] = []
    for f in files:
        data = await f.read()
        ext = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}.get((f.content_type or "").lower())
        if ext is None or not data or len(data) > 6 * 1024 * 1024:
            raise HTTPException(422, "Photos JPEG, PNG ou WebP de 6 Mo au plus.")
        blobs.append((data, ext))
    from agents import ebay_draft

    if not ebay_draft.chrome_ready():
        raise HTTPException(409, "Le Chrome eBay n'est pas ouvert : lancez scripts/ebay_chrome.sh et connectez-vous à eBay.")

    loop = asyncio.get_running_loop()
    queue: asyncio.Queue = asyncio.Queue()
    stop = threading.Event()
    tmp = Path(tempfile.mkdtemp(prefix="snapncash-draft-"))
    paths = []
    for i, (data, ext) in enumerate(blobs, 1):
        p = tmp / f"photo-{i}.{ext}"
        p.write_bytes(data)
        paths.append(p)
    cond = condition if condition in listing.CONDITIONS else "Bon état"

    def emit(ev: dict) -> None:
        loop.call_soon_threadsafe(queue.put_nowait, ev)

    def work() -> None:
        try:
            res = ebay_draft.run_draft(Client(), photos=paths, title=title, description=description, price=price,
                                       category_id=category_id or None, condition=cond, emit=emit, stop=stop)
            emit({"type": "result", **(res.model_dump() if res else {"status": "cancelled", "note": "Interrompu."})})
        except Exception as e:  # la cause technique reste dans le journal du serveur, pas dans l'écran
            print(f"[brouillon eBay] {type(e).__name__}: {e}")
            emit({"type": "result", "status": "blocked", "note": "L'agent n'a pas pu démarrer. Vérifiez le Chrome eBay et réessayez."})
        finally:
            emit({"type": "done"})

    async def stream():
        global _draft_running
        with _draft_lock:
            busy = _draft_running
            if not busy:
                _draft_running = True
        if busy:
            shutil.rmtree(tmp, ignore_errors=True)
            yield _sse({"type": "result", "status": "blocked", "note": "Un brouillon est déjà en cours de préparation."})
            yield _sse({"type": "done"})
            return
        try:
            yield _sse({"type": "start", "photos": len(paths)})
            threading.Thread(target=work, daemon=True).start()
            while True:
                ev = await queue.get()
                yield _sse(ev)
                if ev["type"] == "done":
                    break
        finally:
            stop.set()
            shutil.rmtree(tmp, ignore_errors=True)  # les photos ne restent pas sur le disque
            with _draft_lock:
                _draft_running = False

    return StreamingResponse(stream(), media_type="text/event-stream", headers=SSE_HEADERS)


@app.post("/api/studio")
async def make_studio(request: Request, file: UploadFile = File(...)):
    if not STUDIO_ENABLED:
        raise HTTPException(503, "Les photos studio sont désactivées pour le moment.")
    if not _demo_key_ok(request.headers.get("x-demo-key", "")) and not _allow("studio", _client_ip(request), STUDIO_PER_HOUR):
        raise HTTPException(429, "Trop de photos studio d'un coup. Réessayez dans un moment.")
    data = await file.read(MAX_UPLOAD + 1)
    if len(data) > MAX_UPLOAD:
        raise HTTPException(413, "Photo trop lourde (8 Mo maximum).")

    def work() -> bytes:
        img = photo.load_image(data)
        if photo.count_faces(img) > 0:  # règle 6 : aucune photo avec un visage
            raise photo.PhotoError("Un visage apparaît sur la photo. Reprenez une photo de l'objet seul.")
        with _studio_slot:
            return studio.make_studio(img)

    try:
        jpeg = await asyncio.to_thread(work)
    except (photo.PhotoError, studio.StudioError) as e:
        raise HTTPException(422, str(e))
    except Exception:
        raise HTTPException(502, "La photo studio a échoué. Réessayez dans un instant.")
    return Response(jpeg, media_type="image/jpeg", headers={"Cache-Control": "no-store"})


@app.post("/api/listing")
async def make_listing(req: listing.ListingRequest, request: Request):
    if req.condition not in listing.CONDITIONS:
        raise HTTPException(422, "État inconnu.")
    _limit(request, "listing", LISTING_PER_HOUR)
    try:
        return await asyncio.to_thread(listing.generate, req)
    except listing.ListingError as e:
        raise HTTPException(422, str(e))
    except Exception:
        raise HTTPException(502, "La rédaction a échoué. Réessayez dans un instant.")


@app.get("/api/ebay")
async def ebay_prices(
    request: Request,
    product: str = Query(..., min_length=2, max_length=120),
    category: str = Query("smartphone"),
):
    # Bloc séparé des boutiques (licence eBay) : ses prix ne passent ni dans shop_block ni dans un modèle de texte.
    if category not in CATEGORIES:
        raise HTTPException(422, "Catégorie inconnue.")
    _limit(request, "ebay", EBAY_PER_HOUR)
    try:
        return await ebay.search(product, category)
    except ebay.EbayNotConfigured:
        return {"state": "non_configure", "block": None, "items": []}
    except ebay.EbayError:
        return {"state": "indisponible", "block": None, "items": []}


@app.get("/api/ebay/category")
async def ebay_category(
    request: Request,
    product: str = Query(..., min_length=2, max_length=120),
    category: str | None = Query(None),
):
    # Aide à la publication : catégorie suggérée par eBay (API Taxonomy), triée avec notre catégorie.
    # L'utilisateur publie lui-même.
    if category is not None and category not in CATEGORIES:
        raise HTTPException(422, "Catégorie inconnue.")
    _limit(request, "ebay", EBAY_PER_HOUR)
    try:
        return await ebay.suggest_category(product, category)
    except ebay.EbayNotConfigured:
        return {"state": "non_configure", "categories": []}
    except ebay.EbayError:
        return {"state": "indisponible", "categories": []}


@app.get("/api/shot/{token}")
async def shot(token: str):
    # La capture se lit chez H avec notre clé : on la relaie octet par octet, sans la garder.
    if not DEMO_SHOTS:
        raise HTTPException(404)
    with _shots_lock:
        entry = _shots.get(token)
    if not entry or entry[1] < time.time():
        raise HTTPException(404)
    try:
        # H redirige vers l'image ; httpx retire l'en-tête Authorization si la redirection change d'hôte.
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as c:
            r = await c.get(entry[0], headers={"Authorization": f"Bearer {os.getenv('HAI_API_KEY', '')}"})
    except httpx.HTTPError:
        raise HTTPException(502)
    if r.status_code != 200 or not r.headers.get("content-type", "").startswith("image/"):
        raise HTTPException(502)
    return Response(r.content, media_type=r.headers["content-type"], headers={"Cache-Control": "no-store"})


def _site_payload(site: str, r, product: str, category: str, condition: str = "Bon état") -> dict:
    # Seules les annonces du même modèle comptent : les autres sont écartées par notre code.
    matched, rejected_model = matching.filter_offers(product, category, r.offers)
    # L'état classe les offres au lieu de les exclure (issue #23) : même état d'abord, voisins s'il en manque.
    ranked, rejected_unverified = matching.rank_by_condition(matched, condition)
    kept = [o for o, _ in ranked]
    rejected = rejected_model + rejected_unverified
    # Une session coupée au délai (ou en échec) mais qui a déjà rendu des offres : elles passent les mêmes contrôles que les
    # autres (modèle, état, lien), on les garde. Test réel du 18/11 : Easy Cash rendait 2 offres « Bon état », jetées à tort.
    broken = r.cancelled or r.status in ("failed", "timed_out", "interrupted", "error")
    if broken and not r.offers:
        state = "indisponible"
    elif kept:
        state = "ok"
    else:
        state = "aucun_resultat"
    return {
        "type": "site_result", "site": site, "state": state,
        "duration_s": r.duration_s, "steps": r.steps,
        "offers": [{**o.model_dump(), "condition_match": m} for o, m in ranked] if state == "ok" else [],
        "n_rejected": rejected if state != "indisponible" else 0,
    }


@app.get("/api/search")
async def search(
    request: Request,
    product: str = Query(..., min_length=2, max_length=120),
    category: str = Query("smartphone"),
    demo: bool = Query(False),
    hint: str = Query("", max_length=60),
    condition: str = Query("Bon état", max_length=30),
    box: bool | None = Query(None),
    accessories: str = Query("", max_length=200),
    details: str = Query("", max_length=400),
    key: str = Query("", max_length=100),
):
    if category not in CATEGORIES:
        raise HTTPException(422, "Catégorie inconnue.")
    if condition not in listing.CONDITIONS:
        raise HTTPException(422, "État inconnu.")
    shots = demo and DEMO_SHOTS
    hint = photo.clean_hint(hint)  # description générique (« manette PS5 ») pour élargir la recherche de l'agent
    if not os.getenv("HAI_API_KEY"):
        raise HTTPException(503, "Nos agents sont momentanément indisponibles. Réessayez dans quelques minutes.")

    # Refus envoyé comme un événement du flux : EventSource ne lit pas le code HTTP, l'interface affiche le message.
    def refuse(message: str):
        async def one():
            yield _sse({"type": "error", "message": message})
            yield _sse({"type": "done"})
        return StreamingResponse(one(), media_type="text/event-stream", headers=SSE_HEADERS)

    if not _demo_key_ok(key) and not _allow("search", _client_ip(request), SEARCH_PER_HOUR):
        return refuse("Vous avez lancé beaucoup d'estimations en peu de temps. Réessayez dans un moment.")

    loop = asyncio.get_running_loop()
    stop = threading.Event()  # levé quand l'utilisateur quitte la recherche
    queue: asyncio.Queue = asyncio.Queue()
    client = Client()
    active = sites_for(category, product)

    def emit(ev: dict) -> None:
        loop.call_soon_threadsafe(queue.put_nowait, ev)

    def work(site: str) -> None:
        emit({"type": "site_step", "site": site, "label": "en attente d'un agent libre"})
        while not _slots.acquire(timeout=1):
            if stop.is_set():
                return  # recherche abandonnée avant même d'obtenir une place
        try:
            if stop.is_set():
                return
            emit({"type": "site_step", "site": site, "label": f"ouvre {SITES[site]['name']}"})
            try:
                r = run_site(
                    client, site, product, category, log=lambda _m: None, hint=hint,
                    condition=condition, box=box, accessories=accessories, details=details, stop=stop,
                    on_step=lambda s: emit({
                        "type": "site_step", "site": site, "elapsed_s": s["elapsed_s"],
                        "label": "démarrage du navigateur" if s["steps"] == 0 else f"navigue, étape {s['steps']}",
                    }),
                    on_shot=(lambda url: emit({"type": "site_shot", "site": site, "shot": _register_shot(url)})) if shots else None,
                )
                emit(_site_payload(site, r, product, category, condition))
            except Exception:
                emit({"type": "site_result", "site": site, "state": "indisponible", "offers": []})
        finally:
            _slots.release()

    async def stream():
        # La place est prise ici, dans le flux, et rendue dans son « finally » : si le navigateur part avant le
        # premier octet, le flux ne démarre jamais et aucune place n'est prise (pas de compteur bloqué).
        global _running
        with _running_lock:
            full = _running >= MAX_SEARCHES
            if not full:
                _running += 1
        if full:
            yield _sse({"type": "error", "message": "Nos agents sont tous occupés. Réessayez dans une minute."})
            yield _sse({"type": "done"})
            return
        try:
            yield _sse({
                "type": "start", "product": product, "category": category,
                "sites": [{"key": k, "name": v["name"], "active": k in active} for k, v in SITES.items()],
            })
            for s in active:
                threading.Thread(target=work, args=(s,), daemon=True).start()
            prices: list[float] = []
            remaining = len(active)
            while remaining:
                ev = await queue.get()
                if ev["type"] == "site_result":
                    remaining -= 1
                    prices += [o["price_eur"] for o in ev["offers"]]
                    yield _sse(ev)
                    yield _sse({"type": "shop_block", "block": pricing.shop_block(prices, category)})
                else:
                    yield _sse(ev)
            yield _sse({"type": "done"})
        finally:
            # Fin normale ou navigateur parti : on arrête les agents encore en route et on libère la place.
            stop.set()
            with _running_lock:
                _running -= 1

    return StreamingResponse(stream(), media_type="text/event-stream", headers=SSE_HEADERS)


# X-Accel-Buffering : demande aux proxys (nginx, celui du Space) de ne pas retenir le flux, pour que les résultats arrivent boutique par boutique
SSE_HEADERS = {"Cache-Control": "no-store", "X-Accel-Buffering": "no"}


def _sse(ev: dict) -> str:
    return f"data: {json.dumps(ev, ensure_ascii=False)}\n\n"
