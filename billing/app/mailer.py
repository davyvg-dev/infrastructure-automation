"""Send the factuur to the client by email via Resend (stdlib urllib).

Resend is already the repo's transactional-email choice. The API key lives in
.env as RESEND_API_KEY; without it, sending fails loudly rather than silently
dropping an invoice. The 'from' address is the seller email (must be on a domain
you've verified in Resend, e.g. facturen@klantkraan.nl).
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

from . import settings

_ENDPOINT = "https://api.resend.com/emails"


def _api_key() -> str:
    key = os.getenv("RESEND_API_KEY", "").strip()
    if not key:
        raise SystemExit(
            "RESEND_API_KEY is not set — cannot email the factuur. Add it to "
            "billing/.env (Resend dashboard -> API keys), and verify the sender "
            "domain for BILLING_SELLER_EMAIL."
        )
    return key


def send_invoice(*, to: str, subject: str, html_body: str) -> str:
    """Email an invoice; returns the Resend message id. Raises on failure."""
    payload = {
        "from": settings.SELLER["email"],
        "to": [to],
        "subject": subject,
        "html": html_body,
    }
    req = urllib.request.Request(
        _ENDPOINT, data=json.dumps(payload).encode(), method="POST"
    )
    req.add_header("Authorization", f"Bearer {_api_key()}")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            out = json.loads(resp.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")
        raise RuntimeError(f"Resend POST -> HTTP {e.code}: {detail}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"Resend POST failed: {e.reason}") from e
    return out.get("id", "")
