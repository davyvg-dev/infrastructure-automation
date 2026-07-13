"""Config + env loading, with per-request multi-tenant routing.

One server process can host many clients. Each client is a `config/clients/<slug>.yaml`,
reached at its own origin (e.g. `https://<slug>.klantkraan.nl`). For each request the server
resolves the slug (Host subdomain, or an explicit `?client=` / `X-Client-Slug` override) and
sets it for the duration of that request; every `business()` call downstream then reads that
client's config — no signatures change.

With no active slug (Telegram, WhatsApp, the CLI, selftest, or an unknown host) it falls back
to the single config named by `BUSINESS_CONFIG`, so single-tenant setups and the live demo keep
working exactly as before.
"""

from __future__ import annotations

import os
import re
from contextvars import ContextVar, Token
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
CLIENTS_DIR = ROOT / os.getenv("CLIENTS_DIR", "config/clients")

# A slug is one DNS-label-ish token (lowercase, digits, hyphens). Anchored end-to-end so it
# can never contain a path separator or dot — no traversal out of CLIENTS_DIR.
_SLUG_RE = re.compile(r"[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$")

# The client active for the current request (None => the BUSINESS_CONFIG default).
_active_slug: ContextVar[str | None] = ContextVar("active_slug", default=None)

try:  # python-dotenv is optional; env vars can also be set directly.
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
except ModuleNotFoundError:
    pass


class MissingSetting(RuntimeError):
    pass


def env(name: str, required: bool = True, default: str | None = None) -> str | None:
    value = os.getenv(name, default)
    if required and not value:
        raise MissingSetting(f"{name} is not set. Copy .env.example to .env and fill it in.")
    return value


# --- multi-tenant routing ---------------------------------------------------------------


def default_config_path() -> Path:
    return ROOT / os.getenv("BUSINESS_CONFIG", "config/business.yaml")


def client_config_path(slug: str | None) -> Path | None:
    """The config path for a slug if the slug is valid AND that file exists, else None."""
    if not slug or not _SLUG_RE.match(slug):
        return None
    path = CLIENTS_DIR / f"{slug}.yaml"
    return path if path.exists() else None


def resolve_slug(host: str | None, override: str | None = None) -> str | None:
    """Pick a client slug for a request: an explicit override (query/header) wins, else the
    first label of the Host header. Returns the slug only if a matching config exists."""
    if client_config_path(override):
        return override
    if host:
        label = host.split(":", 1)[0].split(".", 1)[0].strip().lower()
        if client_config_path(label):
            return label
    return None


def use_slug(slug: str | None) -> Token:
    """Set the active client for the current context; returns a token to reset with."""
    return _active_slug.set(slug)


def clear_slug(token: Token) -> None:
    _active_slug.reset(token)


def current_slug() -> str | None:
    return _active_slug.get()


def config_path() -> Path:
    """The config file backing the current request — the active client, or the default."""
    return client_config_path(_active_slug.get()) or default_config_path()


def active_client() -> str:
    """Stable label for the active config — the slug, or the default config's stem. Used to
    namespace per-tenant state (the session store, the sim bookings file)."""
    return _active_slug.get() or default_config_path().stem


@lru_cache(maxsize=64)
def _load(path_str: str) -> dict[str, Any]:
    with Path(path_str).open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def business() -> dict[str, Any]:
    return _load(str(config_path()))


def ensure_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
