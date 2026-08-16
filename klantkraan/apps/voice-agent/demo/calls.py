"""Call log for the ElevenLabs voice agent, from the terminal.

    python3 calls.py            # recent calls, newest first
    python3 calls.py show 1     # transcript + analysis of the Nth call (1 = newest)
    python3 calls.py show conv_...   # same, by conversation id
    python3 calls.py latency 1  # per-turn stage latencies (asr/llm/tts) of the Nth call

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


def resolve_conv_id(which: str) -> str:
    if which.startswith("conv_"):
        return which
    convs = fetch_recent()
    idx = int(which)
    if not 1 <= idx <= len(convs):
        sys.exit(f"no call #{idx}, only {len(convs)} recent calls")
    return convs[idx - 1]["conversation_id"]


def cmd_show(which: str) -> None:
    conv_id = resolve_conv_id(which)
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


STAGES = {  # metric key -> column header, in pipeline order
    "convai_turn_asr_latency": "asr",
    "convai_llm_service_ttfb": "llm_ttfb",
    "convai_llm_service_ttf_sentence": "llm_sent",
    "convai_llm_tool_request_generation_latency": "tool_gen",
    "convai_tts_service_ttfb": "tts_ttfb",
    "convai_ttf_audio_since_silence": "audio",
}


def cmd_latency(which: str) -> None:
    conv_id = resolve_conv_id(which)
    d = get(f"/conversations/{conv_id}")
    rows = []
    for i, turn in enumerate(d.get("transcript") or []):
        metrics = (turn.get("conversation_turn_metrics") or {}).get("metrics") or {}
        if not metrics:
            continue
        vals = {h: metrics.get(k, {}).get("elapsed_time") for k, h in STAGES.items()}
        # audio includes deliberate turn-taking silence; subtract it to get pipeline time
        wait = metrics.get("convai_turn_silence_before_initiation", {}).get("elapsed_time")
        if vals["audio"] is not None and wait:
            vals["audio"] -= wait
        msg = (turn.get("message") or "").strip().replace("\n", " ")[:40]
        rows.append((i, vals, msg))
    if not rows:
        print("no turn metrics on this call")
        return
    headers = list(STAGES.values())
    print(f"call {conv_id}  (seconds; audio = first agent audio after caller silence, minus wait)")
    print(f"{'turn':>4}  " + "".join(f"{h:>9}" for h in headers) + "  agent said")
    for i, vals, msg in rows:
        cells = "".join(f"{vals[h]:>9.3f}" if vals[h] is not None else f"{'-':>9}" for h in headers)
        print(f"{i:>4}  {cells}  {msg}")
    print(f"{'':>4}  " + "-" * (9 * len(headers)))
    for label, pick in (("median", lambda xs: sorted(xs)[len(xs) // 2]), ("max", max)):
        cells = ""
        for h in headers:
            xs = [v[h] for _, v, _ in rows if v[h] is not None]
            cells += f"{pick(xs):>9.3f}" if xs else f"{'-':>9}"
        print(f"{label:>4}  {cells}")


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] == "list":
        cmd_list()
    elif args[0] == "show" and len(args) == 2:
        cmd_show(args[1])
    elif args[0] == "latency" and len(args) == 2:
        cmd_latency(args[1])
    else:
        sys.exit(__doc__)
