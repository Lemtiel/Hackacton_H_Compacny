"""Une session d'agent H sur un site boutique : relève les prix d'occasion d'un objet.

Même consigne pour tous les sites. Seule la règle de navigation (recherche autorisée ou non)
vient de la configuration du site.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Optional

from hai_agents import Client
from pydantic import BaseModel, Field

from agents.sites import SITES, start_url

AGENT = "h/web-surfer-flash"
MAX_SECONDS = 90  # au-delà, le site passe en « indisponible »
FORCE_ANSWER_AT = 70  # on demande à l'agent de conclure avec ce qu'il a
POLL_SECONDS = 2
TERMINAL = {"completed", "failed", "timed_out", "interrupted", "idle"}


class Offer(BaseModel):
    title: str = Field(description="Listing title as shown on the site")
    price_eur: float = Field(description="Selling price in euros")
    condition: Optional[str] = Field(default=None, description="Condition or grade if shown")
    url: Optional[str] = Field(default=None, description="Product page URL")


class Offers(BaseModel):
    offers: list[Offer]
    note: Optional[str] = Field(default=None, description="Short note: why few or no results, blocking, etc.")


def build_task(site_key: str, product: str) -> str:
    site = SITES[site_key]
    if site["search_allowed"]:
        nav = "You may use the site's own search bar."
    else:
        nav = (
            "Do NOT use the site's search bar or any search URL. Navigate only by clicking "
            "category menus, category pages and pagination links. Do not apply filters or sorting."
        )
    return (
        f"You are on {site['name']}, a French second-hand retailer. "
        f'Find used items for sale matching this product: "{product}". {nav} '
        "Collect up to 8 listings of the exact same model. Ignore items that are not this product: "
        "accessories made for it, cases and other models. "
        "For each listing give the title, the price in euros, the condition or grade if shown, and the product page URL. "
        "Do not log in, do not add to cart, do not fill any form. "
        "If a cookie consent banner appears, choose the option that refuses or continues without accepting; never accept cookies. "
        "If a captcha or an anti-bot page appears, stop immediately and report it in the note. "
        "If the site does not sell this kind of product or has no matching listing, return an empty list with a short note."
    )


@dataclass
class RunResult:
    site: str
    product: str
    status: str = "unknown"
    outcome: Optional[str] = None
    error_code: Optional[str] = None
    duration_s: float = 0.0
    steps: int = 0
    input_tokens: int = 0
    cached_tokens: int = 0
    output_tokens: int = 0
    forced_answer: bool = False
    cancelled: bool = False
    offers: list[Offer] = field(default_factory=list)
    note: Optional[str] = None
    session_id: Optional[str] = None
    agent_view_url: Optional[str] = None

    @property
    def available(self) -> bool:
        # h/web-surfer-flash est interactif : il finit en « idle » une fois sa réponse donnée.
        return not self.cancelled and self.status in ("completed", "idle")


def _usage(status) -> tuple[int, int, int]:
    i = c = o = 0
    for m in status.usage_per_model or []:
        i += m.input_tokens or 0
        c += m.cached_tokens or 0
        o += m.output_tokens or 0
    return i, c, o


def _last_image_url(events) -> Optional[str]:
    """Adresse de la dernière capture d'écran parmi des événements de session (ObservationEvent.image)."""
    found = None

    def walk(x):
        nonlocal found
        if isinstance(x, dict):
            if x.get("type") == "url" and str(x.get("source", "")).startswith("https://") and "image" in str(x.get("media_type") or "image"):
                found = x["source"]
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)

    for ev in events or []:
        try:
            walk(ev.model_dump(mode="json"))
        except Exception:
            continue
    return found


def run_site(client: Client, site_key: str, product: str, category: str, log=print, on_step=None, on_shot=None) -> RunResult:
    """on_step(dict) reçoit chaque changement d'étape, pour l'affichage progressif.
    on_shot(url) reçoit l'adresse de chaque nouvelle capture d'écran (mode démo). L'adresse n'est lisible
    qu'avec la clé API : elle ne doit jamais partir telle quelle vers le navigateur."""
    res = RunResult(site=site_key, product=product)
    t0 = time.monotonic()
    handle = client.start_session(
        agent=AGENT,
        messages=build_task(site_key, product),
        overrides={"agent.environments[kind=web].start_url": start_url(site_key, category)},
        answer_schema=Offers,
    )
    res.session_id = handle.id if hasattr(handle, "id") else None
    log(f"[{site_key}] session lancée")

    status = None
    last_steps = -1
    ev_index = 0
    last_shot = None
    while True:
        elapsed = time.monotonic() - t0
        status = handle.status()
        if on_shot:
            try:
                ch = handle.changes(from_index=ev_index, wait_for_seconds=0)
                if ch and ch.new_events:
                    ev_index = (ch.first_index if ch.first_index is not None else ev_index) + len(ch.new_events)
                    shot = _last_image_url(ch.new_events)
                    if shot and shot != last_shot:
                        last_shot = shot
                        on_shot(shot)
            except Exception:
                pass  # l'affichage démo ne doit jamais faire échouer la recherche
        if status.steps != last_steps:
            last_steps = status.steps
            log(f"[{site_key}] {elapsed:5.1f}s  {status.status}  étape {status.steps}")
            if on_step:
                on_step({"status": status.status, "steps": status.steps, "elapsed_s": round(elapsed, 1)})
        if status.status in TERMINAL:
            break
        if elapsed >= MAX_SECONDS and not res.cancelled:
            handle.cancel()
            res.cancelled = True
            log(f"[{site_key}] > {MAX_SECONDS}s : annulé, site indisponible")
        elif elapsed >= FORCE_ANSWER_AT and not res.forced_answer:
            handle.force_answer()
            res.forced_answer = True
            log(f"[{site_key}] {FORCE_ANSWER_AT}s : réponse forcée")
        time.sleep(POLL_SECONDS)

    res.duration_s = round(time.monotonic() - t0, 1)
    res.status = status.status
    res.outcome = status.outcome
    res.error_code = status.error_code
    res.steps = status.steps
    res.input_tokens, res.cached_tokens, res.output_tokens = _usage(status)

    session = handle.get()
    res.agent_view_url = getattr(session, "agent_view_url", None)
    answer = getattr(session, "latest_answer", None)
    if isinstance(answer, str):
        try:
            answer = Offers.model_validate_json(answer)
        except Exception:
            res.note = answer[:300]
            answer = None
    elif isinstance(answer, dict):
        try:
            answer = Offers.model_validate(answer)
        except Exception:
            res.note = str(answer)[:300]
            answer = None
    if isinstance(answer, Offers):
        res.offers = answer.offers
        res.note = answer.note
    if status.status == "idle":
        handle.cancel()  # libère le slot (3 sessions simultanées au plan gratuit)
    return res
