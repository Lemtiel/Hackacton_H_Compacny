"""Serveur Snap N Cash (FastAPI).

  POST /api/identify   photo -> contrôle visage -> identification (marque, modèle, état)
  GET  /api/search     recherche des prix en boutique, résultats envoyés site par site (SSE)
  POST /api/listing    annonce rédigée en 4 formats (Vinted, Leboncoin, eBay, générique)

Rien n'est conservé : ni photo, ni annonce relevée. Les résultats ne vivent que le temps de la requête.

Lancer :  .venv/bin/uvicorn backend.main:app --reload --port 8000
"""

from __future__ import annotations

import asyncio
import json
import os
import threading
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from hai_agents import Client

from agents.price_agent import MAX_SECONDS, run_site
from agents.sites import CATEGORIES, SITES, sites_for
from backend import listing, matching, photo, pricing

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

MAX_UPLOAD = 8 * 1024 * 1024
# Le compte H autorise 3 sessions simultanées : au-delà, un site attend son tour.
MAX_PARALLEL = int(os.getenv("HAI_MAX_PARALLEL", "3"))
_slots = threading.Semaphore(MAX_PARALLEL)

app = FastAPI(title="Snap N Cash")

# Interface Next.js (Vercel) sur une autre adresse : origines autorisées dans ALLOWED_ORIGINS, séparées par des virgules.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",") if o.strip()],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


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
        "conditions": listing.CONDITIONS,
    }


@app.post("/api/identify")
async def identify(file: UploadFile = File(...)):
    data = await file.read(MAX_UPLOAD + 1)
    if len(data) > MAX_UPLOAD:
        raise HTTPException(413, "Photo trop lourde (8 Mo maximum).")
    try:
        ident = await asyncio.to_thread(photo.check_and_identify, data)
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


@app.post("/api/listing")
async def make_listing(req: listing.ListingRequest):
    if req.condition not in listing.CONDITIONS:
        raise HTTPException(422, "État inconnu.")
    try:
        return await asyncio.to_thread(listing.generate, req)
    except listing.ListingError as e:
        raise HTTPException(422, str(e))
    except Exception:
        raise HTTPException(502, "La rédaction a échoué. Réessayez dans un instant.")


def _site_payload(site: str, r, product: str, category: str) -> dict:
    # Seules les annonces du même modèle comptent : les autres sont écartées par notre code.
    kept, rejected = matching.filter_offers(product, category, r.offers)
    if r.cancelled or r.status in ("failed", "timed_out", "interrupted", "error"):
        state = "indisponible"
    elif kept:
        state = "ok"
    else:
        state = "aucun_resultat"
    return {
        "type": "site_result", "site": site, "state": state,
        "duration_s": r.duration_s, "steps": r.steps,
        "offers": [o.model_dump() for o in kept] if state == "ok" else [],
        "n_rejected": rejected if state != "indisponible" else 0,
    }


@app.get("/api/search")
async def search(
    product: str = Query(..., min_length=2, max_length=120),
    category: str = Query("smartphone"),
):
    if category not in CATEGORIES:
        raise HTTPException(422, "Catégorie inconnue.")
    if not os.getenv("HAI_API_KEY"):
        raise HTTPException(503, "HAI_API_KEY manque dans .env.")

    loop = asyncio.get_running_loop()
    queue: asyncio.Queue = asyncio.Queue()
    client = Client()
    active = sites_for(category)

    def emit(ev: dict) -> None:
        loop.call_soon_threadsafe(queue.put_nowait, ev)

    def work(site: str) -> None:
        emit({"type": "site_step", "site": site, "label": "en attente d'un agent libre"})
        with _slots:
            emit({"type": "site_step", "site": site, "label": f"ouvre {SITES[site]['name']}"})
            try:
                r = run_site(
                    client, site, product, category, log=lambda _m: None,
                    on_step=lambda s: emit({
                        "type": "site_step", "site": site, "elapsed_s": s["elapsed_s"],
                        "label": "démarrage du navigateur" if s["steps"] == 0 else f"navigue, étape {s['steps']}",
                    }),
                )
                emit(_site_payload(site, r, product, category))
            except Exception:
                emit({"type": "site_result", "site": site, "state": "indisponible", "offers": []})

    async def stream():
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
                yield _sse({"type": "shop_block", "block": pricing.shop_block(prices)})
            else:
                yield _sse(ev)
        yield _sse({"type": "done"})

    return StreamingResponse(stream(), media_type="text/event-stream", headers={"Cache-Control": "no-store"})


def _sse(ev: dict) -> str:
    return f"data: {json.dumps(ev, ensure_ascii=False)}\n\n"
