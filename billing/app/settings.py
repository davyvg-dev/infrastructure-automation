"""Billing settings: Mollie credentials + seller identity, all read from env.

Secrets live in `.env` (gitignored). NEVER hard-code the API key. Start with a
Mollie *test* key (`test_...`); switch to a live key only once Mollie has verified
the account. The key is read here so every module shares one source of truth.
"""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # billing/
DATA_DIR = ROOT / "data"

# Load .env for local runs. python-dotenv if present (matches the sibling apps),
# else a tiny stdlib fallback so billing runs with zero extra deps.
try:  # pragma: no cover - trivial
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
except ModuleNotFoundError:  # pragma: no cover - trivial
    _env = ROOT / ".env"
    if _env.exists():
        for _line in _env.read_text().splitlines():
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _k, _, _v = _line.partition("=")
                os.environ.setdefault(_k.strip(), _v.strip())

MOLLIE_API_BASE = os.getenv("MOLLIE_API_BASE", "https://api.mollie.com/v2")

# Where Mollie returns the client after checkout, and (optional) where it posts
# payment/subscription status webhooks. The webhook server arrives in the scaffold
# step; until then leave BILLING_WEBHOOK_BASE unset and webhooks are omitted.
REDIRECT_URL = os.getenv("BILLING_REDIRECT_URL", "https://klantkraan.nl/")
WEBHOOK_BASE = os.getenv("BILLING_WEBHOOK_BASE", "").rstrip("/")

# Seller identity — printed on invoices (scaffold step). Empty until the founder
# supplies the real KvK + BTW-id; the invoice generator will refuse to run with
# blanks so we never send a legally-incomplete factuur.
SELLER = {
    "name": os.getenv("BILLING_SELLER_NAME", "Klantkraan"),
    "kvk": os.getenv("BILLING_SELLER_KVK", ""),
    "btw": os.getenv("BILLING_SELLER_BTW", ""),
    "address": os.getenv("BILLING_SELLER_ADDRESS", ""),
    "email": os.getenv("BILLING_SELLER_EMAIL", "facturen@klantkraan.nl"),
    "iban": os.getenv("BILLING_SELLER_IBAN", ""),
}


def api_key() -> str:
    """The Mollie API key, or a clear error telling the founder where to put it."""
    key = os.getenv("MOLLIE_API_KEY", "").strip()
    if not key:
        raise SystemExit(
            "MOLLIE_API_KEY is not set. Copy billing/.env.example to billing/.env and "
            "fill in a Mollie test_ key (Mollie dashboard -> Developers -> API keys)."
        )
    return key


def is_live_key() -> bool:
    return os.getenv("MOLLIE_API_KEY", "").startswith("live_")
