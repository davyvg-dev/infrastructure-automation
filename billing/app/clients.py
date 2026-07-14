"""Resolve a paying client's name + email.

Reuses the ai-receptionist client config (`config/clients/<slug>.yaml`) so the
business details aren't re-entered, with explicit --name/--email overrides for
anything not on file. The paying customer IS the trade business that runs the
receptionist, so the same config is the right source.
"""
from __future__ import annotations

from . import settings

# ai-receptionist sits next to billing/ in the repo.
_CLIENTS_DIR = settings.ROOT.parent / "ai-receptionist" / "config" / "clients"


def from_config(slug: str) -> dict:
    path = _CLIENTS_DIR / f"{slug}.yaml"
    if not path.exists():
        return {}
    import yaml  # local import so plans/selftest stay import-light

    cfg = yaml.safe_load(path.read_text()) or {}
    biz = cfg.get("business", {})
    return {
        "name": biz.get("name"),
        "email": biz.get("email"),
        "phone": biz.get("phone"),
        "address": biz.get("address"),
    }


def by_customer_id(customer_id: str) -> str | None:
    """Reverse-lookup the client slug for a Mollie customer id (webhook path)."""
    from . import store

    for slug, rec in (store.all_records()).items():
        if rec.get("customer_id") == customer_id:
            return slug
    return None


def resolve(slug: str, name: str | None, email: str | None) -> dict:
    base = from_config(slug)
    resolved = {"name": name or base.get("name"), "email": email or base.get("email")}
    missing = [k for k, v in resolved.items() if not v]
    if missing:
        raise SystemExit(
            f"Missing {', '.join(missing)} for client '{slug}'. Add business.{{name,email}} "
            f"to ai-receptionist/config/clients/{slug}.yaml, or pass --name/--email."
        )
    return resolved
