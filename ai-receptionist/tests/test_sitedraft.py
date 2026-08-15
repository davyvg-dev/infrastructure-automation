"""sitedraft: extraction -> client-sites proposal config. Offline — the Claude call is never
made; `draft_copy` is the only thing that talks to the API and it is not exercised here."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from app import sitedraft, sitestyle
from app.sitedraft import DraftError

EXTRACTION = {
    "business_type": {"value": "loodgieter", "snippet": "Uw loodgieter in Zeist"},
    "phone": {"value": "030 - 123 45 67", "snippet": "Bel 030 - 123 45 67"},
    "region": {"value": "Zeist en omgeving", "snippet": "werkzaam in Zeist en omgeving"},
    "services": [
        {"name": "Lekkage", "category": "lekkage-reparatie", "snippet": "lekkages", "confidence": "high"},
    ],
    "hours": {
        "monday": {"open": "08:00", "close": "17:00", "snippet": "ma 8-17"},
        "saturday": {"open": "09:00", "close": "13:00", "snippet": "za 9-13"},
        "sunday": {"open": "", "close": "", "snippet": ""},
    },
}

DRAFT = {
    "vak": "Loodgieter",
    "plaats": "Zeist",
    "werkgebied": ["Zeist", "Utrecht", "De Bilt"],
    "diensten": [
        {"naam": "Lekkage verhelpen", "omschrijving": "Wij sporen de lekkage op en dichten hem."},
        {"naam": "Ontstoppen", "omschrijving": "Een verstopte afvoer weer laten doorstromen."},
        {"naam": "Sanitair", "omschrijving": "Kraan of toilet vervangen en netjes aansluiten."},
    ],
    "usps": ["Vaste prijs vooraf", "Eigen monteurs"],
    "spoed_beschikbaar": True,
    "spoed_tekst": "Bij een lekkage komen wij dezelfde dag langs.",
}


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("030 - 123 45 67", "+31 301234567"),
        ("06 12345678", "+31 612345678"),
        ("0031612345678", "+31 612345678"),
        ("+31 (0)10 1234567", "+31 101234567"),
    ],
)
def test_nl_phone_normalises_scraped_shapes(raw: str, expected: str) -> None:
    assert sitedraft.nl_phone(raw) == expected


def test_nl_phone_refuses_rather_than_guesses() -> None:
    with pytest.raises(DraftError):
        sitedraft.nl_phone("bel ons")


def test_openingstijden_maps_days_and_drops_the_uncited_ones() -> None:
    uren = sitedraft.openingstijden(EXTRACTION["hours"])
    assert uren == {"maandag": ["08:00", "17:00"], "zaterdag": ["09:00", "13:00"]}
    assert "zondag" not in uren  # empty times are absent, not rendered as 00:00


def test_build_config_is_a_proposal_and_invents_nothing() -> None:
    config = sitedraft.build_config("Jansen Loodgieters", EXTRACTION, DRAFT)
    assert config["modus"] == "preview"
    assert config["receptionist"] is False
    # The fields a proposal must not carry: legal identifiers, a domain, reviews, prices.
    assert set(config["bedrijf"]) == {"naam", "vak", "telefoon", "adres", "werkgebied"}
    assert "domein" not in config
    assert "reviews" not in config
    assert config["bedrijf"]["vak"] == "loodgieter"
    assert config["bedrijf"]["telefoon"] == "+31 301234567"
    assert config["bedrijf"]["adres"] == {"plaats": "Zeist"}


def test_build_config_caps_werkgebied_and_keeps_the_home_town_first() -> None:
    draft = {**DRAFT, "plaats": "Bunnik", "werkgebied": ["A", "B", "C", "D", "E"]}
    config = sitedraft.build_config("X BV", EXTRACTION, draft)
    assert config["bedrijf"]["werkgebied"] == ["Bunnik", "A", "B", "C", "D"]


def test_build_config_refuses_a_site_without_hours() -> None:
    with pytest.raises(DraftError, match="openingstijden"):
        sitedraft.build_config("X BV", {**EXTRACTION, "hours": {}}, DRAFT)


def _arrays(node: object):
    """Every array subschema in _SCHEMA, at any depth."""
    if isinstance(node, dict):
        if node.get("type") == "array":
            yield node
        for value in node.values():
            yield from _arrays(value)
    elif isinstance(node, list):
        for item in node:
            yield from _arrays(item)


def test_schema_carries_no_array_bounds_the_api_rejects() -> None:
    """Structured outputs 400 on `maxItems`, and on `minItems` above 1. Those bounds live in the
    prompt and in build_config instead; putting them back here breaks every scrape."""
    for array in _arrays(sitedraft._SCHEMA):
        assert "maxItems" not in array, array
        assert array.get("minItems", 0) in (0, 1), array


@pytest.mark.parametrize(
    ("veld", "waarde"),
    [("diensten", DRAFT["diensten"][:2]), ("usps", ["Eén pluspunt"])],
)
def test_build_config_refuses_a_draft_under_the_client_sites_floor(veld: str, waarde: list) -> None:
    with pytest.raises(DraftError, match=veld):
        sitedraft.build_config("X BV", EXTRACTION, {**DRAFT, veld: waarde})


def test_build_config_truncates_to_the_client_sites_ceilings() -> None:
    fat = {
        **DRAFT,
        "werkgebied": [f"Plaats{i}" for i in range(9)],
        "diensten": [{"naam": f"Dienst {i}", "omschrijving": "Wat wij doen."} for i in range(12)],
        "usps": [f"Pluspunt {i}" for i in range(7)],
    }
    config = sitedraft.build_config("X BV", EXTRACTION, fat)
    assert len(config["bedrijf"]["werkgebied"]) == 5
    assert len(config["diensten"]) == 8
    assert len(config["usps"]) == 4


def test_build_config_refuses_a_brand_colour_white_text_cannot_sit_on() -> None:
    with pytest.raises(DraftError, match="te licht"):
        sitedraft.build_config("X BV", EXTRACTION, DRAFT, kleur_primair="#ffe08a")


def test_slugify() -> None:
    assert sitedraft.slugify("Jansen Loodgieters B.V.") == "jansen-loodgieters-b-v"
    with pytest.raises(DraftError):
        sitedraft.slugify("!!!")


STIJL = {
    "letterontwerp": "industrieel",
    "schaal": "groot",
    "vorm": "scherp",
    "ritme": "ruim",
    "palet": "warm",
    "kleuring": "royaal",
    "foto": "randloos",
    "redenen": {axis: f"reden voor {axis}" for axis in
                ("letterontwerp", "schaal", "vorm", "ritme", "palet", "kleuring", "foto")},
}


def test_the_fixture_skin_is_one_the_site_could_actually_be_built_in() -> None:
    """Written after a hand-made fixture put `royaal` (a kleuring) on the ritme axis and the
    yaml round-tripped happily all the way to a build that Zod refused. A fixture that no
    build would accept lets every test below it pass while proving nothing."""
    sitestyle.check_stijl(STIJL)


def test_build_config_puts_the_skin_next_to_the_branding() -> None:
    config = sitedraft.build_config("X BV", EXTRACTION, DRAFT, stijl=sitestyle.keuzes(STIJL))
    assert list(config).index("stijl") == list(config).index("branding") + 1
    # The reasons are comments, never config: the Zod schema has no field for them.
    assert "redenen" not in config["stijl"]
    assert config["stijl"]["vorm"] == "scherp"


def test_build_config_without_a_skin_writes_no_key_at_all() -> None:
    """Absent `stijl:` is the pre-vocabulary look, which is a valid config. An empty or
    half-filled block would be a different thing entirely."""
    assert "stijl" not in sitedraft.build_config("X BV", EXTRACTION, DRAFT)


def test_dump_config_without_a_block_is_what_it_always_was() -> None:
    """The per-key dump exists only so `stijl:` can carry comments; it must not change a
    single byte of every config that has no such block."""
    config = sitedraft.build_config("Jansen Loodgieters", EXTRACTION, DRAFT)
    assert sitedraft.dump_config(config) == yaml.dump(
        config,
        Dumper=sitedraft._Dumper,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False,
    )


def test_write_config_keeps_the_reasons_as_comments_and_the_choices_as_data(
    tmp_path: Path,
) -> None:
    config = sitedraft.build_config("Jansen Loodgieters", EXTRACTION, DRAFT,
                                    stijl=sitestyle.keuzes(STIJL))
    path = sitedraft.write_config("jansen", config, tmp_path, sitestyle.as_yaml(STIJL))
    body = path.read_text(encoding="utf-8")

    # The block the founder reads and the config the build reads are the same seven values.
    assert yaml.safe_load(body) == config
    assert "# reden voor vorm" in body
    # A comment, so it survives the round trip above without becoming a config key.
    assert "redenen" not in yaml.safe_load(body)["stijl"]
    # In place, not appended: the skin sits with the branding, above the copy.
    assert body.index("stijl:") < body.index("diensten:")


def test_choose_stijl_composes_when_there_is_nothing_to_point_at(monkeypatch) -> None:
    """No reference is not a reason to fall back to the default look (TODO section R)."""
    calls = {}
    monkeypatch.setattr(
        sitestyle, "compose_stijl",
        lambda vak, naam, primair, accent: calls.update(
            vak=vak, naam=naam, primair=primair, accent=accent) or STIJL,
    )
    stijl = sitedraft.choose_stijl(
        "Dakwerken Bos", "dakdekker", [], kleur_primair="#1f3a5f", kleur_accent="#c2703d"
    )
    assert stijl is STIJL
    assert calls == {
        "vak": "dakdekker", "naam": "Dakwerken Bos",
        "primair": "#1f3a5f", "accent": "#c2703d",
    }


def test_choose_stijl_reads_the_reference_when_there_is_one(monkeypatch) -> None:
    monkeypatch.setattr(
        sitestyle, "compose_stijl",
        lambda *a: pytest.fail("composed while a reference site was measured"),
    )
    monkeypatch.setattr(sitestyle, "map_to_stijl", lambda facts, vak, naam: {**STIJL, "gezien": facts})
    stijl = sitedraft.choose_stijl(
        "Dakwerken Bos", "dakdekker", [{"bron": "https://zecc.nl"}],
        kleur_primair="#1f3a5f", kleur_accent="#c2703d",
    )
    assert stijl["gezien"] == [{"bron": "https://zecc.nl"}]


def test_vak_travels_to_the_skin_exactly_as_the_site_writes_it() -> None:
    """The composer argues from the trade, and a `Loodgieter` that reaches it capitalised is
    a different prompt from the `loodgieter` on the page."""
    config = sitedraft.build_config("X BV", EXTRACTION, DRAFT)
    assert sitedraft.vak_van(DRAFT) == config["bedrijf"]["vak"] == "loodgieter"


def _stub_scrape(monkeypatch, gedraaid: list[str]) -> None:
    """Everything main() does before the skin, minus the network and the API."""
    monkeypatch.setattr(sitedraft.extract, "gather_sources", lambda *a: {"site": "tekst"})
    monkeypatch.setattr(sitedraft.extract, "extract", lambda *a, **k: EXTRACTION)
    monkeypatch.setattr(
        sitedraft, "draft_copy", lambda *a: (gedraaid.append("copy"), DRAFT)[1]
    )


def test_a_bad_reference_stops_the_run_before_the_copy_call(monkeypatch, tmp_path, capsys):
    """Measuring is free and the copy call is not. A mistyped --voorbeeld must cost a second,
    not an Opus request -- the same rule the openingstijden check follows."""
    gedraaid: list[str] = []
    _stub_scrape(monkeypatch, gedraaid)
    monkeypatch.setattr(sitedraft.sitestyle, "measure", lambda url: (_ for _ in ()).throw(
        sitestyle.StyleError(f"{url} gaf geen leesbare pagina terug")
    ))

    code = sitedraft.main([
        "sitedraft", "Jansen Loodgieters", "--url", "https://x.nl",
        "--voorbeeld", "https://typo.invalid", "--out-dir", str(tmp_path),
    ])

    assert code == 1
    assert gedraaid == []  # nothing was paid for
    assert "geen leesbare pagina" in capsys.readouterr().err
    assert not list(tmp_path.iterdir())


def test_a_bad_brand_colour_stops_the_run_before_the_copy_call(monkeypatch, tmp_path, capsys):
    """It would otherwise come back twice over: once as a warning from the composer, which is
    handed the colour, and again as build_config's error saying the same thing."""
    gedraaid: list[str] = []
    _stub_scrape(monkeypatch, gedraaid)

    code = sitedraft.main([
        "sitedraft", "Jansen Loodgieters", "--url", "https://x.nl",
        "--kleur", "#ffe08a", "--out-dir", str(tmp_path),
    ])

    assert code == 1
    assert gedraaid == []
    assert "te licht" in capsys.readouterr().err
    assert not list(tmp_path.iterdir())


def test_a_failed_skin_still_writes_the_voorstel(monkeypatch, tmp_path, capsys) -> None:
    """The copy call is paid for by the time the skin is chosen. Throwing that away over a
    look would cost more than shipping the voorstel in the default one and saying so."""
    _stub_scrape(monkeypatch, [])
    monkeypatch.setattr(sitedraft, "choose_stijl", lambda *a, **k: (_ for _ in ()).throw(
        sitestyle.StyleError("Claude weigerde deze aanvraag")
    ))

    code = sitedraft.main([
        "sitedraft", "Jansen Loodgieters", "--url", "https://x.nl", "--out-dir", str(tmp_path),
    ])
    uit = capsys.readouterr()

    assert code == 0
    config = yaml.safe_load((tmp_path / "jansen-loodgieters" / "client.yaml").read_text())
    assert "stijl" not in config  # absent, not half-filled
    assert "stijl overgeslagen" in uit.err
    # And the founder is told how to give it one by hand, with this client's own arguments.
    assert "app.sitestyle --vak loodgieter" in uit.out


def test_main_takes_more_than_one_reference(monkeypatch, tmp_path) -> None:
    gezien: list[list[dict]] = []
    _stub_scrape(monkeypatch, [])
    monkeypatch.setattr(sitedraft.sitestyle, "measure", lambda url: {"bron": url})
    monkeypatch.setattr(sitedraft, "choose_stijl",
                        lambda naam, vak, v, **k: (gezien.append(v), STIJL)[1])

    code = sitedraft.main([
        "sitedraft", "Jansen Loodgieters", "--url", "https://x.nl",
        "--voorbeeld", "https://a.nl", "--voorbeeld", "https://b.nl",
        "--out-dir", str(tmp_path),
    ])

    assert code == 0
    assert gezien == [[{"bron": "https://a.nl"}, {"bron": "https://b.nl"}]]
    body = (tmp_path / "jansen-loodgieters" / "client.yaml").read_text()
    assert yaml.safe_load(body)["stijl"] == sitestyle.keuzes(STIJL)


def test_write_config_round_trips_and_never_overwrites(tmp_path: Path) -> None:
    config = sitedraft.build_config("Jansen Loodgieters", EXTRACTION, DRAFT)
    path = sitedraft.write_config("jansen", config, tmp_path)
    assert path == tmp_path / "jansen" / "client.yaml"

    body = path.read_text(encoding="utf-8")
    assert body.startswith("# VOORSTEL-config")
    assert yaml.safe_load(body) == config
    # Times and the phone number are quoted: unquoted "17:00" is 1020 under YAML 1.1, and the
    # site build must never receive a number where it expects text.
    assert "'17:00'" in body and "'08:00'" in body
    assert "'+31 301234567'" in body

    with pytest.raises(DraftError, match="bestaat al"):
        sitedraft.write_config("jansen", config, tmp_path)
