"""Contrôle et identification de la photo.

La photo est traitée en mémoire uniquement : jamais écrite sur disque, jamais journalisée.

Deux modèles Hugging Face, PROPOSÉS et en attente de validation (voir JOURNAL.md) :
- visages : opencv/face_detection_yunet, exécuté en local (la photo ne sort pas du serveur) ;
- identification : modèle vision appelé par le routeur Hugging Face, choisi par HF_VISION_MODEL.
"""

from __future__ import annotations

import base64
import io
import json
import os
import re
from functools import lru_cache
from pathlib import Path
from typing import Optional

import cv2
import httpx
import numpy as np
from PIL import Image, ImageOps
from pydantic import BaseModel

from agents.sites import CATEGORIES

MAX_SIDE = 1024
FACE_SCORE = 0.8
DEFAULT_VISION_MODEL = "google/gemma-4-31B-it"


class PhotoError(ValueError):
    """Photo refusée, avec un message affichable à l'utilisateur."""


class Identification(BaseModel):
    is_object: bool = True
    brand: Optional[str] = None
    model: Optional[str] = None
    variant: Optional[str] = None  # capacité, couleur, édition
    category: str = "autre"
    condition: Optional[str] = None
    confidence: float = 0.0
    product: str = ""  # texte de recherche : marque + modèle


def load_image(data: bytes) -> Image.Image:
    try:
        img = Image.open(io.BytesIO(data))
        img = ImageOps.exif_transpose(img).convert("RGB")
    except Exception as e:
        raise PhotoError("Ce fichier n'est pas une image lisible.") from e
    img.thumbnail((MAX_SIDE, MAX_SIDE))
    return img


YUNET_URL = "https://huggingface.co/opencv/face_detection_yunet/resolve/main/face_detection_yunet_2023mar.onnx"
YUNET_FILE = Path(__file__).parent / "models" / "face_detection_yunet_2023mar.onnx"


@lru_cache(maxsize=1)
def _yunet_path() -> str:
    """Télécharge le modèle (230 Ko) depuis Hugging Face au premier appel, puis le garde en local."""
    if not YUNET_FILE.exists():
        YUNET_FILE.parent.mkdir(exist_ok=True)
        data = httpx.get(YUNET_URL, timeout=30, follow_redirects=True).raise_for_status().content
        tmp = YUNET_FILE.with_suffix(".part")
        tmp.write_bytes(data)
        tmp.replace(YUNET_FILE)
    return str(YUNET_FILE)


def count_faces(img: Image.Image) -> int:
    bgr = cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)
    h, w = bgr.shape[:2]
    det = cv2.FaceDetectorYN.create(_yunet_path(), "", (w, h), FACE_SCORE)
    _, faces = det.detect(bgr)
    return 0 if faces is None else len(faces)


PROMPT = (
    "You identify second-hand consumer electronics and video games from a photo. "
    "Answer with ONE JSON object and nothing else, with these keys: "
    '"is_object" (boolean: false if the photo does not show a tech product or a video game), '
    '"brand" (string or null), "model" (string or null, the exact commercial model name), '
    '"variant" (string or null: storage capacity, colour or edition, only if visible), '
    f'"category" (one of: {", ".join(CATEGORIES)}, autre), '
    '"condition" (string or null, in French: visible wear such as "rayures sur l\'écran", or "bon état apparent"), '
    '"confidence" (number from 0 to 1 for brand and model). '
    "Read any text printed on the product. Do not guess a model you cannot see evidence for: "
    "use null and a low confidence instead."
)


def _parse_json(text: str) -> dict:
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        raise PhotoError("Le modèle n'a pas rendu de réponse exploitable. Tapez le nom de l'objet.")
    return json.loads(m.group(0))


def identify(img: Image.Image) -> Identification:
    token = os.getenv("HF_TOKEN")
    if not token:
        raise PhotoError("Identification indisponible : HF_TOKEN manque dans .env. Tapez le nom de l'objet.")
    from openai import OpenAI

    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=85)
    url = "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()
    client = OpenAI(base_url="https://router.huggingface.co/v1", api_key=token, timeout=40)
    resp = client.chat.completions.create(
        model=(os.getenv("HF_VISION_MODEL") or DEFAULT_VISION_MODEL),
        messages=[{"role": "user", "content": [
            {"type": "text", "text": PROMPT},
            {"type": "image_url", "image_url": {"url": url}},
        ]}],
        max_tokens=300,
        temperature=0,
    )
    try:
        raw = _parse_json(resp.choices[0].message.content or "")
        ident = Identification(**{k: v for k, v in raw.items() if k in Identification.model_fields})
    except PhotoError:
        raise
    except Exception as e:
        raise PhotoError("Le modèle n'a pas rendu de réponse exploitable. Tapez le nom de l'objet.") from e
    if ident.category not in CATEGORIES:
        ident.category = "autre"
    ident.product = " ".join(x for x in (ident.brand, ident.model) if x).strip()
    return ident


def check_and_identify(data: bytes) -> Identification:
    img = load_image(data)
    if count_faces(img) > 0:
        raise PhotoError("Un visage apparaît sur la photo. Reprenez une photo de l'objet seul.")
    return identify(img)
