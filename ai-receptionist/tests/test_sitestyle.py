"""sitestyle: reference site -> client-sites skin vocabulary. Offline — nothing here fetches
a URL or calls the API. `gather_css` and `map_to_stijl` are the only two functions that talk
to the outside world, and both are stubbed or skipped."""

from __future__ import annotations

import pytest

from app import sitestyle
from app.sitestyle import StyleError

# One stylesheet exercising every shape the parser has to survive: a fluid clamp scale, a
# nested @media, an @font-face, a pill, a section band, and a rule inside @keyframes that
# must NOT be mistaken for a design declaration.
CSS = """
/* comment { with a brace } */
:root { --brand: #c2703d; }
html, body { background-color: #f5f1ea; font-size: 17px; color: #23201c; }
h1 { font-size: clamp(1.9rem, 4.5vw, 3.5rem); font-weight: 700; letter-spacing: -0.03em; }
h2 { font-size: 32px; font-weight: 700; }
p { font-size: 17px; }
.card { border-radius: 12px; padding: 24px; background: #fffdf9; }
.knop { border-radius: 9999px; max-width: 12rem; }
.band { padding: 80px 24px; background-color: #e8f0d8; }
.wrap { max-width: 1200px; }
.diensten { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); }
.sectie__body { grid-column: 6 / -1; }
figure img { border-radius: 0px; aspect-ratio: 3 / 2; }
@media (min-width: 768px) { .band { padding-block: 112px; } }
@font-face { font-family: 'Figtree'; src: url(/f.woff2) format('woff2'); }
@keyframes spin { from { font-size: 999px; } }
"""


def _measure(monkeypatch, css: str = CSS, ratios=None, google=None) -> dict:
    monkeypatch.setattr(
        sitestyle, "gather_css", lambda url: (css, list(ratios or []), list(google or []))
    )
    return sitestyle.measure("https://voorbeeld.nl")


# --- lengths ------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        # clamp() is resolved at the assumed viewport, not maximised: 4.5vw is 64.8px at
        # 1440px, but the browser renders the 3rem ceiling, and that is what we must report.
        ("clamp(1.9rem, 4.5vw, 3rem)", 48.0),
        ("clamp(2rem, 10vw, 8rem)", 128.0),
        ("4.5vw", 64.8),
        ("16px", 16.0),
        ("1.0625rem", 17.0),
        ("12pt", 16.0),
        ("0", None),
        ("auto", None),
    ],
)
def test_px_resolves_lengths_at_the_assumed_viewport(value: str, expected: float | None) -> None:
    assert sitestyle._px(value) == expected


def test_em_reads_tracking_in_em_and_converts_px() -> None:
    assert sitestyle._em("-0.03em") == -0.03
    assert sitestyle._em("-1px") == -0.0625
    assert sitestyle._em("normal") is None


# --- colour -------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("#FFF", "#ffffff"),
        ("#c2703d", "#c2703d"),
        ("rgb(34, 34, 34)", "#222222"),
        ("rgba(34 34 34 / 0.5)", "#222222"),
        ("transparent", None),
        ("var(--brand)", None),
    ],
)
def test_colour_normalises_to_hex(value: str, expected: str | None) -> None:
    assert sitestyle._colour(value) == expected


def test_hsl_separates_a_warm_off_white_from_a_neutral_one() -> None:
    # The whole point of the palet axis: these two are both "almost white" and differ only
    # in the few degrees of hue and few percent of saturation that hex comparison cannot see.
    zand = sitestyle.hsl("#f5f1ea")
    neutraal = sitestyle.hsl("#f7f7f7")
    assert zand["verzadiging"] > neutraal["verzadiging"]
    assert 30 <= zand["tint"] <= 60
    assert neutraal["verzadiging"] == 0


# --- typefaces ----------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("stack", "expected"),
    [
        ("'Figtree', system-ui, sans-serif", "Figtree"),
        ('"Instrument Serif", Georgia, serif', "Instrument Serif"),
        # A default stack is a decision not to choose, and must read as `systeem`.
        ("Arial, Helvetica, sans-serif", None),
        ("system-ui, -apple-system, sans-serif", None),
        # Next.js metric-matched fallbacks are not typefaces anybody picked.
        ("'Figtree Fallback', sans-serif", None),
        ("SFMono-Regular, Menlo, monospace", None),
        # Georgia first IS a choice, unlike Arial first.
        ("Georgia, serif", "Georgia"),
        ("var(--font-body), sans-serif", None),
    ],
)
def test_familie_picks_the_chosen_face_and_nothing_else(stack: str, expected: str | None) -> None:
    assert sitestyle._familie(stack) == expected


def test_familie_rejects_names_that_are_not_plainly_typefaces() -> None:
    # The one free-text field that reaches the model is whitelisted, not escaped.
    assert sitestyle._familie("'<script>alert(1)</script>', sans-serif") is None
    assert sitestyle._familie("'" + "x" * 80 + "', sans-serif") is None


# --- CSS structure ------------------------------------------------------------------------


def test_iter_rules_descends_into_media_and_skips_keyframes() -> None:
    selectors = [sel for sel, _ in sitestyle._iter_rules(CSS)]
    assert "@font-face" in selectors
    # The @media body yields its inner rule, not the @media prelude.
    assert any(s.strip() == ".band" for s in selectors)
    assert not any("keyframes" in s for s in selectors)
    # A 999px font-size inside @keyframes must never reach the type scale.
    assert not any(s.strip() == "from" for s in selectors)


def test_decls_splits_on_top_level_semicolons_only() -> None:
    body = "font-family: 'A', 'B'; background: rgba(0, 0, 0, 0.5); padding: 1rem"
    assert dict(sitestyle._decls(body)) == {
        "font-family": "'A', 'B'",
        "background": "rgba(0, 0, 0, 0.5)",
        "padding": "1rem",
    }


def test_ratio_reads_img_dimensions_and_refuses_nonsense() -> None:
    assert sitestyle._ratio("1500", "1000") == 1.5
    assert sitestyle._ratio("0", "10") is None
    assert sitestyle._ratio("", "10") is None


def test_google_fonts_reads_families_and_weights_from_the_url() -> None:
    href = (
        "https://fonts.googleapis.com/css2?family=Figtree:wght@400;700&family=Archivo&display=swap"
    )
    assert sitestyle._google_fonts(href) == [
        {"familie": "Figtree", "gewichten": [400, 700]},
        {"familie": "Archivo", "gewichten": []},
    ]


# --- the extractor collects no prose ------------------------------------------------------


def test_assets_collects_stylesheets_and_never_a_word_of_the_page() -> None:
    """The privacy guarantee is structural, so it gets a test rather than a comment.

    A reference's copy, photographs and logo are not ours. The parser is blind to text
    outside <style>, which is why there is no path from a reference's sentences to a
    client's site -- not a rule the model is asked to follow, but a thing it never sees.
    """
    assets = sitestyle._Assets()
    assets.feed(
        "<html><head><link rel='stylesheet' href='/a.css'>"
        "<style>body { color: red }</style></head>"
        "<body><h1>Wij zijn al 40 jaar de beste dakdekker van Utrecht</h1>"
        "<p>Bel ons op 030 123 45 67</p><img src='x.jpg' width='1500' height='1000'></body></html>"
    )
    assert assets.sheets == ["/a.css"]
    assert assets.ratios == [1.5]
    assert assets.styles == ["body { color: red }"]
    blob = " ".join(assets.sheets + assets.styles)
    for woord in ("dakdekker", "Utrecht", "40 jaar", "030"):
        assert woord not in blob


def test_measure_carries_no_text_from_the_page(monkeypatch) -> None:
    import json

    facts = _measure(monkeypatch)
    blob = json.dumps(facts, ensure_ascii=False)
    # Only the reference URL, typeface names, numbers and hex values may appear.
    assert "dakdekker" not in blob and "Utrecht" not in blob


# --- measuring ----------------------------------------------------------------------------


def test_measure_reads_the_type_scale(monkeypatch) -> None:
    facts = _measure(monkeypatch)
    # h1 is a clamp capped at 3.5rem; the ceiling, not the 4.5vw middle term.
    assert facts["kop1_px"]["max"] == 56.0
    assert facts["kop2_px"]["max"] == 32.0
    assert facts["tekst_px"]["mediaan"] == 17.0
    assert facts["kop_gewicht"] == [700]
    assert facts["kop_letterafstand_em"] == -0.03
    # The histogram is the fallback for compiled stylesheets, so it must hold every size.
    assert {s["px"] for s in facts["tekstgroottes_px"]} >= {56.0, 32.0, 17.0}
    assert all(s["px"] != 999.0 for s in facts["tekstgroottes_px"])


def test_measure_reads_shape_rhythm_and_colour(monkeypatch) -> None:
    facts = _measure(monkeypatch)
    assert facts["radius_px"]["mediaan"] == 6.0  # 12px card and 0px figure
    assert facts["pil_vormen"] == 1  # 9999px is a pill, not a 9999px corner
    # 24px card padding is not section rhythm; 80px and 112px are.
    assert facts["sectie_padding_px"]["mediaan"] == 96.0
    assert facts["sectie_padding_px"]["max"] == 112.0
    assert facts["pagina_achtergrond"]["hex"] == "#f5f1ea"
    assert facts["beeld_radius_px"]["max"] == 0.0
    assert facts["beeldverhoudingen"] == [{"verhouding": 1.5, "voorkomen": 1}]


def test_measure_reads_the_page_width_and_the_grid(monkeypatch) -> None:
    """The two measurements the composition axes are read off.

    `container_px` is the whole of the `maat` axis and nothing measured it before the axis
    existed; a max-width on a button is not a page container, so the band is bounded. The
    grid pair is tell #24 of the award study: award sites place items with unequal spans
    (median 2.5) and never repeat thirds, templates do the reverse.
    """
    facts = _measure(monkeypatch)
    assert facts["container_px"]["max"] == 1200.0
    assert facts["container_px"]["metingen"] == 1  # the 12rem button is not a container
    assert facts["drie_kolommen"] == 1
    assert facts["raster_spannen"] == 1


def test_measure_separates_declared_webfonts_from_used_ones(monkeypatch) -> None:
    facts = _measure(monkeypatch, google=[{"familie": "Archivo", "gewichten": [700]}])
    assert facts["webfonts"] == ["Archivo", "Figtree"]


def test_measure_refuses_a_page_with_no_css(monkeypatch) -> None:
    with pytest.raises(StyleError, match="geen CSS"):
        _measure(monkeypatch, css="   ")


def test_measure_all_survives_one_dead_reference(monkeypatch) -> None:
    def half(url: str) -> dict:
        if "dood" in url:
            raise StyleError("dood")
        return {"bron": url}

    monkeypatch.setattr(sitestyle, "measure", half)
    assert sitestyle.measure_all(["https://dood.nl", "https://ok.nl"]) == [
        {"bron": "https://ok.nl"}
    ]
    with pytest.raises(StyleError):
        sitestyle.measure_all(["https://dood.nl"])


# --- the vocabulary -----------------------------------------------------------------------


def test_vocabulaire_matches_the_resolver() -> None:
    """The reason this is parsed out of stijl.ts and indeling.ts instead of restated here.

    A value only sitestyle knows about would pass the API schema and then fail Zod at build
    time, on the founder's machine, after the voorstel was written.
    """
    axes = sitestyle.vocabulaire()
    assert set(axes) == {
        "letterontwerp",
        "schaal",
        "vorm",
        "ritme",
        "palet",
        "kleuring",
        "foto",
        "maat",
        "hero",
        "diensten",
    }
    assert axes["letterontwerp"] == ["systeem", "grotesk", "industrieel", "redactioneel"]
    assert axes["palet"] == ["warm", "koel", "neutraal", "zand"]
    # The axes T1-T4 added, and the ones the composer could not reach before T10.
    assert axes["maat"] == ["smal", "normaal", "breed"]
    assert axes["schaal"] == ["compact", "normaal", "groot", "royaal"]
    assert axes["hero"] == ["gesplitst", "gestapeld", "typografisch"]
    assert axes["diensten"] == ["kaarten", "lijst", "index"]
    assert all(values for values in axes.values())


def test_the_two_blocks_are_the_two_client_yaml_keys() -> None:
    """The skin and the composition are two blocks in client.yaml, so they are two here.
    Flattening them would put `hero:` under `stijl:`, which the Zod schema does not have."""
    blokken = sitestyle.per_blok()
    assert list(blokken) == ["stijl", "indeling"]
    assert list(blokken["indeling"]) == ["hero", "diensten"]
    # `weglaten` is the third key of the indeling block and is deliberately not chosen here:
    # which section a business can do without is a question about what it has to say.
    assert "weglaten" not in blokken["indeling"]
    assert list(sitestyle.vocabulaire()) == [
        axis for axes in blokken.values() for axis in axes
    ]


def test_kop_maxima_are_read_out_of_the_checked_schema() -> None:
    """Parsed rather than restated, same argument as the vocabulary: a ceiling only this
    module knew would let the composer offer a scale the drafted kop does not fit, and the
    founder would find out at build time. A rename in client.ts must fail here, not there."""
    per_schaal, standaard = sitestyle.kop_maxima()
    assert per_schaal == {"royaal": 55, "groot": 70}
    assert standaard == 90


def test_schema_offers_only_vocabulary_values() -> None:
    schema = sitestyle.schema()
    axes = sitestyle.vocabulaire()
    for axis, values in axes.items():
        assert schema["properties"][axis]["enum"] == values
    # Structured outputs require this on every object, and a missing one is a 400.
    assert schema["additionalProperties"] is False
    assert schema["properties"]["redenen"]["additionalProperties"] is False
    assert set(schema["required"]) == set(axes) | {"redenen"}


def test_schema_narrows_to_the_axes_it_is_given() -> None:
    """The withdrawn value has to leave the enum, not merely the prompt.

    A sentence in the system prompt is advice; an enum the API validates is a rule, and the
    run that ignores the advice ships a five-line headline on a real proposal.
    """
    axes = sitestyle.allowed("Installatietechniek Van der Veldenhuizen")
    schema = sitestyle.schema(axes)
    assert "groot" not in schema["properties"]["schaal"]["enum"]
    assert schema["properties"]["schaal"]["enum"] == axes["schaal"]


def test_check_stijl_refuses_a_value_outside_the_vocabulary() -> None:
    goed = {axis: values[0] for axis, values in sitestyle.vocabulaire().items()}
    assert sitestyle.check_stijl(dict(goed)) == goed
    with pytest.raises(StyleError, match="palet"):
        sitestyle.check_stijl({**goed, "palet": "pastel"})
    with pytest.raises(StyleError, match="schaal"):
        sitestyle.check_stijl({k: v for k, v in goed.items() if k != "schaal"})


def test_check_stijl_holds_the_narrowed_set_too() -> None:
    axes = sitestyle.allowed("Installatietechniek Van der Veldenhuizen")
    goed = {axis: values[0] for axis, values in axes.items()}
    assert sitestyle.check_stijl(dict(goed), axes) == goed
    with pytest.raises(StyleError, match="schaal"):
        sitestyle.check_stijl({**goed, "schaal": "groot"}, axes)


# --- the long-name rule -------------------------------------------------------------------


@pytest.mark.parametrize(
    ("naam", "groot_beschikbaar"),
    [
        ("Dakwerken Bos", True),
        ("Installatiebedrijf Van der Velden", True),  # 33 characters: four lines, measured
        ("Dakdekkersbedrijf Van der Meulen BV", False),  # 35: five lines, measured
        ("Installatietechniek Van der Veldenhuizen", False),
        ("   Installatietechniek Van der Veldenhuizen   ", False),  # padding is not a name
        (None, True),
    ],
)
def test_groot_is_withdrawn_for_a_long_company_name(naam, groot_beschikbaar: bool) -> None:
    """The H1 is "<naam>: vakwerk waar u op kunt rekenen." in a half-width column, so the
    company name is the one client field that can break the type scale. R1 capped `groot` at
    3.5rem to keep the call button on screen; this keeps the headline readable above it."""
    assert ("groot" in sitestyle.allowed(naam)["schaal"]) is groot_beschikbaar
    # Only schaal narrows -- a long name says nothing about paper colour or corners.
    for axis, values in sitestyle.allowed(naam).items():
        if axis != "schaal":
            assert values == sitestyle.vocabulaire()[axis]


def test_the_rule_reaches_the_reference_path_as_well() -> None:
    # A reference site with a 64px display face is no reason to set a 40-character name at
    # `groot`: it is the same page either way.
    assert "groot" not in sitestyle.candidates("Installatietechniek Van der Veldenhuizen")["schaal"]
    assert "groot" not in sitestyle.allowed("Installatietechniek Van der Veldenhuizen")["schaal"]


# --- the headline the schaal has to carry --------------------------------------------------


@pytest.mark.parametrize(
    ("kop", "over"),
    [
        # The real drafted koppen in the fleet run 43-48 characters and fit everything.
        ("Knippen en scheren aan de rand van Kralingen", ["compact", "normaal", "groot", "royaal"]),
        # 56: past what an 88px H1 carries, still fine one step down.
        ("K" * 56, ["compact", "normaal", "groot"]),
        ("K" * 71, ["compact", "normaal"]),
        # No scale carries 91 characters. Withdrawing the axis entirely would be a 400 from
        # the API for a sentence the founder can shorten, so the offer stands and the checked
        # schema says what is wrong in those words.
        ("K" * 91, ["compact", "normaal", "groot", "royaal"]),
        (None, ["compact", "normaal", "groot", "royaal"]),
    ],
)
def test_a_kop_withdraws_the_scales_it_does_not_fit(kop, over: list[str]) -> None:
    """ClientSchemaChecked caps the H1 per schaal (55 at `royaal`, 70 at `groot`, 90 below).
    The composer is handed the drafted kop, so it cannot offer a scale that config will be
    refused for -- which before T10 it could, because `royaal` was in the enum and nothing
    here had ever seen the headline."""
    assert sitestyle.allowed("Dakwerken Bos", kop)["schaal"] == over


def test_a_long_kop_and_a_long_name_narrow_the_same_axis_together() -> None:
    assert sitestyle.allowed("Installatietechniek Van der Veldenhuizen", "K" * 56)["schaal"] == [
        "compact",
        "normaal",
    ]


# --- the one cross-axis rule ---------------------------------------------------------------


def test_no_offer_ever_holds_both_royaal_and_gesplitst() -> None:
    """The rule the checked schema enforces, enforced one step earlier so the model cannot
    return the pair at all. 88px of H1 in the split hero's half-width column is about five
    characters a line -- the exact failure R4 measured.

    Swept over the whole expanded offer space rather than over a few names: every axis
    combination a shortlist can produce, for a spread of clients, plus both reference-path
    offers. A single reachable (royaal, gesplitst) is a voorstel that does not build.
    """
    import itertools

    aanbiedingen = [sitestyle.candidates(f"Voorbeeldbedrijf {n}") for n in range(60)]
    aanbiedingen += [sitestyle.candidates(n) for n in ("Bos", "Elektro Jansen", "Dakwerken Bos")]
    aanbiedingen += [
        sitestyle.zonder_botsing(sitestyle.allowed(), px)
        for px in (None, 24.0, 56.0, 71.9, 72.0, 130.0)
    ]
    gezien = set()
    for axes in aanbiedingen:
        for combinatie in itertools.product(*axes.values()):
            keuze = dict(zip(axes, combinatie, strict=True))
            assert not (keuze["schaal"] == "royaal" and keuze["hero"] == "gesplitst"), keuze
            gezien.add((keuze["schaal"], keuze["hero"]))
    # And the sweep really covered the interesting corners rather than passing by omission.
    assert ("royaal", "gestapeld") in gezien
    assert ("groot", "gesplitst") in gezien


def test_the_measured_display_size_decides_which_of_the_two_goes() -> None:
    """A reference is a measurement, so the measurement settles it: a site setting its
    display type at 72px or more (the midpoint between what `groot` can express at 56 and
    what `royaal` sets at 88) IS a big-headline site, and the arrangement that cannot hold
    one is what leaves. Below it the arrangement stands and `royaal` goes."""
    heel = sitestyle.zonder_botsing(sitestyle.allowed(), 130.0)
    assert "royaal" in heel["schaal"]
    assert heel["hero"] == ["gestapeld", "typografisch"]

    klein = sitestyle.zonder_botsing(sitestyle.allowed(), 48.0)
    assert "royaal" not in klein["schaal"]
    assert klein["hero"] == ["gesplitst", "gestapeld", "typografisch"]

    # No measurement is not a small measurement, but it is not evidence for 88px either, so
    # the split hero -- what the 60-site trade survey endorses -- is what stands.
    assert sitestyle.zonder_botsing(sitestyle.allowed(), None) == klein
    # Nothing else moves. A cross-axis rule that quietly narrowed the palet would be a bug
    # nobody would look for.
    for axis, values in sitestyle.allowed().items():
        if axis not in ("schaal", "hero"):
            assert heel[axis] == klein[axis] == values


def test_the_composer_still_reaches_royaal_on_some_clients() -> None:
    """The cheap way to satisfy the rule is to never offer `royaal`, which would re-open the
    gap T4 closed: display type on the sixteen award sites runs 96-320px and this factory
    topped out at 56. So it has to stay reachable without a reference, and it is -- on the
    clients whose hero shortlist came up without `gesplitst`."""
    namen = [f"Voorbeeldbedrijf {n}" for n in range(200)]
    met_royaal = [n for n in namen if "royaal" in sitestyle.candidates(n)["schaal"]]
    assert 20 <= len(met_royaal) <= 80, f"{len(met_royaal)} van 200"
    # And where it is offered, the split hero is not.
    for naam in met_royaal:
        assert "gesplitst" not in sitestyle.candidates(naam)["hero"]


def test_gemeten_display_follows_the_first_reference() -> None:
    """Same rule the prompt gives the model for references that disagree. `kop1_px` when the
    stylesheet names its headings, the top of the histogram when it does not -- a compiled
    stylesheet names .styles_heading__x7f2 and the named fields stay empty."""
    genoemd = {"kop1_px": {"max": 96.0}, "tekstgroottes_px": [{"px": 300.0, "voorkomen": 1}]}
    samengesteld = {"kop1_px": None, "tekstgroottes_px": [{"px": 88.0, "voorkomen": 2}]}
    assert sitestyle.gemeten_display([genoemd, samengesteld]) == 96.0
    assert sitestyle.gemeten_display([samengesteld]) == 88.0
    assert sitestyle.gemeten_display([{"kop1_px": None, "tekstgroottes_px": []}]) is None
    assert sitestyle.gemeten_display([]) is None


# --- composing without a reference --------------------------------------------------------


def test_candidates_are_stable_for_the_same_client() -> None:
    """Re-running for one client must rebuild one site.

    hash() is salted per process, so a seed built on it would redesign the page every time
    the founder fixed a typo in the yaml.
    """
    eerst = sitestyle.candidates("Dakwerken Bos")
    assert eerst == sitestyle.candidates("Dakwerken Bos")
    assert eerst == sitestyle.candidates("  DAKWERKEN-BOS!  ")
    # Pinned so a change to the seed shows up as a failing test rather than as every
    # existing client silently getting a new look on the next run.
    assert eerst["letterontwerp"] == ["industrieel", "redactioneel"]
    assert eerst["palet"] == ["zand", "warm"]


def test_candidates_differ_between_clients() -> None:
    """The reason the shortlist exists. sitedraft gives every prospect the same
    DEFAULT_PRIMARY until the founder overrides it, so without this six dakdekkers drafted
    in one week would arrive with identical inputs and leave with an identical skin."""
    namen = [
        "Dakwerken Bos",
        "Loodgietersbedrijf Kok",
        "Van Dijk Dakbedekking",
        "Installatiebedrijf Van Veen",
        "Elektro Jansen",
        "Slotenmakerij DRS",
    ]
    shortlists = [tuple(map(tuple, sitestyle.candidates(n).values())) for n in namen]
    assert len(set(shortlists)) == len(namen)


def test_candidates_never_offer_the_composer_systeem() -> None:
    """`systeem` is not a look, it is what a page looks like when nobody chose a typeface.
    A factory asked to compose one cannot answer "none" -- but measuring a reference really
    set in Arial still maps to it, which is a reading rather than a decision."""
    for naam in ("Dakwerken Bos", "Elektro Jansen", "Bouwbedrijf Hendriks"):
        assert "systeem" not in sitestyle.candidates(naam)["letterontwerp"]
    assert "systeem" in sitestyle.allowed("Dakwerken Bos")["letterontwerp"]


def test_candidates_stay_inside_the_vocabulary_and_keep_every_axis() -> None:
    axes = sitestyle.vocabulaire()
    for naam in ("Bos", "Installatietechniek Van der Veldenhuizen", "Elektro Jansen"):
        kandidaten = sitestyle.candidates(naam)
        assert set(kandidaten) == set(axes)
        for axis, values in kandidaten.items():
            assert 1 <= len(values) <= 2
            assert len(set(values)) == len(values)
            assert set(values) <= set(axes[axis])


def test_every_value_survives_somewhere_across_clients() -> None:
    """A rotation that stranded a value would quietly delete part of the vocabulary: the
    look would exist in stijl.ts, be reachable from a reference, and never be composed."""
    namen = [f"Voorbeeldbedrijf {n}" for n in range(40)]
    gezien: dict[str, set[str]] = {axis: set() for axis in sitestyle.vocabulaire()}
    for naam in namen:
        for axis, values in sitestyle.candidates(naam).items():
            gezien[axis].update(values)
    for axis, values in sitestyle.vocabulaire().items():
        verwacht = set(values) - {"systeem"} if axis == "letterontwerp" else set(values)
        assert gezien[axis] == verwacht


def test_check_hex_refuses_anything_that_is_not_a_colour() -> None:
    assert sitestyle._check_hex("#1F3A5F") == "#1f3a5f"
    for slecht in ("1f3a5f", "#1f3a5", "rood", "", None):
        with pytest.raises(StyleError, match="hex-waarde"):
            sitestyle._check_hex(slecht)


def test_compose_stijl_sends_the_vak_the_name_and_the_colours_in_hsl(monkeypatch) -> None:
    gezien = {}

    def vang(system: str, message: str, axes: dict) -> dict:
        gezien.update(system=system, message=message, axes=axes)
        return {axis: values[0] for axis, values in axes.items()}

    monkeypatch.setattr(sitestyle, "_choose", vang)
    stijl = sitestyle.compose_stijl("dakdekker", "Dakwerken Bos", "#1f3a5f", "#c2703d")

    assert gezien["axes"] == sitestyle.candidates("Dakwerken Bos")
    assert stijl["letterontwerp"] in sitestyle.candidates("Dakwerken Bos")["letterontwerp"]
    assert "dakdekker" in gezien["message"] and "Dakwerken Bos" in gezien["message"]
    # Hue and saturation, not just hex: whether a brand colour wants warm or cool paper is a
    # question about its hue, and the model should not do that arithmetic in its head.
    assert '"tint": 215' in gezien["message"]
    assert '"verzadiging": 51' in gezien["message"]
    # And the shortlist travels, so the reasons can name what was on the table.
    assert "Aangeboden waarden per as" in gezien["message"]
    # The composer is told the rules it is already prevented from breaking.
    assert str(sitestyle.NAAM_MAX_GROOT) in gezien["system"]
    assert "royaal" in gezien["system"] and "gesplitst" in gezien["system"]


def test_compose_stijl_sends_the_page_the_axes_have_to_fit(monkeypatch) -> None:
    """The kop and the number of diensten are what two of the new axes are chosen against:
    `schaal` has to set that headline, `diensten` has to arrange that many rows. Neither was
    ever in front of the composer before, and both are re-checked afterwards -- by the schema
    (the kop cap) and by tell-lint (`weesrij`, the card left alone on the last row)."""
    gezien = {}

    def vang(system: str, message: str, axes: dict) -> dict:
        gezien.update(message=message, axes=axes)
        return {axis: values[0] for axis, values in axes.items()}

    monkeypatch.setattr(sitestyle, "_choose", vang)
    kop = "Lekkage, verstopping of een ketel die het opgeeft"
    sitestyle.compose_stijl("loodgieter", "Dakwerken Bos", "#1f3a5f", None, kop, 6)
    assert kop in gezien["message"]
    assert f"({len(kop)} tekens)" in gezien["message"]
    assert "Aantal diensten dat de pagina toont: 6" in gezien["message"]
    # And the kop reached the offer, not just the prompt.
    assert gezien["axes"] == sitestyle.candidates("Dakwerken Bos", kop)


def test_map_to_stijl_offers_the_composition_axes_too(monkeypatch) -> None:
    """Both paths end in the same schema and the same yaml, so the reference path has to
    answer the same ten axes. Before T10 it answered seven and the other three defaulted to
    the arrangement every site the factory ever built already had."""
    gezien = {}

    def vang(system: str, message: str, axes: dict) -> dict:
        gezien.update(system=system, message=message, axes=axes)
        return {axis: values[0] for axis, values in axes.items()}

    monkeypatch.setattr(sitestyle, "_choose", vang)
    facts = [{"bron": "https://voorbeeld.nl", "kop1_px": {"max": 96.0}, "container_px": None}]
    stijl = sitestyle.map_to_stijl(facts, "dakdekker", "Dakwerken Bos")
    assert set(gezien["axes"]) == set(sitestyle.vocabulaire())
    assert set(stijl) == set(sitestyle.vocabulaire())
    # A 96px reference is a big-headline site, so the half-width hero came off the table.
    assert "gesplitst" not in gezien["axes"]["hero"]
    assert "royaal" in gezien["axes"]["schaal"]
    # The measurements the new axes are read off are named in the prompt, or the model is
    # being asked to choose `maat` from nothing.
    for veld in ("container_px", "drie_kolommen", "raster_spannen"):
        assert veld in gezien["system"]


def test_compose_stijl_refuses_a_bad_colour_before_paying_for_a_call(monkeypatch) -> None:
    monkeypatch.setattr(
        sitestyle, "_choose", lambda *a: pytest.fail("should not have called the API")
    )
    with pytest.raises(StyleError, match="hex-waarde"):
        sitestyle.compose_stijl("dakdekker", "Dakwerken Bos", "rood")


def test_main_without_a_reference_needs_a_vak_and_a_name(capsys) -> None:
    assert sitestyle.main(["app.sitestyle"]) == 1
    assert "--vak en --naam" in capsys.readouterr().err
    assert sitestyle.main(["app.sitestyle", "--vak", "dakdekker"]) == 1


def test_main_feiten_without_a_reference_prints_the_shortlists(capsys) -> None:
    """Same promise as `--feiten` on the reference path: see what the call will be judged on
    without paying for it. There are no measurements here, so the inputs are the answer."""
    import json

    code = sitestyle.main(
        ["app.sitestyle", "--vak", "dakdekker", "--naam", "Dakwerken Bos", "--kleur", "#1F3A5F"]
        + ["--feiten"]
    )
    assert code == 0
    feiten = json.loads(capsys.readouterr().out)
    assert feiten["vak"] == "dakdekker"
    assert feiten["naam_tekens"] == 13
    assert feiten["kleuren"]["primair"]["tint"] == 215
    assert "accent" not in feiten["kleuren"]
    assert feiten["kandidaten"] == sitestyle.candidates("Dakwerken Bos")


def test_as_yaml_writes_every_axis_with_its_reason() -> None:
    stijl = {axis: values[0] for axis, values in sitestyle.vocabulaire().items()}
    stijl["redenen"] = {"palet": "papier #f5f1ea heeft\n  12% verzadiging"}
    yaml = sitestyle.as_yaml(stijl)
    assert yaml.startswith("stijl:")
    assert "\nindeling:" in yaml
    for axis, value in stijl.items():
        if axis != "redenen":
            assert f"  {axis}: {value}" in yaml
    # A reason spanning lines would produce a yaml file that does not parse.
    assert "  # papier #f5f1ea heeft 12% verzadiging" in yaml
    # Two block headers, one line per axis, one comment.
    assert len(yaml.splitlines()) == 2 + len(sitestyle.vocabulaire()) + 1


def test_the_blocks_are_the_keys_the_config_carries() -> None:
    """sitedraft substitutes these for the yaml.dump of the same top-level key, so a key here
    that the config does not have is a block that silently never gets written."""
    import yaml as pyyaml

    stijl = {axis: values[0] for axis, values in sitestyle.vocabulaire().items()}
    stijl["redenen"] = {axis: f"reden voor {axis}" for axis in sitestyle.vocabulaire()}
    blokken = sitestyle.blokken(stijl)
    assert list(blokken) == ["stijl", "indeling"]
    assert pyyaml.safe_load("\n".join(blokken.values())) == sitestyle.keuzes(stijl)
    # The choices are data and the reasons are comments -- a client.yaml key the Zod schema
    # has never heard of is silently dropped on a good day and an error on a bad one.
    assert sitestyle.keuzes(stijl)["indeling"] == {"hero": "gesplitst", "diensten": "kaarten"}
    assert "redenen" not in sitestyle.keuzes(stijl)["stijl"]
    assert "# reden voor hero" in blokken["indeling"]


def test_as_yaml_wraps_a_long_reason_instead_of_running_off_the_screen() -> None:
    stijl = {axis: values[0] for axis, values in sitestyle.vocabulaire().items()}
    # The real model writes reasons this long; the Zecc run produced 180 characters.
    stijl["redenen"] = {"letterontwerp": "Displayfont Robust ICG met 20 voorkomens is een " * 5}
    yaml = sitestyle.as_yaml(stijl)
    comments = [line for line in yaml.splitlines() if line.startswith("  #")]
    assert len(comments) > 1
    assert all(len(line) <= 96 for line in yaml.splitlines())
    # Wrapping must not lose or duplicate a word.
    assert (
        " ".join(line.removeprefix("  # ") for line in comments)
        == stijl["redenen"]["letterontwerp"].strip()
    )
