"""Studio photo : la vraie photo de l'objet, détourée et posée sur un fond clair. Notre code, plus un modèle de détourage.

Modèles validés par Jude le 17/11 :
- principal : briaai/RMBG-2.0, appelé via Hugging Face chez le fournisseur fal.ai (« fal-ai/bria/background/remove »).
  Carte graphique : 1 à 2 s mesurées. La photo part chez fal.ai, sans visage (contrôle avant) et sans métadonnées
  (réencodée en JPEG). Payé à l'image sur les crédits Hugging Face.
- secours : ZhengPeng7/BiRefNet_lite (licence MIT), version ONNX d'onnx-community, sur notre serveur avec
  onnxruntime. Lent sans carte graphique (57 à 85 s mesurées sur un Mac M1 8 Go saturé). Rien ne sort du serveur.
Aucune photo n'est conservée.

L'objet n'est jamais redessiné : seuls le fond, le cadrage et une ombre douce changent. Une annonce doit montrer
l'objet réel, rayures comprises. L'interface l'affiche : « fond retouché, objet non modifié ».
"""

from __future__ import annotations

import io
import threading
from pathlib import Path

import httpx
import numpy as np
from PIL import Image, ImageFilter

# Révision figée : le fichier téléchargé ne change pas sans qu'on le décide.
MODEL_REVISION = "de15b22ba131738a16dff04aab8bdf8dc32e3ac1"
MODEL_URL = (
    "https://huggingface.co/onnx-community/BiRefNet_lite-ONNX/resolve/"
    f"{MODEL_REVISION}/onnx/model.onnx"
)
MODEL_FILE = Path(__file__).parent / "models" / "birefnet_lite.onnx"
SIZE = 1024  # entrée du modèle
MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)

OUT_SIDE = 1200  # photo studio carrée, la taille conseillée par les sites d'annonces
BACKGROUND = (246, 246, 244)  # blanc cassé, comme un fond de studio
FILL = 0.78  # part du cadre occupée par l'objet
MIN_COVER = 0.01  # sous 1 % de pixels détourés, le détourage a échoué

_session = None
_lock = threading.Lock()


class StudioError(ValueError):
    """Photo studio impossible, avec un message affichable."""


def _model_path() -> str:
    """Télécharge le modèle (224 Mo) depuis Hugging Face au premier appel, puis le garde en local."""
    if not MODEL_FILE.exists():
        MODEL_FILE.parent.mkdir(exist_ok=True)
        tmp = MODEL_FILE.with_suffix(".part")
        with httpx.stream("GET", MODEL_URL, timeout=120, follow_redirects=True) as r:
            r.raise_for_status()
            with open(tmp, "wb") as f:
                for chunk in r.iter_bytes():
                    f.write(chunk)
        tmp.replace(MODEL_FILE)
    return str(MODEL_FILE)


def _get_session():
    global _session
    with _lock:
        if _session is None:
            import onnxruntime as ort

            _session = ort.InferenceSession(_model_path(), providers=["CPUExecutionProvider"])
    return _session


PROVIDER_MODEL = "briaai/RMBG-2.0"
PROVIDER = "fal-ai"
PROVIDER_TIMEOUT_S = 20


def mask_remote(img: Image.Image) -> Image.Image:
    """Masque calculé par Bria RMBG-2.0 chez fal.ai, via le routeur Hugging Face."""
    import os

    from huggingface_hub import InferenceClient

    token = os.getenv("HF_TOKEN")
    if not token:
        raise StudioError("Studio indisponible : HF_TOKEN manque.")
    buf = io.BytesIO()
    img.convert("RGB").save(buf, "JPEG", quality=90)  # réencodage : aucune métadonnée (GPS, appareil) ne part
    client = InferenceClient(provider=PROVIDER, api_key=token, timeout=PROVIDER_TIMEOUT_S)
    segs = client.image_segmentation(buf.getvalue(), model=PROVIDER_MODEL)
    if not segs:
        raise StudioError("Le détourage n'a rien rendu.")
    m = segs[0].mask
    m = m.getchannel("A") if m.mode in ("RGBA", "LA") else m.convert("L")
    return m.resize(img.size, Image.BILINEAR) if m.size != img.size else m


def mask_of(img: Image.Image) -> Image.Image:
    """Masque de l'objet (niveaux de gris, 255 = objet), à la taille de la photo : Bria d'abord, BiRefNet en secours."""
    import os

    if os.getenv("STUDIO_LOCAL") != "1":
        try:
            return mask_remote(img)
        except StudioError:
            raise
        except Exception:
            pass  # fournisseur indisponible : on bascule sur le modèle local
    return mask_local(img)


def mask_local(img: Image.Image) -> Image.Image:
    """Masque calculé sur notre serveur par BiRefNet_lite (lent sans carte graphique)."""
    x = np.asarray(img.convert("RGB").resize((SIZE, SIZE), Image.BILINEAR), dtype=np.float32) / 255.0
    x = ((x - MEAN) / STD).transpose(2, 0, 1)[None]
    sess = _get_session()
    out = sess.run(None, {sess.get_inputs()[0].name: x.astype(np.float32)})[0][0, 0]
    prob = 1.0 / (1.0 + np.exp(-out))
    m = Image.fromarray((prob * 255).astype(np.uint8), "L").resize(img.size, Image.BILINEAR)
    return m


def compose(img: Image.Image, mask: Image.Image) -> Image.Image:
    """Objet recadré, centré sur fond clair, avec une ombre douce sous lui."""
    bbox = mask.point(lambda v: 255 if v > 128 else 0).getbbox()
    cover = np.asarray(mask, dtype=np.uint8).mean() / 255.0
    if not bbox or cover < MIN_COVER:
        raise StudioError("Impossible de détacher l'objet du fond. Essayez avec une photo plus nette, objet bien visible.")

    obj = img.convert("RGB").crop(bbox)
    alpha = mask.crop(bbox)
    scale = (OUT_SIDE * FILL) / max(obj.size)
    size = (max(1, round(obj.width * scale)), max(1, round(obj.height * scale)))
    obj = obj.resize(size, Image.LANCZOS)
    alpha = alpha.resize(size, Image.LANCZOS)

    canvas = Image.new("RGB", (OUT_SIDE, OUT_SIDE), BACKGROUND)
    x = (OUT_SIDE - size[0]) // 2
    y = (OUT_SIDE - size[1]) // 2

    # Ombre : la silhouette, floutée, décalée vers le bas, très légère.
    shadow = Image.new("L", (OUT_SIDE, OUT_SIDE), 0)
    shadow.paste(alpha.point(lambda v: int(v * 0.28)), (x, y + round(OUT_SIDE * 0.018)))
    shadow = shadow.filter(ImageFilter.GaussianBlur(OUT_SIDE * 0.02))
    canvas.paste(Image.new("RGB", canvas.size, (60, 60, 60)), (0, 0), shadow)

    canvas.paste(obj, (x, y), alpha)
    return canvas


def make_studio(img: Image.Image) -> bytes:
    """Photo studio en JPEG. L'image d'entrée a déjà passé le contrôle de visage."""
    out = compose(img, mask_of(img))
    buf = io.BytesIO()
    out.save(buf, "JPEG", quality=90)
    return buf.getvalue()
