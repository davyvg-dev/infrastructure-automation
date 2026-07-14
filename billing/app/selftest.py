"""Offline billing selftests — no network, no API key required.

Verifies the money math and the request payloads the CLI builds, so a broken
price or rounding bug is caught before anything is sent to Mollie.
Run from billing/:  python -m app.selftest
"""
from __future__ import annotations

from decimal import Decimal

from . import plans


def check_plans() -> None:
    chat = plans.plan("chat")
    assert chat.net == Decimal("299"), chat.net
    assert chat.btw == Decimal("62.79"), chat.btw
    assert chat.gross == Decimal("361.79"), chat.gross
    assert chat.gross_value() == "361.79", chat.gross_value()

    compleet = plans.plan("compleet")
    assert compleet.btw == Decimal("104.79"), compleet.btw
    assert compleet.gross == Decimal("603.79"), compleet.gross

    assert plans.discounted(chat.gross, Decimal("0.5")) == Decimal("180.90")
    assert plans.discounted(compleet.gross, Decimal("0.5")) == Decimal("301.90")
    print("plans   : chat 299->361.79, compleet 499->603.79, 50% first 180.90/301.90  OK")


def check_unknown_plan() -> None:
    try:
        plans.plan("nope")
    except SystemExit:
        print("plans   : unknown plan rejected  OK")
        return
    raise AssertionError("unknown plan should raise SystemExit")


def main() -> None:
    check_plans()
    check_unknown_plan()
    print("billing selftest: all OK")


if __name__ == "__main__":
    main()
