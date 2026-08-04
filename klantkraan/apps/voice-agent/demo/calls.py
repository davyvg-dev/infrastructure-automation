"""Call log for the ElevenLabs voice agent, from the terminal.

    python3 calls.py            # recent calls, newest first
    python3 calls.py show 1     # transcript + analysis of the Nth call (1 = newest)
    python3 calls.py show conv_...   # same, by conversation id

Reads ELEVENLABS_API_KEY and ELEVENLABS_AGENT_ID from ../.env (or the environment).
"""

import json
import os
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

BASE = "https://api.elevenlabs.io/v1/convai"


def env(name: str) -> str:
    if os.environ.get(name):
        return os.environ[name]
    env_file = Path(__file__).resolve().parent.parent / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if line.startswith(f"{name}="):
                return line.split("=", 1)[1].strip()
    sys.exit(f"{name} not set and not found in {env_file}")


def get(path: str) -> dict:
    req = urllib.request.Request(f"{BASE}{path}", headers={"xi-api-key": env("ELEVENLABS_API_KEY")})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.load(r)


def fetch_recent(n: int = 15) -> list[dict]:
    agent = env("ELEVENLABS_AGENT_ID")
    return get(f"/conversations?agent_id={agent}&page_size={n}")["conversations"]


def cmd_list() -> None:
    convs = fetch_recent()
    if not convs:
        print("no calls yet")
        return
    for i, c in enumerate(convs, 1):
        t = datetime.fromtimestamp(c["start_time_unix_secs"]).strftime("%d-%m %H:%M")
        dur = f"{c['call_duration_secs']:>4}s"
        status = c["status"]
        ok = {"success": "ok", "failure": "FAILED", "unknown": "?"}.get(c["call_successful"], "?")
        summary = (c.get("call_summary_title") or c.get("transcript_summary") or "").replace("\n", " ")[:70]
        print(f"{i:>2}. {t}  {dur}  {status:<11} {ok:<7} {summary}")


def cmd_show(which: str) -> None:
    if which.startswith("conv_"):
        conv_id = which
    else:
        convs = fetch_recent()
        idx = int(which)
        if not 1 <= idx <= len(convs):
            sys.exit(f"no call #{idx}, only {len(convs)} recent calls")
        conv_id = convs[idx - 1]["conversation_id"]
    d = get(f"/conversations/{conv_id}")
    meta = d.get("metadata", {})
    call = meta.get("phone_call", {})
    an = d.get("analysis") or {}
    print(f"id:        {conv_id}")
    print(f"caller:    {call.get('external_number', '-')}  ->  {call.get('agent_number', '-')}")
    print(f"status:    {d.get('status')}  |  ended: {meta.get('termination_reason', '-')}")
    print(f"duration:  {meta.get('call_duration_secs', '?')}s  |  verdict: {an.get('call_successful', '?')}")
    if an.get("transcript_summary"):
        print(f"\nsummary:   {an['transcript_summary']}")
    results = an.get("data_collection_results") or {}
    if results:
        print("\ncollected:")
        for k, v in results.items():
            print(f"  {k}: {v.get('value') if isinstance(v, dict) else v}")
    print("\ntranscript:")
    for turn in d.get("transcript") or []:
        msg = (turn.get("message") or "").strip()
        if msg:
            print(f"  {turn['role']:>5}: {msg}")
        for tc in turn.get("tool_calls") or []:
            print(f"   tool: {tc.get('tool_name')}({tc.get('params_as_json', '')})")


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] == "list":
        cmd_list()
    elif args[0] == "show" and len(args) == 2:
        cmd_show(args[1])
    else:
        sys.exit(__doc__)
