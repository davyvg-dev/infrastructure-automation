"""Offline tests for the kk dispatcher: planner logic only, nothing executes."""

import importlib.machinery
import importlib.util
import sys
from pathlib import Path

import pytest

KK_PATH = Path(__file__).resolve().parent.parent / "kk"
ROOT = Path("/fake/repo")
AIR = ROOT / "ai-receptionist"
AIR_PY = str(AIR / ".venv" / "bin" / "python")


def _load_kk():
    loader = importlib.machinery.SourceFileLoader("kk", str(KK_PATH))
    spec = importlib.util.spec_from_loader("kk", loader)
    mod = importlib.util.module_from_spec(spec)
    # dataclass resolves string annotations via sys.modules — register before exec
    sys.modules["kk"] = mod
    loader.exec_module(mod)
    return mod


kk = _load_kk()


def argvs(verb, args=()):
    return [s.argv for s in kk.plan(verb, list(args), ROOT)]


# -- board / deal ------------------------------------------------------------


def test_board_runs_both_boards_from_air():
    steps = kk.plan("board", [], ROOT)
    assert [s.cwd for s in steps] == [AIR, AIR]
    assert steps[0].argv == [AIR_PY, "-m", "app.pipeline", "board"]
    assert steps[1].argv == [AIR_PY, "-m", "scripts.sequence", "board"]


def test_deal_passthrough_and_default():
    assert argvs("deal", ["advance", "acme", "demo"]) == [
        [AIR_PY, "-m", "app.pipeline", "advance", "acme", "demo"]
    ]
    assert argvs("deal") == [[AIR_PY, "-m", "app.pipeline", "board"]]


# -- outreach cap ------------------------------------------------------------


def test_outreach_send_injects_cap_when_absent():
    (argv,) = argvs("outreach", ["send"])
    assert argv == [AIR_PY, "-m", "scripts.outreach_send", "--send", "--limit", "6"]


def test_outreach_send_keeps_lower_limit():
    (argv,) = argvs("outreach", ["send", "--limit", "3"])
    assert argv.count("--limit") == 1
    assert argv[argv.index("--limit") + 1] == "3"


def test_outreach_send_rejects_limit_above_cap():
    with pytest.raises(kk.UsageError):
        kk.plan("outreach", ["send", "--limit", "7"], ROOT)
    with pytest.raises(kk.UsageError):
        kk.plan("outreach", ["send", "--limit=25"], ROOT)


def test_outreach_send_rejects_malformed_limit():
    with pytest.raises(kk.UsageError):
        kk.plan("outreach", ["send", "--limit"], ROOT)
    with pytest.raises(kk.UsageError):
        kk.plan("outreach", ["send", "--limit", "six"], ROOT)


def test_outreach_send_equals_form_within_cap_passes():
    (argv,) = argvs("outreach", ["send", "--limit=2", "--touch", "1"])
    assert "--limit=2" in argv and "--touch" in argv


def test_outreach_default_and_stop():
    assert argvs("outreach") == [[AIR_PY, "-m", "scripts.sequence", "board"]]
    assert argvs("outreach", ["stop", "acme", "--bounced"]) == [
        [AIR_PY, "-m", "scripts.sequence", "stop", "acme", "--bounced"]
    ]


def test_outreach_dry_has_no_send_flag():
    (argv,) = argvs("outreach", ["dry"])
    assert "--send" not in argv


# -- evals / billing ---------------------------------------------------------


def test_evals_default_runs_all():
    assert argvs("evals") == [[AIR_PY, "-m", "app.evals", "run", "all"]]


def test_evals_pack_and_list():
    assert argvs("evals", ["hallucination"]) == [
        [AIR_PY, "-m", "app.evals", "run", "hallucination"]
    ]
    assert argvs("evals", ["list"]) == [[AIR_PY, "-m", "app.evals"]]


def test_billing_default_status():
    assert argvs("billing") == [[AIR_PY, "-m", "app.billing", "status"]]


# -- cursus ------------------------------------------------------------------


def test_cursus_default_board():
    assert argvs("cursus") == [[AIR_PY, "-m", "app.cursus", "board"]]


def test_cursus_passthrough_keeps_flags():
    assert argvs("cursus", ["send", "--dry"]) == [
        [AIR_PY, "-m", "app.cursus", "send", "--dry"]
    ]
    assert argvs("cursus", ["stop", "jan@bedrijf.nl", "--bounced"]) == [
        [AIR_PY, "-m", "app.cursus", "stop", "jan@bedrijf.nl", "--bounced"]
    ]


def test_cursus_runs_from_the_app_dir():
    (step,) = kk.plan("cursus", [], ROOT)
    assert step.cwd == AIR


def test_nieuwsbrief_board_runs_on_the_server_as_app_user():
    (argv,) = argvs("nieuwsbrief")
    assert argv[0] == "ssh" and argv[1].startswith("root@")
    assert "runuser -u klantkraan" in argv[2] and "app.nieuwsbrief board" in argv[2]


def test_nieuwsbrief_send_picks_newest_edition_and_keeps_dry():
    (argv,) = argvs("nieuwsbrief", ["send", "--dry"])
    assert "ls -t" in argv[2] and "growth-engine/data/trades/newsletters" in argv[2]
    assert 'send --file "$f" --dry' in argv[2]
    (argv,) = argvs("nieuwsbrief", ["send"])
    assert argv[2].endswith('send --file "$f"')


def test_nieuwsbrief_send_named_file_must_be_bare_md():
    (argv,) = argvs("nieuwsbrief", ["send", "--file", "editie-2026-08.md"])
    assert "newsletters/editie-2026-08.md" in argv[2] and "ls -t" not in argv[2]
    with pytest.raises(kk.UsageError):
        kk.plan("nieuwsbrief", ["send", "--file", "../evil.md"], ROOT)
    with pytest.raises(kk.UsageError):
        kk.plan("nieuwsbrief", ["send", "--file", "editie"], ROOT)
    with pytest.raises(kk.UsageError):
        kk.plan("nieuwsbrief", ["oops"], ROOT)


def test_logs_cursus_alias_points_at_the_timer_unit():
    (argv,) = argvs("logs", ["cursus"])
    assert "klantkraan-cursus" in argv
    assert argvs("billing", ["subs", "cst_123"]) == [
        [AIR_PY, "-m", "app.billing", "subs", "cst_123"]
    ]


# -- health / logs -----------------------------------------------------------


def test_health_steps_are_tolerant():
    steps = kk.plan("health", [], ROOT)
    assert all(s.tolerant for s in steps)
    assert steps[0].argv[-1] == "--check"
    assert steps[1].argv[-1] == "--deep"
    assert any("ssh" in s.argv[0] for s in steps)


def test_health_lists_failed_units_on_the_server():
    steps = kk.plan("health", [], ROOT)
    assert any("--failed" in s.argv for s in steps)


def test_health_checks_alert_delivery_config():
    # OnFailure alerts are only real when the server can deliver them; a health run must
    # say so either way (§C5 defect 5: digest failures were invisible).
    steps = kk.plan("health", [], ROOT)
    ssh_payloads = [s.argv[-1] for s in steps if s.argv[0] == "ssh"]
    assert kk.ALERT_CONFIG_CHECK in ssh_payloads
    assert "OWNER_TELEGRAM_CHAT_ID" in kk.ALERT_CONFIG_CHECK
    assert "RESEND_API_KEY" in kk.ALERT_CONFIG_CHECK


def test_logs_alias_and_passthrough():
    (argv,) = argvs("logs", ["digest"])
    assert "ai-receptionist-digest" in argv
    (argv,) = argvs("logs", ["some-unit", "40"])
    assert "some-unit" in argv and "40" in argv


def test_logs_requires_unit():
    with pytest.raises(kk.UsageError):
        kk.plan("logs", [], ROOT)


# -- status ------------------------------------------------------------------


GEN = str(ROOT / "ops" / "status" / "generate.py")


def test_status_default_renders_ansi_from_the_app_dir():
    # cwd must be the app dir: the generator imports app.* / scripts.* from there.
    (step,) = kk.plan("status", [], ROOT)
    assert step.cwd == AIR
    assert step.argv == [AIR_PY, GEN, "--ansi"]


def test_status_open_renders_html_then_opens_it():
    steps = kk.plan("status", ["open"], ROOT)
    assert steps[0].argv[:3] == [AIR_PY, GEN, "--html"]
    page = steps[0].argv[3]
    assert steps[1].argv == ["open", page]


def test_status_push_ships_snapshot_then_regenerates_remote_page():
    steps = kk.plan("status", ["push"], ROOT)
    assert steps[0].argv[:3] == [AIR_PY, GEN, "--snapshot"]
    snap = steps[0].argv[3]
    assert steps[1].argv[0] == "scp" and steps[1].argv[1] == snap
    assert kk.SNAPSHOT_REMOTE in steps[1].argv[2]
    # remote follow-up must hand the file to the app user and regenerate immediately
    assert steps[2].argv[0] == "ssh"
    assert "chown klantkraan:klantkraan" in steps[2].argv[-1]
    assert "klantkraan-status.service" in steps[2].argv[-1]


def test_status_unknown_subverb_raises():
    with pytest.raises(kk.UsageError):
        kk.plan("status", ["frobnicate"], ROOT)


# -- deploy ------------------------------------------------------------------


def test_deploy_server_gates_on_evals_first():
    # ROOT does not exist, so the marker is unreadable: the gate must assume the worst
    steps = kk.plan("deploy", ["server"], ROOT)
    assert steps[0].argv == [AIR_PY, "-m", "app.evals", "run", "all"]
    assert not steps[0].tolerant  # a failing eval must abort the deploy
    assert steps[1].argv[-1] == kk.SERVER_IP
    assert "deploy.sh" in steps[1].argv[0]


def test_deploy_server_records_the_marker_last_and_tolerantly():
    steps = kk.plan("deploy", ["server"], ROOT)
    assert len(steps) == 3
    assert steps[2].argv[:2] == ["sh", "-c"]
    assert kk.DEPLOY_MARKER in steps[2].argv[2]
    assert "git rev-parse HEAD" in steps[2].argv[2]
    # a failed marker write must not fail a deploy that already landed
    assert steps[2].tolerant


def test_eval_surface_covers_prompt_tools_and_client_configs():
    assert kk.touches_eval_surface(["ai-receptionist/app/receptionist.py"])
    assert kk.touches_eval_surface(["ai-receptionist/app/tools.py"])
    assert kk.touches_eval_surface(["ai-receptionist/config/clients/dhz-autoservice.yaml"])
    assert kk.touches_eval_surface(["ai-receptionist/app/evals.py"])
    # one hit anywhere in the changeset is enough
    assert kk.touches_eval_surface(["ops/status/generate.py", "ai-receptionist/app/rdw.py"])


def test_eval_surface_excludes_everything_that_cannot_move_a_golden():
    assert not kk.touches_eval_surface([])
    assert not kk.touches_eval_surface([
        "ops/status/generate.py",
        "ops/hetzner/klantkraan-cursus.timer",
        "klantkraan/apps/marketing-site/src/pages/index.astro",
        "growth-engine/src/newsletter.py",
        "ai-receptionist/app/nieuwsbrief.py",   # mail sender, never in a conversation
        "ai-receptionist/tests/test_cursus.py",
    ])


def test_changed_since_deploy_is_unknown_without_a_marker(tmp_path):
    assert kk.changed_since_deploy(tmp_path) is None


def test_changed_since_deploy_is_unknown_when_the_marker_is_empty(tmp_path):
    marker = tmp_path / kk.DEPLOY_MARKER
    marker.parent.mkdir(parents=True)
    marker.write_text("  \n")
    assert kk.changed_since_deploy(tmp_path) is None


def test_deploy_site_sequence():
    steps = kk.plan("deploy", ["site"], ROOT)
    site = ROOT / "klantkraan" / "apps" / "marketing-site"
    assert [s.cwd for s in steps] == [site, site, site]
    assert steps[0].argv == ["npm", "run", "typecheck"]
    assert "--branch=production" in steps[2].argv


def test_deploy_needs_valid_target():
    for bad in ([], ["api"], ["prod"]):
        with pytest.raises(kk.UsageError):
            kk.plan("deploy", bad, ROOT)


# -- content / leads (read-only local verbs) ---------------------------------


def _write_json(path, data):
    import json

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


def test_content_boards_queues_flags_dry_run_and_errors(tmp_path, capsys):
    _write_json(
        tmp_path / "growth-engine" / "data" / "trades" / "queue.json",
        [
            {
                "id": "a1",
                "status": "pending",
                "topic": "gemiste oproepen",
                "created_at": "2026-08-12T09:00:00+02:00",
            },
            {"id": "a2", "status": "approved", "dry_run": True, "topic": "x"},
            {
                "id": "a3",
                "status": "posted",
                "topic": "y",
                "x_error": "2026-08-12T09:00:00+02:00 rate limited",
            },
        ],
    )
    assert kk.cmd_content(tmp_path, []) == 0
    out = capsys.readouterr().out
    assert "TRADES — 3 drafts" in out
    assert "1 approved, 1 pending, 1 posted" in out
    assert "(1 dry-run)" in out
    assert "pending  a1" in out and "gemiste oproepen" in out
    assert "a3  x push failed" in out and "rate limited" in out


def test_content_without_queues_fails(tmp_path, capsys):
    assert kk.cmd_content(tmp_path, []) == 1
    assert "no content queues" in capsys.readouterr().out


def test_leads_merges_all_four_stores_newest_first(tmp_path, capsys):
    data = tmp_path / "ai-receptionist" / "data"
    _write_json(
        data / "messages-acme.json",
        [
            {
                "at": "2026-08-01T10:00:00",
                "client": "acme",
                "customer_name": "Jan",
                "contact": "06-1",
                "message": "bel me\nterug",
            },
        ],
    )
    data.joinpath("leads.jsonl").write_text(
        '{"at": "2026-08-04T10:00:00", "naam": "Piet", "email": "p@x.nl", "plan": "chat"}\n'
        "NOT JSON — torn line must be skipped\n",
        encoding="utf-8",
    )
    data.joinpath("listing-leads-demo.jsonl").write_text(
        '{"at": "2026-08-03T10:00:00", "client": "demo", "customer_name": "Ana",'
        ' "contact": "a@x.es", "notes": "pool"}\n',
        encoding="utf-8",
    )
    _write_json(
        data / "bookings-acme.json",
        [
            {
                "created_at": "2026-08-02T10:00:00",
                "customer_name": "Kees",
                "contact": "k@x.nl",
                "service": "Check-up",
                "slot": "2026-08-03 08:00",
            },
        ],
    )
    assert kk.cmd_leads(tmp_path, []) == 0
    out = capsys.readouterr().out
    assert "4 records" in out
    order = [out.index(n) for n in ("Piet", "Ana", "Kees", "Jan")]
    assert order == sorted(order)  # newest first
    assert (
        "site-lead" in out
        and "listing" in out
        and "booking" in out
        and "message" in out
    )


def test_leads_limit_and_more_hint(tmp_path, capsys):
    data = tmp_path / "ai-receptionist" / "data"
    _write_json(
        data / "bookings.json",
        [
            {
                "created_at": f"2026-08-0{i}T10:00:00",
                "customer_name": f"c{i}",
                "contact": "x",
                "service": "s",
                "slot": "t",
            }
            for i in range(1, 6)
        ],
    )
    assert kk.cmd_leads(tmp_path, ["2"]) == 0
    out = capsys.readouterr().out
    assert "c5" in out and "c4" in out and "c3" not in out
    assert "… 3 more" in out


def test_content_and_leads_are_local_verbs_not_planned():
    assert set(kk.LOCAL_VERBS) == {"content", "leads"}
    for verb in kk.LOCAL_VERBS:
        with pytest.raises(kk.UsageError):
            kk.plan(verb, [], ROOT)


# -- site (client websites) --------------------------------------------------

CS = ROOT / "klantkraan" / "apps" / "client-sites"


def _write_client(tmp_path, slug, modus):
    d = tmp_path / "klantkraan" / "apps" / "client-sites" / "clients" / slug
    d.mkdir(parents=True)
    (d / "client.yaml").write_text(f"modus: {modus}\nbedrijf:\n  naam: Test\n", encoding="utf-8")
    return tmp_path


def test_site_new_passes_through_to_sitedraft():
    (step,) = kk.plan("site", ["new", "Jansen BV", "--url", "https://x.nl"], ROOT)
    assert step.cwd == AIR
    assert step.argv == [AIR_PY, "-m", "app.sitedraft", "Jansen BV", "--url", "https://x.nl"]


def test_site_build_builds_then_verifies_with_client_in_the_env():
    steps = kk.plan("site", ["build", "jansen"], ROOT)
    assert [s.argv for s in steps] == [["pnpm", "build"], ["pnpm", "check"]]
    assert all(s.cwd == CS and s.env == {"CLIENT": "jansen"} for s in steps)


def test_site_check_skips_the_build():
    (step,) = kk.plan("site", ["check", "jansen"], ROOT)
    assert step.argv == ["pnpm", "check"]


def test_site_open_never_serves_an_unverified_build():
    steps = kk.plan("site", ["open", "jansen"], ROOT)
    assert [s.argv for s in steps] == [["pnpm", "build"], ["pnpm", "check"], ["pnpm", "preview"]]


def test_site_deploy_puts_a_proposal_on_a_branch_of_the_shared_project(tmp_path):
    root = _write_client(tmp_path, "jansen", "preview")
    steps = kk.plan("site", ["deploy", "jansen"], root)
    assert [s.argv[:2] for s in steps] == [["pnpm", "build"], ["pnpm", "check"], ["pnpm", "dlx"]]
    assert steps[-1].argv[-2:] == ["--project-name=klant-preview", "--branch=jansen"]


def test_site_deploy_live_uses_the_clients_own_project(tmp_path):
    root = _write_client(tmp_path, "jansen", "live")
    steps = kk.plan("site", ["deploy", "jansen", "--live"], root)
    assert steps[-1].argv[-2:] == ["--project-name=client-jansen", "--branch=production"]


def test_site_deploy_refuses_to_take_a_proposal_live(tmp_path):
    root = _write_client(tmp_path, "jansen", "preview")
    with pytest.raises(kk.UsageError, match="voorstel"):
        kk.plan("site", ["deploy", "jansen", "--live"], root)


def test_site_deploy_refuses_to_put_a_paying_client_on_the_preview_host(tmp_path):
    root = _write_client(tmp_path, "jansen", "live")
    with pytest.raises(kk.UsageError, match="--live"):
        kk.plan("site", ["deploy", "jansen"], root)


def test_site_deploy_names_the_known_clients_when_the_slug_is_unknown(tmp_path):
    root = _write_client(tmp_path, "jansen", "live")
    with pytest.raises(kk.UsageError, match="jansen"):
        kk.plan("site", ["deploy", "onbekend"], root)


def test_site_rejects_a_slug_that_could_escape_the_clients_dir():
    for bad in ("../../etc", "Jansen", "a/b", ""):
        with pytest.raises(kk.UsageError):
            kk.site_modus(ROOT, bad)


def test_site_usage_errors():
    for args in ([], ["frobnicate"], ["new"], ["build"], ["deploy"]):
        with pytest.raises(kk.UsageError):
            kk.plan("site", args, ROOT)


# -- dispatcher shell --------------------------------------------------------


def test_unknown_verb_raises():
    with pytest.raises(kk.UsageError):
        kk.plan("frobnicate", [], ROOT)


def test_run_aborts_on_strict_failure_and_tolerates_tolerant(monkeypatch):
    calls = []

    class FakeProc:
        def __init__(self, rc):
            self.returncode = rc

    def fake_run(argv, cwd, check=False, env=None):
        calls.append((argv, env))
        return FakeProc(1 if argv == ["fail"] else 0)

    monkeypatch.setattr(kk.subprocess, "run", fake_run)
    steps = [
        kk.Step(ROOT, ["fail"], tolerant=True),
        kk.Step(ROOT, ["ok"]),
        kk.Step(ROOT, ["fail"]),
        kk.Step(ROOT, ["never"]),
    ]
    assert kk.run(steps) == 1
    assert [c[0] for c in calls] == [["fail"], ["ok"], ["fail"]]  # aborted before "never"
    assert all(env is None for _, env in calls)  # no env dict => inherit unchanged


def test_run_merges_step_env_over_the_environment(monkeypatch):
    seen = {}

    class FakeProc:
        returncode = 0

    def fake_run(argv, cwd, check=False, env=None):
        seen.update(env or {})
        return FakeProc()

    monkeypatch.setattr(kk.subprocess, "run", fake_run)
    monkeypatch.setenv("PATH", "/usr/bin")
    assert kk.run([kk.Step(ROOT, ["build"], env={"CLIENT": "jansen"})]) == 0
    assert seen["CLIENT"] == "jansen"
    assert seen["PATH"] == "/usr/bin"  # inherited, not replaced


def test_help_exits_zero(capsys):
    assert kk.main([]) == 0
    assert kk.main(["help"]) == 0
    assert "kk board" in capsys.readouterr().out
