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
MAX_PHOTOS = 3  # face, dos ou étiquette, détail
IDENTIFY_SECONDS = 15  # par tentative, 2 tentatives au plus
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
    kind: Optional[str] = None  # description générique pour élargir la recherche : « manette PS5 »


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
    "You identify second-hand consumer electronics and video games from photos. "
    "You may receive up to 3 photos of the SAME object (front, back or label, a detail): combine what they show. "
    "Answer with ONE JSON object and nothing else, with these keys: "
    '"is_object" (boolean: false if the photo does not show a tech product or a video game), '
    '"brand" (string or null), "model" (string or null, the exact commercial model name), '
    '"variant" (string or null: storage capacity, colour or edition, only if visible), '
    f'"category" (one of: {", ".join(CATEGORIES)}, autre), '
    '"condition" (string or null, in French: visible wear such as "rayures sur l\'écran", or "bon état apparent"), '
    '"confidence" (number from 0 to 1 for brand and model), '
    '"kind" (string or null, in French, 2 to 4 words: the generic product type plus its platform or brand, '
    'as a shopper would type it in a search bar, e.g. "manette PS5", "console Nintendo Switch", '
    '"smartphone Apple", "jeu PS4", "casque Sony"). '
    "Read any text printed on the product. Do not guess a model you cannot see evidence for: "
    "use null and a low confidence instead."
)


def _parse_json(text: str) -> dict:
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        raise PhotoError("Le modèle n'a pas rendu de réponse exploitable. Tapez le nom de l'objet.")
    return json.loads(m.group(0))


def identify(imgs: "Image.Image | list[Image.Image]") -> Identification:
    token = os.getenv("HF_TOKEN")
    if not token:
        raise PhotoError("La reconnaissance photo est momentanément indisponible. Tapez le nom de l'objet.")
    from openai import OpenAI

    if not isinstance(imgs, list):
        imgs = [imgs]
    images = []
    for img in imgs[:MAX_PHOTOS]:
        buf = io.BytesIO()
        img.save(buf, "JPEG", quality=85)
        url = "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()
        images.append({"type": "image_url", "image_url": {"url": url}})
    # Même parade que pour l'annonce (listing.py) : le routeur répartit les appels entre fournisseurs de vitesse
    # très inégale (2 s d'ordinaire, 40 s mesurées le 17/11 avec 2 photos). On demande le plus rapide,
    # on coupe une tentative à IDENTIFY_SECONDS et on retente une fois.
    model = os.getenv("HF_VISION_MODEL") or DEFAULT_VISION_MODEL
    if ":" not in model:
        model += ":fastest"
    client = OpenAI(base_url="https://router.huggingface.co/v1", api_key=token, timeout=IDENTIFY_SECONDS, max_retries=0)
    resp = None
    for _ in range(2):
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": [
                    {"type": "text", "text": PROMPT},
                    *images,
                ]}],
                max_tokens=300,
                temperature=0,
            )
            break
        except Exception:
            continue
    if resp is None:
        raise PhotoError("L'identification n'a pas abouti. Réessayez dans un instant, ou tapez le nom de l'objet.")
    try:
        raw = _parse_json(resp.choices[0].message.content or "")
        ident = Identification(**{k: v for k, v in raw.items() if k in Identification.model_fields})
    except PhotoError:
        raise
    except Exception as e:
        raise PhotoError("Le modèle n'a pas rendu de réponse exploitable. Tapez le nom de l'objet.") from e
    if ident.category not in CATEGORIES:
        ident.category = "autre"
    # « Apple » + « Apple Watch » : la marque est déjà dans le modèle, on ne la répète pas (relevé du 18/11 : « Apple Apple Watch »).
    brand, model = (ident.brand or "").strip(), (ident.model or "").strip()
    ident.product = model if brand and model.lower().startswith(brand.lower()) else " ".join(x for x in (brand, model) if x)
    ident.kind = clean_hint(ident.kind)
    return ident


def clean_hint(text: Optional[str]) -> Optional[str]:
    """Description générique réduite à des mots simples : elle part dans la consigne de l'agent."""
    if not text:
        return None
    words = re.findall(r"[0-9A-Za-zÀ-ÿ+-]+", text)[:4]
    out = " ".join(words)[:40].strip()
    return out or None


def check_and_identify(data: "bytes | list[bytes]") -> Identification:
    """Jusqu'à 3 photos du même objet. Chacune passe le contrôle de visage avant tout appel au modèle."""
    datas = data if isinstance(data, list) else [data]
    imgs = []
    for i, d in enumerate(datas[:MAX_PHOTOS], start=1):
        img = load_image(d)
        if count_faces(img) > 0:
            which = "la photo" if len(datas) == 1 else f"la photo {i}"
            raise PhotoError(f"Un visage apparaît sur {which}. Reprenez une photo de l'objet seul.")
        imgs.append(img)
    return identify(imgs)
