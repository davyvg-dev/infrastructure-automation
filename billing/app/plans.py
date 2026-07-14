"""Subscription plans and BTW math.

Prices are quoted EX BTW (this is B2B). Mollie charges the customer the
21%-inclusive GROSS amount that actually leaves their account; the invoice
(scaffold step) breaks the gross back out into net + BTW. All money is Decimal —
never float — and rounds half-up to cents.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

BTW_RATE = Decimal("0.21")  # NL standard rate
CENTS = Decimal("0.01")


def _cents(amount: Decimal) -> Decimal:
    return amount.quantize(CENTS, rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class Plan:
    key: str
    label: str
    net: Decimal  # monthly price ex BTW, EUR
    interval: str = "1 month"

    @property
    def btw(self) -> Decimal:
        return _cents(self.net * BTW_RATE)

    @property
    def gross(self) -> Decimal:
        return _cents(self.net + self.btw)

    def gross_value(self) -> str:
        """Mollie wants amount.value as a 2-decimal string, e.g. '361.79'."""
        return f"{self.gross:.2f}"


PLANS: dict[str, Plan] = {
    "chat": Plan("chat", "Klantkraan Chat", Decimal("299")),
    "compleet": Plan("compleet", "Klantkraan Compleet", Decimal("499")),
}


def plan(key: str) -> Plan:
    try:
        return PLANS[key]
    except KeyError:
        raise SystemExit(f"Unknown plan '{key}'. Choose one of: {', '.join(PLANS)}.")


def discounted(amount: Decimal, fraction: Decimal) -> Decimal:
    """fraction=Decimal('0.5') => half price. Rounds to cents."""
    return _cents(amount * fraction)
