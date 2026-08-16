"""Offline tests for the KVK list machine.

The sieve is the whole point of this module. A false negative costs a prospect; a false
positive puts cold mail in front of an eenmanszaak, which is the one outcome here that is
not merely embarrassing but against the rules we sell on. So the BV gate gets the most
tests, and the fixture below is shaped like a real Basisprofiel response rather than like
the dataclass, because parsing that shape is where it would actually break.
"""

from __future__ import annotations

from scripts.sourcing import Candidate, Filters, from_profile, load_config, verdict

FILTERS = Filters(
    rechtsvorm_contains=["Besloten vennootschap", "Naamloze vennootschap"],
    skip_non_mailing=True,
    staff_min=2,
    staff_max=25,
    keep_unknown_staff=True,
)
LOODGIETER_SBI = ["4322", "4329"]


def profile(**over) -> dict:
    """A Basisprofiel response, in the shape the live API actually returns."""
    base = {
        "kvkNummer": "12345678",
        "statutaireNaam": "Loodgietersbedrijf Meijer B.V.",
        "indNonMailing": "Nee",
        "totaalWerkzamePersonen": 6,
        "sbiActiviteiten": [
            {"sbiCode": "43221", "sbiOmschrijving": "Loodgieterswerk", "indHoofdactiviteit": "Ja"}
        ],
        "_embedded": {
            "eigenaar": {"rechtsvorm": "Besloten vennootschap"},
            "hoofdvestiging": {
                "adressen": [
                    {
                        "type": "bezoekadres",
                        "straatnaam": "Dorpsstraat",
                        "huisnummer": 12,
                        "postcode": "3512AB",
                        "plaats": "Utrecht",
                    }
                ]
            },
        },
    }
    base.update(over)
    return base


def candidate() -> Candidate:
    return Candidate(kvk="12345678", name="Meijer", city="Utrecht", trade="loodgieter")


def test_a_real_bv_plumber_passes():
    c = from_profile(candidate(), profile())
    assert verdict(c, FILTERS, LOODGIETER_SBI) is None
    assert c.postcode == "3512AB"
    assert c.street == "Dorpsstraat 12"


def test_eenmanszaak_is_rejected():
    """The non-negotiable one: cold mail to an eenmanszaak without opt-in is not allowed."""
    c = from_profile(candidate(), profile(_embedded={"eigenaar": {"rechtsvorm": "Eenmanszaak"}}))
    assert "Eenmanszaak" in verdict(c, FILTERS, LOODGIETER_SBI)


def test_vof_is_rejected():
    c = from_profile(
        candidate(), profile(_embedded={"eigenaar": {"rechtsvorm": "Vennootschap onder firma"}})
    )
    assert verdict(c, FILTERS, LOODGIETER_SBI) is not None


def test_missing_rechtsvorm_is_rejected_rather_than_assumed():
    """A sparse profile must not fall through the gate. Absence of evidence that they are
    a BV is not evidence that they are."""
    c = from_profile(candidate(), profile(_embedded={}))
    assert verdict(c, FILTERS, LOODGIETER_SBI) is not None


def test_non_mailing_indicator_is_respected():
    c = from_profile(candidate(), profile(indNonMailing="Ja"))
    assert verdict(c, FILTERS, LOODGIETER_SBI) == "non-mailing indicator"


def test_non_mailing_can_be_switched_off_in_config():
    c = from_profile(candidate(), profile(indNonMailing="Ja"))
    relaxed = Filters(**{**FILTERS.__dict__, "skip_non_mailing": False})
    assert verdict(c, relaxed, LOODGIETER_SBI) is None


def test_a_namesake_in_the_wrong_trade_is_rejected():
    """Zoeken matches on name, so "Meijer Sanitair Groothandel" (wholesale, SBI 4674)
    comes back on a loodgieter query. SBI is what throws it out."""
    c = from_profile(
        candidate(),
        profile(sbiActiviteiten=[{"sbiCode": "46740", "sbiOmschrijving": "Groothandel"}]),
    )
    assert "outside the trade" in verdict(c, FILTERS, LOODGIETER_SBI)


def test_sbi_matches_on_prefix_so_subcodes_do_not_need_pinning():
    for code in ("4322", "43221", "43222"):
        c = from_profile(candidate(), profile(sbiActiviteiten=[{"sbiCode": code}]))
        assert verdict(c, FILTERS, LOODGIETER_SBI) is None, code


def test_solo_operator_is_out_of_band():
    c = from_profile(candidate(), profile(totaalWerkzamePersonen=1))
    assert verdict(c, FILTERS, LOODGIETER_SBI) == "1 staff"


def test_large_company_is_out_of_band():
    c = from_profile(candidate(), profile(totaalWerkzamePersonen=200))
    assert verdict(c, FILTERS, LOODGIETER_SBI) == "200 staff"


def test_unknown_headcount_is_kept_because_the_register_often_omits_it():
    c = from_profile(candidate(), profile(totaalWerkzamePersonen=None))
    assert verdict(c, FILTERS, LOODGIETER_SBI) is None

    strict = Filters(**{**FILTERS.__dict__, "keep_unknown_staff": False})
    assert verdict(c, strict, LOODGIETER_SBI) == "headcount unknown"


def test_slug_survives_a_url_and_drops_the_legal_form():
    cases = {
        "Loodgietersbedrijf Meijer B.V.": "loodgietersbedrijf-meijer",
        "A. Barendse & Zn. B.V.": "a-barendse-zn",
        "Dak & Klus  Utrecht  BV": "dak-klus-utrecht",
    }
    for name, expected in cases.items():
        assert Candidate(kvk="1", name=name, city="", trade="").slug == expected


def test_shipped_config_parses_and_covers_both_trades():
    cfg = load_config()
    assert {t.name for t in cfg.trades} == {"loodgieter", "dakdekker"}
    assert cfg.filters.rechtsvorm_contains  # the BV gate is not silently empty
    assert cfg.cities
