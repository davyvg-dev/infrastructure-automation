"""Offline tests for the status page generator: pure logic only, no systemctl, no
sqlite, no network. Collectors are exercised elsewhere (smoke runs); here we pin the
RAG verdict, the billing ledger summary, and the renderers' honesty guarantees."""

import importlib.machinery
import importlib.util
from datetime import datetime

GEN_PATH = (
    __import__("pathlib").Path(__file__).resolve().parents[2] / "ops" / "status" / "generate.py"
)


def _load():
    loader = importlib.machinery.SourceFileLoader("status_generate", str(GEN_PATH))
    spec = importlib.util.spec_from_loader("status_generate", loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


gen = _load()
NOW = datetime(2026, 8, 12, 12, 0, 0)  # noqa: DTZ001 — generator compares local-naive


def _data(**sections):
    base = {
        "generated_at": NOW.isoformat(),
        "sections": {
            "health": {"has_systemd": False, "failed_units": [], "watchdog": None,
                       "last_run_hours": {}, "alerts_configured": None},
            "today": {"label": "x", "totals": {}, "clients": []},
            "deals": {"total": 1, "counts": {}, "active": [], "due_callbacks": []},
            "outreach": {"prospects": 0, "due_today": [], "closed": 0,
                         "sequence_complete": 0, "suppressed": 0},
            "content": {"verticals": []},
            "billing": {"events": 0, "counts": {}, "active_subs": 0, "mrr_eur": 0.0,
                        "last_webhook": None, "last_event": None},
            "timers": {"matrix": None},
        },
    }
    base["sections"].update(sections)
    return base


# -- rag ---------------------------------------------------------------------


def test_rag_green_when_nothing_is_wrong():
    assert gen.rag(_data(), NOW)["level"] == "green"


def test_rag_red_on_watchdog_down_or_failed_unit():
    down = _data(health={"has_systemd": True, "failed_units": [],
                         "watchdog": {"status": "down", "deep_status": "?", "age_min": 1},
                         "last_run_hours": {}, "alerts_configured": True})
    assert gen.rag(down, NOW)["level"] == "red"
    failed = _data(health={"has_systemd": True, "failed_units": ["growth-engine.service"],
                           "watchdog": {"status": "up", "deep_status": "answering",
                                        "age_min": 1},
                           "last_run_hours": {}, "alerts_configured": True})
    verdict = gen.rag(failed, NOW)
    assert verdict["level"] == "red"
    assert any("growth-engine.service" in r for r in verdict["reasons"])


def test_rag_red_when_up_but_not_answering():
    d = _data(health={"has_systemd": True, "failed_units": [],
                      "watchdog": {"status": "up", "deep_status": "silent", "age_min": 1},
                      "last_run_hours": {}, "alerts_configured": True})
    assert gen.rag(d, NOW)["level"] == "red"


def test_rag_amber_on_section_error_stale_daily_and_dark_alerts():
    err = _data(billing={"error": "boom"})
    assert gen.rag(err, NOW)["level"] == "amber"

    stale = _data(health={"has_systemd": True, "failed_units": [],
                          "watchdog": {"status": "up", "deep_status": "answering",
                                       "age_min": 5},
                          "last_run_hours": {"ai-receptionist-digest": 40.0},
                          "alerts_configured": True})
    verdict = gen.rag(stale, NOW)
    assert verdict["level"] == "amber"
    assert any("digest" in r for r in verdict["reasons"])

    dark = _data(health={"has_systemd": True, "failed_units": [],
                         "watchdog": {"status": "up", "deep_status": "answering",
                                      "age_min": 5},
                         "last_run_hours": {}, "alerts_configured": False})
    assert any("ALERTS UNCONFIGURED" in r for r in gen.rag(dark, NOW)["reasons"])


def test_rag_ignores_alert_config_on_hosts_without_systemd():
    # The Mac .env legitimately lacks owner keys; only the server must be able to page.
    mac = _data(health={"has_systemd": False, "failed_units": [], "watchdog": None,
                        "last_run_hours": {}, "alerts_configured": False})
    assert gen.rag(mac, NOW)["level"] == "green"


def test_rag_amber_on_old_snapshot_and_content_push_failure():
    d = _data()
    d["snapshot_at"] = "2026-08-01T00:00:00"
    verdict = gen.rag(d, NOW)
    assert verdict["level"] == "amber"
    assert any("snapshot" in r for r in verdict["reasons"])

    pushfail = _data(content={"verticals": [
        {"vertical": "trades", "total": 1, "counts": {"approved": 1}, "dry_run": 0,
         "push_errors": ["abc123 x: 401"]}]})
    assert any("push failed" in r for r in gen.rag(pushfail, NOW)["reasons"])


# -- billing summary ---------------------------------------------------------


def test_summarize_billing_counts_subs_and_mrr_and_closes_on_cancel():
    events = [
        {"at": "t1", "event": "checkout_created"},
        {"at": "t2", "event": "webhook", "action": "subscription_created",
         "customer_id": "cst_a", "monthly_eur": "299.00"},
        {"at": "t3", "event": "webhook", "action": "subscription_created",
         "customer_id": "cst_b", "monthly_eur": "499,00"},  # NL comma survives
        {"at": "t4", "event": "cancel", "customer_id": "cst_b"},
    ]
    s = gen.summarize_billing(events)
    assert s["active_subs"] == 1
    assert s["mrr_eur"] == 299.0
    assert s["last_webhook"] == "t3"
    assert s["last_event"] == "t4"
    assert s["counts"]["webhook"] == 2


def test_summarize_billing_empty_ledger():
    s = gen.summarize_billing([])
    assert s == {"events": 0, "counts": {}, "active_subs": 0, "mrr_eur": 0.0,
                 "last_webhook": None, "last_event": None}


# -- small parsers -----------------------------------------------------------


def test_alerts_configured_needs_a_complete_channel():
    assert gen._alerts_configured("OWNER_TELEGRAM_CHAT_ID=1\nNOTIFY_TELEGRAM_TOKEN=t\n")
    assert gen._alerts_configured("OWNER_EMAIL=a@b\nRESEND_API_KEY=k\n")
    assert not gen._alerts_configured("OWNER_TELEGRAM_CHAT_ID=1\n")  # chat id, no token
    assert not gen._alerts_configured("# OWNER_EMAIL=a@b\nRESEND_API_KEY=k\n")  # commented


def test_timestamp_age_hours_parses_systemctl_show_output():
    age = gen._timestamp_age_hours("Tue 2026-08-12 10:00:00 CEST", NOW)
    assert age == 2.0
    assert gen._timestamp_age_hours("", NOW) is None
    assert gen._timestamp_age_hours(None, NOW) is None
    assert gen._timestamp_age_hours("n/a", NOW) is None


# -- renderers ---------------------------------------------------------------


def test_html_renders_level_reasons_and_escapes():
    d = _data(today={"error": "<sqlite3.OperationalError>"})
    d["rag"] = gen.rag(d, NOW)
    page = gen.render_html(d)
    assert "AMBER" in page
    assert "&lt;sqlite3.OperationalError&gt;" in page  # escaped, not injected
    assert "<script" not in page.lower()  # the page promises: no JS, ever
    assert 'http-equiv="refresh"' in page
    assert 'name="robots" content="noindex"' in page


def test_empty_deals_points_at_the_push_command():
    d = _data(deals={"total": 0, "counts": {}, "active": [], "due_callbacks": []})
    d["rag"] = gen.rag(d, NOW)
    assert "kk status push" in gen.render_ansi(d)
    assert "kk status push" in gen.render_html(d)


def test_html_rich_fixture_renders_rows_kpis_and_deal_board():
    d = _data(
        today={"label": "2026-08-12", "totals": {
            "conversations": 7, "leads": 3, "bookings": 2, "cost_eur": 1.23},
            "clients": [
                {"client": "dhz", "conversations": 5, "leads": 2, "bookings": 1,
                 "cost_eur": 0.80},
                {"client": "<b>evil</b>", "conversations": 2, "leads": 1, "bookings": 1,
                 "cost_eur": 0.43}]},
        deals={"total": 3, "counts": {"lead": 1, "demo": 1, "signed": 1},
               "active": [
                   {"slug": "drs", "business": "DRS Riooltechniek", "status": "demo",
                    "next_action": "stuur offerte na", "next_call": "2026-08-12"}],
               "due_callbacks": [{"slug": "drs", "next_call": "2026-08-12"}]},
        billing={"events": 4, "counts": {"webhook": 2, "checkout_created": 2},
                 "active_subs": 2, "mrr_eur": 598.0,
                 "last_webhook": "2026-08-11T09:00:00", "last_event": "2026-08-11T09:00:00"},
    )
    d["rag"] = gen.rag(d, NOW)
    page = gen.render_html(d)
    assert "dhz" in page  # per-client row
    assert "&lt;b&gt;evil&lt;/b&gt;" in page and "<b>evil</b>" not in page
    assert "DRS Riooltechniek" in page  # deal row
    assert "stuur offerte na" in page
    assert ">7<" in page  # conversations KPI tile numeral
    assert "598,00" in page  # MRR, Dutch decimal comma


def test_html_error_section_becomes_fault_panel_and_page_survives():
    d = _data(billing={"error": "boom <tag>"})
    d["rag"] = gen.rag(d, NOW)
    page = gen.render_html(d)
    assert 'class="panel fault"' in page
    assert "boom &lt;tag&gt;" in page and "<tag>" not in page
    assert "Outreach" in page and "Systeem" in page  # the rest still renders


def test_html_timers_matrix_lands_in_a_pre_ledger():
    d = _data(timers={"matrix": "NEXT  LEFT  UNIT\n-     -     klantkraan-status.timer"})
    d["rag"] = gen.rag(d, NOW)
    page = gen.render_html(d)
    assert '<pre class="ledger">' in page
    assert "klantkraan-status.timer" in page


def test_write_assets_copies_when_present_and_skips_when_absent(tmp_path, monkeypatch):
    src = tmp_path / "srcfonts"
    src.mkdir()
    name = gen.FONT_FILES[0]
    (src / name).write_bytes(b"woff2!")
    monkeypatch.setattr(gen, "FONT_SRC", src)
    out = tmp_path / "www"
    out.mkdir()
    gen._write_assets(out)
    assert (out / "fonts" / name).read_bytes() == b"woff2!"
    (src / name).write_bytes(b"changed")  # already-present files are not overwritten
    gen._write_assets(out)
    assert (out / "fonts" / name).read_bytes() == b"woff2!"
    monkeypatch.setattr(gen, "FONT_SRC", tmp_path / "does-not-exist")
    out2 = tmp_path / "www2"
    out2.mkdir()
    gen._write_assets(out2)  # silent no-op
    assert not (out2 / "fonts").exists()


def test_snapshot_carries_only_mac_side_sections_and_its_age():
    d = _data()
    snap = gen.build_snapshot(d)
    assert set(snap) == {"generated_at", "deals", "outreach"}
