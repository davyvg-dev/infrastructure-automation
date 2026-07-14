"""Offline billing selftests — no network, no API key required.

Verifies the money math and the request payloads the CLI builds, so a broken
price or rounding bug is caught before anything is sent to Mollie.
Run from billing/:  python -m app.selftest
"""
from __future__ import annotations

from decimal import Decimal

from . import invoice, plans, settings


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


def check_invoice() -> None:
    # net + BTW must sum back to the exact charged gross
    net, btw = invoice.split_gross(Decimal("361.79"))
    assert (net, btw) == (Decimal("299.00"), Decimal("62.79")), (net, btw)
    net2, btw2 = invoice.split_gross(Decimal("180.90"))
    assert net2 + btw2 == Decimal("180.90"), (net2, btw2)

    # render a factuur with a complete (test) seller; no counter side-effects
    saved = dict(settings.SELLER)
    settings.SELLER.update(
        name="Klantkraan", kvk="12345678", btw="NL001234567B01",
        address="Teststraat 1, 1000 AA Amsterdam", iban="NL00BANK0123456789",
    )
    try:
        inv = invoice.build(
            gross=Decimal("361.79"),
            buyer={"name": "Meijer B.V.", "email": "info@x.nl", "address": "Rotterdam"},
            description="Klantkraan Chat", period="juli 2026",
            payment_id="tr_test", assign_number=False,
        )
        rendered = invoice.render_html(inv)
        # explicit number wins (webhook reuses a pre-allocated number on retry)
        fixed = invoice.build(gross=Decimal("361.79"), buyer={"name": "x", "email": "x@x.nl"},
                              description="x", period="x", number="2026-0042")
        assert fixed.number == "2026-0042", fixed.number
    finally:
        settings.SELLER.clear()
        settings.SELLER.update(saved)
    for needle in ("Factuur", "BTW 21%", "Meijer B.V.", "12345678", "NL001234567B01"):
        assert needle in rendered, needle
    print("invoice : split 361.79->299.00+62.79, factuur renders required BTW fields  OK")


def check_invoice_guardrail() -> None:
    saved = dict(settings.SELLER)
    settings.SELLER.update(kvk="", btw="", address="")  # incomplete seller
    try:
        invoice.build(gross=Decimal("361.79"), buyer={"name": "x", "email": "x@x.nl"},
                      description="x", period="x", assign_number=False)
    except SystemExit:
        print("invoice : incomplete seller identity refused  OK")
        return
    finally:
        settings.SELLER.clear()
        settings.SELLER.update(saved)
    raise AssertionError("incomplete seller should raise SystemExit")


def main() -> None:
    check_plans()
    check_unknown_plan()
    check_invoice()
    check_invoice_guardrail()
    print("billing selftest: all OK")


if __name__ == "__main__":
    main()
