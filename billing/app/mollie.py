"""Minimal Mollie REST client over stdlib urllib — no SDK dependency.

Covers exactly what the billing CLI needs: customers, a first payment (to
establish the recurring mandate), mandate lookup, and subscriptions. Mollie's API
is a plain Bearer-token JSON REST API, so this stays small and dependency-free.
Docs: https://docs.mollie.com/ (fetched via context7 /websites/mollie, 2026-07-14).
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any

from . import settings


class MollieError(RuntimeError):
    """A non-2xx response or transport failure from Mollie, with the body attached."""


class Mollie:
    def __init__(self, api_key: str | None = None, base: str | None = None) -> None:
        self._key = api_key or settings.api_key()
        self._base = (base or settings.MOLLIE_API_BASE).rstrip("/")

    def _request(self, method: str, path: str, body: dict | None = None) -> dict[str, Any]:
        url = f"{self._base}/{path.lstrip('/')}"
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header("Authorization", f"Bearer {self._key}")
        if data is not None:
            req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                raw = resp.read().decode()
        except urllib.error.HTTPError as e:
            detail = e.read().decode(errors="replace")
            raise MollieError(f"Mollie {method} {path} -> HTTP {e.code}: {detail}") from e
        except urllib.error.URLError as e:
            raise MollieError(f"Mollie {method} {path} failed: {e.reason}") from e
        return json.loads(raw) if raw else {}

    # -- customers -----------------------------------------------------------
    def create_customer(self, name: str, email: str, metadata: dict | None = None) -> dict:
        body: dict[str, Any] = {"name": name, "email": email}
        if metadata:
            body["metadata"] = metadata
        return self._request("POST", "/customers", body)

    def get_customer(self, customer_id: str) -> dict:
        return self._request("GET", f"/customers/{customer_id}")

    def get_payment(self, payment_id: str) -> dict:
        # Webhooks only send an id; always re-fetch to learn the real status/amount.
        return self._request("GET", f"/payments/{payment_id}")

    # -- first payment (establishes the mandate) -----------------------------
    def create_first_payment(
        self,
        *,
        customer_id: str,
        amount_value: str,
        description: str,
        redirect_url: str,
        webhook_url: str | None = None,
        currency: str = "EUR",
    ) -> dict:
        body: dict[str, Any] = {
            "amount": {"currency": currency, "value": amount_value},
            "customerId": customer_id,
            "sequenceType": "first",
            "description": description,
            "redirectUrl": redirect_url,
        }
        if webhook_url:
            body["webhookUrl"] = webhook_url
        return self._request("POST", "/payments", body)

    # -- mandates ------------------------------------------------------------
    def list_mandates(self, customer_id: str) -> list[dict]:
        out = self._request("GET", f"/customers/{customer_id}/mandates?limit=250")
        return out.get("_embedded", {}).get("mandates", [])

    def has_valid_mandate(self, customer_id: str) -> bool:
        return any(m.get("status") == "valid" for m in self.list_mandates(customer_id))

    # -- subscriptions -------------------------------------------------------
    def create_subscription(
        self,
        *,
        customer_id: str,
        amount_value: str,
        interval: str,
        description: str,
        start_date: str | None = None,
        times: int | None = None,
        webhook_url: str | None = None,
        currency: str = "EUR",
    ) -> dict:
        body: dict[str, Any] = {
            "amount": {"currency": currency, "value": amount_value},
            "interval": interval,
            "description": description,
        }
        if start_date:
            body["startDate"] = start_date
        if times:
            body["times"] = times
        if webhook_url:
            body["webhookUrl"] = webhook_url
        return self._request("POST", f"/customers/{customer_id}/subscriptions", body)

    def list_subscriptions(self, customer_id: str) -> list[dict]:
        out = self._request("GET", f"/customers/{customer_id}/subscriptions?limit=250")
        return out.get("_embedded", {}).get("subscriptions", [])
