"""Offline tests for the kk dispatcher: planner logic only, nothing executes."""

import importlib.machinery
import importlib.util
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


def test_logs_alias_and_passthrough():
    (argv,) = argvs("logs", ["digest"])
    assert "ai-receptionist-digest" in argv
    (argv,) = argvs("logs", ["some-unit", "40"])
    assert "some-unit" in argv and "40" in argv


def test_logs_requires_unit():
    with pytest.raises(kk.UsageError):
        kk.plan("logs", [], ROOT)


# -- deploy ------------------------------------------------------------------

def test_deploy_server_gates_on_evals_first():
    steps = kk.plan("deploy", ["server"], ROOT)
    assert steps[0].argv == [AIR_PY, "-m", "app.evals", "run", "all"]
    assert not steps[0].tolerant  # a failing eval must abort the deploy
    assert steps[1].argv[-1] == kk.SERVER_IP
    assert "deploy.sh" in steps[1].argv[0]


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


# -- dispatcher shell --------------------------------------------------------

def test_unknown_verb_raises():
    with pytest.raises(kk.UsageError):
        kk.plan("frobnicate", [], ROOT)


def test_run_aborts_on_strict_failure_and_tolerates_tolerant(monkeypatch):
    calls = []

    class FakeProc:
        def __init__(self, rc):
            self.returncode = rc

    def fake_run(argv, cwd, check=False):
        calls.append(argv)
        return FakeProc(1 if argv == ["fail"] else 0)

    monkeypatch.setattr(kk.subprocess, "run", fake_run)
    steps = [
        kk.Step(ROOT, ["fail"], tolerant=True),
        kk.Step(ROOT, ["ok"]),
        kk.Step(ROOT, ["fail"]),
        kk.Step(ROOT, ["never"]),
    ]
    assert kk.run(steps) == 1
    assert calls == [["fail"], ["ok"], ["fail"]]  # aborted before "never"


def test_help_exits_zero(capsys):
    assert kk.main([]) == 0
    assert kk.main(["help"]) == 0
    assert "kk board" in capsys.readouterr().out
