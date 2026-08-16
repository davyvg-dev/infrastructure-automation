"""Offline tests for the enrichment heuristics. No network: every function under test is
pure, and the ones that are not are not tested here.

The expected values are not invented. They are the domains and addresses that the 23
prospects in the pipeline actually turned out to own, which is what makes this a
regression net rather than a restatement of the implementation.
"""

from __future__ import annotations

from scripts.enrich import (
    collapse_initials,
    domain_candidates,
    emails_in,
    headline,
    kvk_in,
    normalise_phone,
    phones_in,
    verify,
)

# name -> the domain the company really uses
REAL = {
    "AJ Dakwerken B.V.": "ajdakwerken.nl",
    "Duckdekker B.V.": "duckdekker.nl",
    "VDP Dakbedekking B.V.": "vdpdakbedekking.nl",
    "DV Dakdekkers B.V.": "dvdakdekkers.nl",
    "Herfst B.V.": "herfstbv.nl",
    "Lohmann Groep B.V.": "lohmannbv.nl",
    "L van der Wiel b.v.": "lvanderwielbv.nl",
    "T.I.B. Verkuylen bv": "tib-verkuylen.nl",
    "Smits Installaties B.V.": "smits-installaties.nl",
    "Technisch Bureau W. Janssen B.V.": "wjanssen.nl",
    "Visser & Van der Hell Loodgietersbedrijf B.V.": "visservanderhell.nl",
    "Andries Valkenburg Loodgieters B.V.": "valkenburgloodgieters.nl",
}


def test_candidate_generation_reaches_the_domains_these_companies_really_own():
    missed = [n for n, d in REAL.items() if d not in domain_candidates(n, "Leiden")]
    assert not missed, f"no candidate reached: {missed}"


def test_legal_form_is_stripped_without_eating_initials():
    """Splitting on word boundaries ate the B of T.I.B. and lost tib-verkuylen.nl."""
    assert "tib-verkuylen.nl" in domain_candidates("T.I.B. Verkuylen bv")


def test_collapse_initials_joins_only_runs_of_single_letters():
    assert collapse_initials(["t", "i", "b", "verkuylen"]) == ["tib", "verkuylen"]
    assert collapse_initials(["visser", "van", "der", "hell"]) == ["visser", "van", "der", "hell"]


def test_connectives_are_kept_because_they_are_part_of_the_name():
    assert "visservanderhell.nl" in domain_candidates("Visser & Van der Hell Loodgietersbedrijf")


def test_candidates_are_capped_so_one_company_is_not_dozens_of_requests():
    assert len(domain_candidates("Loodgieters- en Installatiebedrijf van der Herp B.V.")) <= 8


def test_kvk_number_on_the_page_is_proof():
    html = "<title>Iets anders</title><footer>KvK 12345678</footer>"
    assert verify(html, "12345678", "Willekeurig Bedrijf", rank=3) == "kvk-nummer"


def test_a_different_kvk_number_is_not_proof():
    html = "<title>Iets anders</title><footer>KvK 87654321</footer>"
    assert verify(html, "12345678", "Willekeurig Bedrijf", rank=3) is None


def test_name_in_the_title_verifies():
    assert verify("<title>AJ Dakwerken | Dakdekker</title>", "", "AJ Dakwerken B.V.", rank=0)


def test_name_only_in_the_body_does_not_verify():
    """The failure this guards: meijer.nl mentions "meijer" and is a different Meijer."""
    html = "<title>Meijer Transport</title><p>Loodgietersbedrijf Meijer was hier ooit</p>"
    assert verify(html, "12345678", "Loodgietersbedrijf Meijer B.V.", rank=4) is None


def test_a_bare_surname_is_not_accepted_on_a_wild_guess():
    html = "<title>Wiel Autobanden</title>"
    assert verify(html, "", "L van der Wiel b.v.", rank=0) is None


def test_role_address_on_the_company_domain_wins():
    html = "jan@duckdekker.nl info@duckdekker.nl someone@gmail.com"
    assert emails_in(html, "duckdekker.nl")[0] == "info@duckdekker.nl"


def test_own_domain_beats_a_role_address_elsewhere():
    html = "info@webbouwer.nl administratie@duckdekker.nl"
    assert emails_in(html, "duckdekker.nl")[0] == "administratie@duckdekker.nl"


def test_boilerplate_addresses_are_dropped():
    html = "info@example.com you@domain.com hello@sentry.io info@duckdekker.nl"
    assert emails_in(html, "duckdekker.nl") == ["info@duckdekker.nl"]


def test_headline_reads_title_and_h1_only():
    html = "<title>Herfst BV</title><body><h1>Dakwerk</h1><p>iets anders</p></body>"
    head = headline(html)
    assert "herfstbv" in head and "dakwerk" in head
    assert "ietsanders" not in head


# --- what the page publishes besides an address -------------------------------------
# Every trap below sat in a real Dutch footer alongside the number we wanted. The IBAN
# one is not hypothetical: it matched as a telephone number until it was excluded.

FOOTER = """
<footer>
  <p>Kerkstraat 12, 3011 AB Rotterdam</p>
  <p>Tel: <a href="tel:+31(0)10-412 57 00">010-412 57 00</a></p>
  <p>Mobiel: 06 12 34 56 78</p>
  <p>KvK-nummer: 24398765 &middot; BTW: NL812345678B01</p>
  <p>IBAN NL91 ABNA 0417 1643 00 &middot; &copy; 2026, sinds 1987</p>
</footer>
"""


def test_a_tel_link_is_believed_before_anything_in_the_body():
    assert phones_in(FOOTER)[0] == "0104125700"


def test_an_iban_is_not_a_telephone_number():
    assert "0417164300" not in phones_in(FOOTER)


def test_a_postcode_a_btw_id_and_a_year_are_not_telephone_numbers():
    for trap in ("3011 AB", "NL812345678B01", "1987", "24398765"):
        assert normalise_phone(trap) == ""


def test_every_written_form_of_one_number_normalises_to_the_same_string():
    forms = ["010-412 57 00", "(010) 4125700", "+31(0)10-412 57 00", "0031 10 412 5700"]
    assert {normalise_phone(f) for f in forms} == {"0104125700"}


def test_the_number_is_read_when_the_page_only_writes_it_out():
    html = "<div>Bel ons op 0182-334455. IBAN NL91ABNA0417164300.</div>"
    assert phones_in(html) == ["0182334455"]


def test_the_kvk_number_is_only_read_where_the_page_labels_it_one():
    assert kvk_in(FOOTER) == "24398765"
    assert kvk_in("<p>Kamer van Koophandel nr. 87654321</p>") == "87654321"
    assert kvk_in("<p>Postbus 12345678, sinds 1987</p>") == ""


def test_a_trade_named_after_its_city_is_never_proved_by_its_name():
    """Measured 2026-08-16: loodgieterutrecht.nl passed the title test for Loodgieter
    Utrecht B.V. and belongs to a different company. Trade plus place is not an identity."""
    html = "<title>Loodgieter Utrecht - 24/7 spoedservice</title>"
    assert verify(html, "", "Loodgieter Utrecht B.V.", rank=0) is None
    # ...but its own KVK number still settles it.
    page = "<title>Loodgieter Utrecht</title><footer>KvK 24398765</footer>"
    assert verify(page, "24398765", "Loodgieter Utrecht B.V.", rank=0) == "kvk-nummer"


def test_a_real_surname_beside_a_place_still_proves_the_name():
    html = "<title>Dak Garantie Amsterdam B.V.</title>"
    assert verify(html, "", "Dak Garantie Amsterdam B.V.", rank=0) == "naam"
