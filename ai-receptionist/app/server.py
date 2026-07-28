"""FastAPI server: serves the web chat widget and hosts the WhatsApp (Twilio) webhook.

All channels share the conversation store in `sessions.py`, so the web widget, Telegram
bot, and WhatsApp all talk to the same receptionist.
"""

from __future__ import annotations

import logging
import os
import re
import threading
import time
import uuid
from collections import deque
from pathlib import Path
from typing import Literal
from urllib.parse import urlsplit

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from pydantic import BaseModel, Field, ValidationError, model_validator
from starlette.concurrency import run_in_threadpool

from . import billing, notify, sessions
from .channels import whatsapp
from .settings import MissingSetting, business, clear_slug, ensure_dirs, resolve_slug, use_slug

log = logging.getLogger(__name__)

app = FastAPI(title="AI Receptionist demo")
_WEB = Path(__file__).resolve().parent.parent / "web"

# The marketing site (klantkraan.nl) posts signup leads here cross-origin; the chat widget
# never needs CORS (it runs same-origin inside an iframe), so this allowlist exists only
# for /api/lead. Pages deploy previews match via the regex so a deploy can be verified
# before DNS points at it.
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv(
        "CORS_ALLOW_ORIGINS", "https://klantkraan.nl,https://www.klantkraan.nl"
    ).split(","),
    allow_origin_regex=r"https://[a-z0-9-]+\.klantkraan-marketing\.pages\.dev",
    allow_methods=["GET", "POST"],
    allow_headers=["content-type"],
)

# Per-IP sliding-window rate limit on /chat: every request is a paid Claude call, so an
# open endpoint is a token-cost hole. Behind Caddy/nginx the client IP comes from
# X-Forwarded-For; bare-exposed, request.client is used (spoofable — deploy behind a proxy).
_RATE_LIMIT_PER_MINUTE = int(os.getenv("CHAT_RATE_LIMIT_PER_MINUTE", "20"))
_rate_lock = threading.Lock()
_hits: dict[str, deque[float]] = {}


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _activate(request: Request):
    """Bind the request to a client config (by Host subdomain, or an explicit override) for
    the rest of this call. Returns a token to pass to clear_slug() in a finally block."""
    override = request.query_params.get("client") or request.headers.get("x-client-slug")
    return use_slug(resolve_slug(request.headers.get("host"), override))


def _rate_ok(ip: str) -> bool:
    now = time.monotonic()
    with _rate_lock:
        if len(_hits) > 10_000:  # crude memory bound under address-spraying
            _hits.clear()
        window = _hits.setdefault(ip, deque())
        while window and now - window[0] > 60:
            window.popleft()
        if len(window) >= _RATE_LIMIT_PER_MINUTE:
            return False
        window.append(now)
        return True


class ChatIn(BaseModel):
    session_id: str | None = None
    message: str = Field(max_length=2000)


class ChatOut(BaseModel):
    session_id: str
    reply: str


@app.get("/")
def index() -> FileResponse:
    return FileResponse(_WEB / "index.html")


@app.get("/widget.js")
def widget_js() -> FileResponse:
    # The one-line loader a client pastes on their own site. It injects a floating bubble
    # and an iframe back to this origin, so the chat stays same-origin (no CORS, no key
    # leak). index.html is frameable by default (we never send X-Frame-Options); if a proxy
    # sits in front, don't let it add one. Short cache so updates still propagate.
    return FileResponse(
        _WEB / "widget.js",
        media_type="text/javascript",
        headers={"Cache-Control": "public, max-age=300"},
    )


@app.get("/health")
def health(request: Request) -> dict[str, str]:
    # Liveness probe for Caddy/Uptime Kuma; also confirms the (routed) config loads.
    token = _activate(request)
    try:
        return {"status": "ok", "business": business()["business"]["name"]}
    finally:
        clear_slug(token)


@app.get("/config")
def config(request: Request) -> dict[str, str]:
    token = _activate(request)
    try:
        cfg = business()
        return {
            "name": cfg["business"]["name"],
            "greeting": sessions.greeting(),
            # Drives the widget's UI chrome only; defaults to Dutch (the target market).
            "locale": cfg.get("locale", "nl"),
        }
    finally:
        clear_slug(token)


@app.post("/chat", response_model=ChatOut)
def chat(body: ChatIn, request: Request) -> ChatOut:
    # Sync def → FastAPI runs it in a threadpool, so the blocking Claude call is fine.
    api_key = os.getenv("CHAT_API_KEY")
    if api_key and request.headers.get("x-api-key") != api_key:
        raise HTTPException(status_code=401, detail="Invalid API key.")
    if not _rate_ok(_client_ip(request)):
        raise HTTPException(status_code=429, detail="Too many messages — try again in a minute.")
    session_id = body.session_id or uuid.uuid4().hex
    token = _activate(request)
    try:
        reply = sessions.respond("web", session_id, body.message)
    except Exception as exc:
        log.exception("chat turn failed (session %s)", session_id)
        notify.owner_exception(exc, context="chat")
        raise HTTPException(
            status_code=503, detail="The receptionist is temporarily unavailable."
        ) from exc
    finally:
        clear_slug(token)
    return ChatOut(session_id=session_id, reply=reply)


class LeadIn(BaseModel):
    naam: str = Field(min_length=1, max_length=200)
    bedrijf: str = Field(default="", max_length=200)
    telefoon: str = Field(default="", max_length=50)
    email: str = Field(default="", max_length=200)
    vak: str = Field(default="", max_length=100)
    plan: str = Field(default="", max_length=50)
    bericht: str = Field(default="", max_length=2000)
    # Honeypot: a hidden field humans never see. Bots that fill it get a silent 200.
    website: str = Field(default="", max_length=500)

    @model_validator(mode="after")
    def _reachable(self) -> LeadIn:
        if not (self.telefoon.strip() or self.email.strip()):
            raise ValueError("telefoon of email is verplicht")
        return self


# The signup form posts here two ways: fetch() with JSON (the enhanced path) and, whenever
# that script cannot run (blocked, stale HTML referencing a purged bundle, JS off), the
# browser submits the form natively as form-encoded. The native caller is *navigating*, so
# it must get 303 redirects — into Mollie on success, back to the form on bad input.
_SITE_ORIGIN_RE = re.compile(
    r"^https://(www\.)?klantkraan\.nl$|^https://[a-z0-9-]+\.klantkraan-marketing\.pages\.dev$"
)


async def _lead_payload(request: Request) -> tuple[dict[str, object], bool]:
    """Return (fields, native): JSON from the site's fetch path, form-encoded otherwise."""
    if (request.headers.get("content-type") or "").lower().startswith("application/json"):
        raw = await request.json()
        return (raw if isinstance(raw, dict) else {}), False
    form = await request.form()
    return {k: str(v) for k, v in form.items()}, True


def _form_urls(request: Request) -> tuple[str, str]:
    """(thanks_url, retry_url) for a native form poster, locale-aware via the Referer.
    Only allowlisted site origins are echoed back — anything else gets the defaults."""
    ref = urlsplit(request.headers.get("referer") or "")
    origin = f"{ref.scheme}://{ref.netloc}"
    path = ref.path or "/aanmelden/"
    if not _SITE_ORIGIN_RE.match(origin):
        origin, path = "https://klantkraan.nl", "/aanmelden/"
    prefix = next((p for p in ("/en", "/es") if path.startswith(p + "/")), "")
    return f"{origin}{prefix}/bedankt/", f"{origin}{path}?fout=1"


async def _signup(request: Request, buy: bool) -> Response:
    """Shared body of /api/lead and /api/checkout. The lead ALWAYS persists before any
    Mollie call, and Mollie trouble degrades to no checkout — never to a lost lead."""
    data, native = await _lead_payload(request)
    thanks, retry = _form_urls(request)

    def reject(status: int, detail: str) -> Response:
        if native:
            return RedirectResponse(retry, status_code=303)
        raise HTTPException(status_code=status, detail=detail)

    if not _rate_ok(f"lead:{_client_ip(request)}"):
        return reject(429, "Too many requests — try again in a minute.")
    if buy and native and (data.get("plan") or "chat") != "chat":
        buy = False  # the no-JS form posts every plan to /api/checkout; interest-only = lead
    try:
        body = CheckoutIn.model_validate(data) if buy else LeadIn.model_validate(data)
    except ValidationError:
        return reject(422, "Invalid input.")

    ok_body: dict[str, object] = {"ok": True, "checkout_url": None} if buy else {"ok": True}
    if body.website.strip():  # honeypot tripped: pretend success, store nothing
        return RedirectResponse(thanks, status_code=303) if native else JSONResponse(ok_body)

    lead = body.model_dump(exclude={"website"})
    if buy:
        lead["checkout"] = True  # persisted so paid/abandoned can be cross-checked
    result = await run_in_threadpool(notify.site_lead, lead)
    if not result["ok"]:
        # Neither disk nor Telegram took the lead — the caller must get its fallback.
        return reject(503, "Could not save your request.")
    if not buy:
        return RedirectResponse(thanks, status_code=303) if native else JSONResponse(ok_body)

    def create_checkout() -> str | None:
        try:
            customer_id = billing.create_customer(
                body.bedrijf.strip() or body.naam.strip(), body.email.strip()
            )
            return billing.create_first_payment(
                customer_id, billing.FIRST_MONTH_EUR, "Klantkraan Chat eerste maand", body.plan
            )
        except Exception as exc:
            # The founder already got the lead ping above; this extra one says "send the
            # payment link by hand" (python -m app.billing checkout).
            log.exception("checkout creation failed for lead %s", body.naam)
            notify.owner_exception(exc, context="checkout")
            return None

    checkout_url = await run_in_threadpool(create_checkout)
    if native:
        # No checkout URL means the lead is safe but Mollie is not reachable — the thanks
        # page's "wij nemen contact op" copy covers exactly that.
        return RedirectResponse(checkout_url or thanks, status_code=303)
    return JSONResponse({"ok": True, "checkout_url": checkout_url})


@app.post("/api/lead")
async def lead(request: Request) -> Response:
    return await _signup(request, buy=False)


class CheckoutIn(LeadIn):
    """The buy path. Mollie needs a billing email, and chat is the only plan that can be
    bought self-serve (compleet is sold by hand once voice ships)."""

    email: str = Field(min_length=3, max_length=200)
    plan: Literal["chat"] = "chat"

    @model_validator(mode="after")
    def _billing_email(self) -> CheckoutIn:
        if not self.email.strip():
            raise ValueError("email is verplicht voor betaling")
        return self


@app.post("/api/checkout")
async def checkout(request: Request) -> Response:
    """One POST from /aanmelden: save the lead, then send the buyer into Mollie checkout.
    JSON callers get {ok, checkout_url}; native form posts get a 303 straight to Mollie."""
    return await _signup(request, buy=True)


# Mollie payment ids only — anything else is not a webhook we ever asked for.
_MOLLIE_ID_RE = re.compile(r"^tr_[A-Za-z0-9]+$")


@app.post("/api/mollie/webhook")
async def mollie_webhook(request: Request) -> dict[str, bool]:
    """Mollie pings this with a form-encoded `id=tr_...`; billing fetches the payment back
    from the API for truth. Mollie retries on any non-200, so: handled or hopeless -> 200
    fast; Mollie itself unreachable (or the key not configured yet) -> 503 to keep the
    retry train alive until we can fetch truth."""
    if not _rate_ok(f"mollie:{_client_ip(request)}"):
        raise HTTPException(status_code=429, detail="Too many requests — try again in a minute.")
    form = await request.form()
    payment_id = str(form.get("id") or "")
    if not _MOLLIE_ID_RE.match(payment_id):
        raise HTTPException(status_code=400, detail="Invalid payment id.")
    try:
        result = await run_in_threadpool(billing.handle_webhook, payment_id)
        log.info("mollie webhook %s -> %s", payment_id, result.get("action"))
    except (billing.MollieUnreachable, MissingSetting) as exc:
        log.warning("mollie webhook %s deferred: %s", payment_id, exc)
        raise HTTPException(status_code=503, detail="Temporarily unavailable.") from exc
    except Exception as exc:
        # A broken payment stays broken — 200 so Mollie stops retrying, but the founder hears
        # about it (the event may involve real money).
        log.exception("mollie webhook %s failed", payment_id)
        notify.owner_exception(exc, context="mollie-webhook")
    return {"ok": True}


@app.post("/whatsapp")
async def whatsapp_webhook(request: Request) -> Response:
    form = await request.form()
    params = {k: str(v) for k, v in form.items()}
    signature = request.headers.get("X-Twilio-Signature")
    body, status = await run_in_threadpool(whatsapp.handle, str(request.url), signature, params)
    return Response(content=body, media_type="application/xml", status_code=status)


@app.exception_handler(Exception)
async def _report_unhandled(request: Request, exc: Exception) -> Response:
    # Backstop for any route that doesn't report on its own. HTTPException keeps its default
    # handler, so /chat's 503 (already reported above) never reaches here — no double-fire.
    notify.owner_exception(exc, context=request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error."})


def main() -> None:
    import uvicorn

    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO"),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    ensure_dirs()
    # Default binds localhost; set HOST=0.0.0.0 when serving behind Caddy on the VPS.
    uvicorn.run(
        "app.server:app",
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "8000")),
        reload=False,
    )


if __name__ == "__main__":
    main()
