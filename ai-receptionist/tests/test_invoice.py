"""Factuur: numbering, the BTW split, rendering and the placeholder seller identity.

Offline by design — none of this needs Mollie. The webhook integration (which payments get
an invoice, and what the founder is told) lives in test_billing.py, where the Mollie harness
already is.
"""

from __future__ import annotations

import json
from datetime import date
from decimal import Decimal

import pytest

from app import invoice, mail_layout

_ON = date(2026, 7, 29)


def _build(payment_id: str = "tr_1", gross: str = "361.79", **kw) -> invoice.Invoice:
    return invoice.build(
        payment_id=payment_id,
        gross_eur=gross,
        buyer={"name": "Jan de Vries BV", "email": "jan@devries.nl"},
        description="Klantkraan Chat maandabonnement",
        on=kw.pop("on", _ON),
        **kw,
    )


# --- Numbering ---------------------------------------------------------------------------


def test_numbers_run_in_sequence_without_gaps(data_dir) -> None:
    """An auditor reads a gap as a deleted invoice, so the sequence has to be dense."""
    numbers = [invoice.number_for_payment(f"tr_{i}", _ON) for i in range(1, 6)]

    assert numbers == ["2026-0001", "2026-0002", "2026-0003", "2026-0004", "2026-0005"]


def test_the_same_payment_never_burns_a_second_number(data_dir) -> None:
    """Mollie retries webhooks. A retry must reuse the number, not skip one."""
    first = invoice.number_for_payment("tr_replay", _ON)
    again = invoice.number_for_payment("tr_replay", _ON)
    next_one = invoice.number_for_payment("tr_other", _ON)

    assert first == again == "2026-0001"
    assert next_one == "2026-0002", "the replay consumed nothing"


def test_the_sequence_restarts_per_year(data_dir) -> None:
    assert invoice.number_for_payment("tr_a", date(2026, 12, 31)) == "2026-0001"
    assert invoice.number_for_payment("tr_b", date(2027, 1, 1)) == "2027-0001"


def test_counter_and_payment_map_persist_together(data_dir) -> None:
    invoice.number_for_payment("tr_1", _ON)
    ledger = json.loads((data_dir / "invoices.json").read_text())

    assert ledger["counter"]["2026"] == 1
    assert ledger["payments"]["tr_1"] == "2026-0001"


def test_a_corrupt_ledger_does_not_crash_a_paid_webhook(data_dir) -> None:
    """Worst case we re-issue a number; refusing to invoice a paid customer is worse."""
    (data_dir / "invoices.json").write_text("{ not json")

    assert invoice.number_for_payment("tr_1", _ON) == "2026-0001"


# --- The money ---------------------------------------------------------------------------


@pytest.mark.parametrize("gross", ["361.79", "180.90", "1.21", "299.00", "0.03"])
def test_the_factuur_reconciles_to_the_charge(data_dir, gross: str) -> None:
    """Net + BTW must equal what the bank statement says, to the cent, always."""
    inv = _build(gross=gross)

    assert Decimal(inv.net) + Decimal(inv.btw) == Decimal(gross)
    assert inv.gross == gross


def test_the_standard_month_splits_the_way_the_site_advertises(data_dir) -> None:
    inv = _build(gross="361.79")

    assert (inv.net, inv.btw) == ("299.00", "62.79"), "the €299 we advertise, plus 21%"


def test_a_test_charge_still_produces_a_valid_split(data_dir) -> None:
    """The €1 test payment is a real charge and needs a real factuur."""
    inv = _build(gross="1.21")

    assert (inv.net, inv.btw, inv.gross) == ("1.00", "0.21", "1.21")


# --- The document ------------------------------------------------------------------------


def test_the_factuur_carries_what_the_belastingdienst_requires(data_dir) -> None:
    text = invoice.to_text(_build())

    for required in ("2026-0001", "29-07-2026", "KvK 90232135", "BTW", "€ 299,00", "€ 62,79"):
        assert required in text, f"a legal factuur states {required}"
    assert "T4 Software Consulting BV" in text, "the legal entity, not just the trade name"


def test_both_parts_are_rendered_from_one_description(data_dir) -> None:
    inv = _build()
    html, text = invoice.to_html(inv), invoice.to_text(inv)

    assert html.startswith("<!doctype html>") and "<table" in html
    for part in (html, text):
        assert "361,79" in part, "the total cannot differ between the parts"


def test_a_buyer_name_cannot_break_out_of_the_html(data_dir) -> None:
    """The name comes off a signup form, so it is attacker-controlled."""
    inv = invoice.build(
        payment_id="tr_1",
        gross_eur="361.79",
        buyer={"name": "<script>alert(1)</script> BV", "email": "x@y.nl"},
        description="Klantkraan Chat",
        on=_ON,
    )

    html = invoice.to_html(inv)
    assert "<script>alert(1)</script>" not in html and "&lt;script&gt;" in html


def test_the_amount_column_lines_up_in_the_text_part(data_dir) -> None:
    """A column of money that does not align on the decimal is unreadable in a text client."""
    rendered = mail_layout.to_text(
        [
            mail_layout.Totals(
                [("Subtotaal", "€ 299,00"), ("BTW 21%", "€ 62,79")], ("Totaal", "€ 361,79")
            )
        ]
    )
    amounts = [line.index("€") for line in rendered.splitlines() if "€" in line]

    assert len(set(amounts)) == 1, "every amount starts in the same column"


def test_the_archived_copy_is_what_was_mailed(data_dir) -> None:
    inv = _build()
    rendered = invoice.to_html(inv)

    path = invoice.archive(inv, rendered)

    assert (data_dir / "invoices" / "factuur-2026-0001.html").read_text() == rendered
    assert path.endswith("factuur-2026-0001.html")


# --- Seller identity ---------------------------------------------------------------------


def test_a_placeholder_identity_is_reported_not_hidden(data_dir, monkeypatch) -> None:
    monkeypatch.delenv("BILLING_SELLER_BTW", raising=False)
    monkeypatch.delenv("BILLING_SELLER_ADDRESS", raising=False)

    ok, missing = invoice.identity_complete()

    assert not ok
    assert missing == ["BILLING_SELLER_BTW", "BILLING_SELLER_ADDRESS"]
    assert invoice.PLACEHOLDER_BTW in invoice.to_text(_build()), "visibly provisional, not blank"


def test_real_details_need_no_code_change(data_dir, monkeypatch) -> None:
    monkeypatch.setenv("BILLING_SELLER_BTW", "NL863455324B01")
    monkeypatch.setenv("BILLING_SELLER_ADDRESS", "Voorbeeldstraat 1, 1234 AB Amsterdam")

    ok, missing = invoice.identity_complete()
    text = invoice.to_text(_build())

    assert ok and not missing
    assert "NL863455324B01" in text and "Voorbeeldstraat 1" in text
    assert invoice.PLACEHOLDER_BTW not in text


def test_an_iban_is_shown_only_when_set(data_dir, monkeypatch) -> None:
    monkeypatch.delenv("BILLING_SELLER_IBAN", raising=False)
    assert "IBAN" not in invoice.to_text(_build())

    monkeypatch.setenv("BILLING_SELLER_IBAN", "NL91ABNA0417164300")
    # Joined on whitespace: the plain-text part wraps at column 78, which can put the number
    # on the line after the "IBAN" label.
    assert "IBAN NL91ABNA0417164300" in " ".join(invoice.to_text(_build("tr_2")).split())


# --- Sending -----------------------------------------------------------------------------


def test_send_archives_and_mails_the_same_document(data_dir, monkeypatch) -> None:
    captured: list[dict] = []
    monkeypatch.setattr(
        invoice.mailer,
        "send",
        lambda to, subject, text, *, html=None, reply_to=None, idempotency_key=None: (
            bool(
                captured.append(
                    {"to": to, "subject": subject, "html": html, "key": idempotency_key}
                )
            )
            or True
        ),
    )

    result = invoice.send(
        payment_id="tr_1",
        gross_eur="361.79",
        to="jan@devries.nl",
        buyer_name="Jan de Vries BV",
        description="Klantkraan Chat maandabonnement",
        on=_ON,
    )

    (mail,) = captured
    assert result["sent"] and result["number"] == "2026-0001"
    assert mail["subject"] == "Factuur 2026-0001 van Klantkraan"
    assert mail["key"] == "factuur-tr_1", "a webhook replay must not send a second copy"
    assert (data_dir / "invoices" / "factuur-2026-0001.html").read_text() == mail["html"]


def test_send_never_raises_on_a_customer_without_an_address(data_dir) -> None:
    result = invoice.send(
        payment_id="tr_1", gross_eur="361.79", to="", buyer_name="X", description="Y"
    )

    assert result["sent"] is False and "no e-mail" in result["reason"]


def test_a_broken_renderer_is_reported_not_raised(data_dir, monkeypatch) -> None:
    """The money has already moved; a factuur bug must never fail a paid webhook."""
    monkeypatch.setattr(invoice, "to_html", lambda inv: 1 / 0)

    result = invoice.send(
        payment_id="tr_1", gross_eur="361.79", to="jan@devries.nl", buyer_name="X", description="Y"
    )

    assert result["sent"] is False and "ZeroDivisionError" in result["reason"]
