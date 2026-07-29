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
