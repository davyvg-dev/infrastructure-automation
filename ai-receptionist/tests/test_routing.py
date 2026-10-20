"""Multi-tenant routing: Host subdomain / override / WhatsApp number -> client config. Offline."""

from __future__ import annotations

import textwrap

import pytest

from app.settings import (
    active_client,
    business,
    clear_slug,
    client_config_path,
    config_path,
    current_slug,
    resolve_slug,
    resolve_whatsapp_slug,
    use_slug,
)

_ACME = textwrap.dedent(
    """\
    business:
      name: "Acme Loodgieter"
      type: "loodgieter"
      timezone: "Europe/Amsterdam"
    whatsapp:
      number: "+31 6 1234 5678"
    """
)


@pytest.fixture
def acme(clients_dir):
    (clients_dir / "acme-loodgieter.yaml").write_text(_ACME, encoding="utf-8")
    return "acme-loodgieter"


def test_at_rest_no_active_client():
    assert current_slug() is None


def test_unknown_host_does_not_resolve(acme):
    assert resolve_slug("demo-1-2-3-4.sslip.io") is None


def test_path_traversal_slug_rejected(acme):
    assert client_config_path("../secrets") is None


def test_subdomain_resolves_to_slug(acme):
    assert resolve_slug("acme-loodgieter.klantkraan.nl") == "acme-loodgieter"


def test_whatsapp_number_routes_to_client(acme):
    # Twilio delivers the number as "whatsapp:+31612345678"; matching is format-insensitive.
    assert resolve_whatsapp_slug("whatsapp:+31612345678") == "acme-loodgieter"


def test_unknown_whatsapp_number_falls_back(acme):
    assert resolve_whatsapp_slug("whatsapp:+31699999999") is None


def test_active_slug_swaps_in_client_config_then_reverts(acme):
    default_name = business()["business"]["name"]
    token = use_slug(acme)
    try:
        assert active_client() == "acme-loodgieter"
        assert config_path().name == "acme-loodgieter.yaml"
        assert business()["business"]["name"] == "Acme Loodgieter"
    finally:
        clear_slug(token)
    # Once the request scope ends, everything falls back to the default tenant.
    assert current_slug() is None
    assert business()["business"]["name"] == default_name
