"""Self-healing liveness + deep-answer watchdog for the receptionist demo.

Run by a systemd timer every ~2 min (ops/hetzner/ai-receptionist-watchdog.*).
Two checks, because "process up" and "actually answering" fail independently:

  liveness  every run   GET  /health   -> if down: restart the service + re-probe
  deep      every ~15m  POST /chat      -> a real Claude turn; catches a dead API
                                           key / no credits / model error, which
                                           leave /health green but the bot mute.

The deep probe is what the 2026-07-19 outage needed: an invalid ANTHROPIC_API_KEY
kept /health at 200 while every real turn 503'd. A restart cannot fix that, so a
deep failure ALERTS (human must rotate the key / top up); a liveness failure both
self-heals and alerts. Alerts fire only on state transitions, so a lasting outage
never spams. stdlib only; reuses app.notify for the Telegram ping.

Env (all optional; sensible defaults):
  WATCHDOG_HEALTH_URL     default https://demo-168-119-173-25.sslip.io/health
  WATCHDOG_CHAT_URL       default = health URL with /health -> /chat
  WATCHDOG_SERVICE        systemd unit to restart, default ai-receptionist
  WATCHDOG_DEEP_INTERVAL  seconds between deep probes, default 900
  WATCHDOG_CHAT_API_KEY   sent as x-api-key if the /chat endpoint is protected
  WATCHDOG_STATE_FILE     default data/watchdog_state.json
  WATCHDOG_ENV_FILE       .env to load creds from, default <app>/.env

Usage:
  python -m app.watchdog          # for the timer: probe, self-heal, alert on transition
  python -m app.watchdog --check  # liveness once, print, no restart/alert/state
  python -m app.watchdog --deep   # force a /chat probe, print, no alert/state
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.request

_APP_DIR = os.path.dirname(os.path.dirname(__file__))


def _load_env_file() -> None:
    """Load the app's .env into os.environ (existing vars win) so the watchdog
    finds the Telegram creds whether launched by systemd or by hand. Robust to
    `export ` prefixes, quotes, and comment lines."""
    path = os.getenv("WATCHDOG_ENV_FILE", os.path.join(_APP_DIR, ".env"))
    try:
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, val = line.removeprefix("export ").partition("=")
                key = key.strip()
                if key and key not in os.environ:
                    os.environ[key] = val.strip().strip("'\"")
    except OSError:
        pass  # no .env (e.g. local --check) — rely on the process environment


_load_env_file()

HEALTH_URL = os.getenv("WATCHDOG_HEALTH_URL", "https://demo-168-119-173-25.sslip.io/health")
CHAT_URL = os.getenv("WATCHDOG_CHAT_URL") or HEALTH_URL.replace("/health", "/chat")
SERVICE = os.getenv("WATCHDOG_SERVICE", "ai-receptionist")
DEEP_INTERVAL = int(os.getenv("WATCHDOG_DEEP_INTERVAL", "900"))
CHAT_API_KEY = os.getenv("WATCHDOG_CHAT_API_KEY")
STATE_FILE = os.getenv("WATCHDOG_STATE_FILE", os.path.join(_APP_DIR, "data", "watchdog_state.json"))


def probe() -> tuple[bool, str]:
    """Liveness: HTTP 200 with JSON status == 'ok' from /health."""
    try:
        req = urllib.request.Request(HEALTH_URL, headers={"User-Agent": "klantkraan-watchdog"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            code, body = resp.getcode(), resp.read(2048).decode("utf-8", "replace")
        if code != 200:
            return False, f"HTTP {code}"
        return (json.loads(body).get("status") == "ok"), body[:120]
    except Exception as exc:  # noqa: BLE001 - any failure means "not reachable"
        return False, f"{type(exc).__name__}: {exc}"


def deep_probe() -> tuple[bool, str]:
    """Real turn: POST /chat and require a 200 with a non-empty reply — proves the
    Claude call (key, credits, model, tool loop) actually works end to end."""
    payload = json.dumps(
        {"message": "Systeemcontrole, geen actie nodig.", "session_id": "watchdog"}
    ).encode()
    headers = {"Content-Type": "application/json", "User-Agent": "klantkraan-watchdog"}
    if CHAT_API_KEY:
        headers["x-api-key"] = CHAT_API_KEY
    try:
        req = urllib.request.Request(CHAT_URL, data=payload, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=30) as resp:
            code, body = resp.getcode(), resp.read(4096).decode("utf-8", "replace")
        if code != 200:
            return False, f"HTTP {code}"
        reply = json.loads(body).get("reply", "")
        return (bool(reply.strip())), (f"reply: {reply[:80]}" if reply else "empty reply")
    except Exception as exc:  # noqa: BLE001
        return False, f"{type(exc).__name__}: {exc}"


def restart_service() -> str:
    """Best-effort `systemctl restart`. Returns a short outcome string."""
    try:
        subprocess.run(["systemctl", "restart", SERVICE], check=True, capture_output=True, timeout=60)
        return f"restarted {SERVICE}"
    except Exception as exc:  # noqa: BLE001
        return f"restart FAILED ({type(exc).__name__}: {exc})"


def _load_state() -> dict:
    try:
        with open(STATE_FILE, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError):
        return {}  # first run: absent keys default to healthy so we only alert on real transitions


def _save_state(state: dict) -> None:
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    state["ts"] = int(time.time())
    with open(STATE_FILE, "w", encoding="utf-8") as fh:
        json.dump(state, fh)


def _alert(text: str) -> None:
    from app import notify  # lazy so --check / --deep need no alert config

    notify.owner(text)


def main() -> int:
    if "--check" in sys.argv:
        ok, detail = probe()
        print(f"liveness: {'UP' if ok else 'DOWN'}  {HEALTH_URL}  ({detail})")
        return 0 if ok else 1
    if "--deep" in sys.argv:
        ok, detail = deep_probe()
        print(f"deep: {'ANSWERING' if ok else 'SILENT'}  {CHAT_URL}  ({detail})")
        return 0 if ok else 1

    state = _load_state()

    # 1. Liveness — self-heal a down/crashed/hung process, alert on transition.
    ok, detail = probe()
    healed = ""
    if not ok:
        healed = restart_service()
        time.sleep(8)
        ok, detail = probe()
    now = "up" if ok else "down"
    if now != state.get("status", "up"):
        if now == "down":
            _alert(f"\U0001f534 Chatbot DOWN — {HEALTH_URL}\n{detail}\nself-heal: {healed or 'n/a'}")
        else:
            _alert(f"\U0001f7e2 Chatbot back UP — {HEALTH_URL}" + (f" (after {healed})" if healed else ""))
    state["status"], state["detail"] = now, detail

    # 2. Deep answer probe — only when live, and only every DEEP_INTERVAL. A dead
    #    key / no credits fails here while liveness stays green; restart won't fix
    #    it, so this alerts a human. Transition-gated, same as liveness.
    if ok and (time.time() - int(state.get("deep_ts", 0))) >= DEEP_INTERVAL:
        d_ok, d_detail = deep_probe()
        d_now = "answering" if d_ok else "silent"
        if d_now != state.get("deep_status", "answering"):
            if d_now == "silent":
                _alert(
                    f"\U0001f7e0 Chatbot is UP but NOT ANSWERING — {CHAT_URL}\n{d_detail}\n"
                    "Likely API key / credits / model. A restart won't fix it — check the key."
                )
            else:
                _alert(f"\U0001f7e2 Chatbot answering again — {CHAT_URL}")
        state["deep_status"], state["deep_ts"] = d_now, int(time.time())

    _save_state(state)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
