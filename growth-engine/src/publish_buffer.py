"""Buffer delivery — hand an approved draft to Buffer's per-channel queue.

Buffer is an official publishing partner for LinkedIn (and Instagram, X, Facebook),
so posting through it is sanctioned automation where a direct API call would not be.
One approval pushes the text into the channel's queue and *Buffer* decides when it
goes out — the schedule lives in Buffer's UI, never in this repo.

GraphQL, one endpoint, bearer auth (available on every plan incl. Free):

    channels(input:{organizationId})  → the connected channel IDs
    createPost(input:{..., mode: addToQueue}) → next free slot in that channel's queue

Text-only for now. Assets go in by URL (Buffer fetches them), so image/reel posts
need data/<vertical>/media/ served over public HTTPS first — until that exists,
media is left off and the founder attaches it in Buffer if they want it.

Inspect the wiring without posting: `python -m src.publish_buffer`.
Docs: context7 /websites/developers_buffer (fetched 2026-07-30).
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from functools import lru_cache
from typing import Any

from .settings import dry_run, env

_ENDPOINT = "https://api.buffer.com"

# Buffer identifies a channel by `service`, which matches our platform keys except
# where Buffer kept the old brand name.
_SERVICE_ALIASES = {"x": ("x", "twitter")}


class BufferError(RuntimeError):
    """Anything that stops a Buffer call — always with an actionable message."""


def _gql(query: str) -> dict[str, Any]:
    """One GraphQL round-trip. Both error channels (HTTP + `errors`) surface as BufferError."""
    key = (env("BUFFER_API_KEY", required=False) or "").strip()
    if not key:
        raise BufferError("BUFFER_API_KEY is not set — see .env.example (Buffer section).")
    req = urllib.request.Request(
        _ENDPOINT,
        data=json.dumps({"query": query}).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            payload = json.load(resp)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace").strip()[:300]
        hint = " (is BUFFER_API_KEY still valid?)" if exc.code in (401, 403) else ""
        raise BufferError(f"Buffer HTTP {exc.code}{hint}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise BufferError(f"Buffer unreachable: {exc.reason}") from exc
    if payload.get("errors"):
        raise BufferError(
            "Buffer rejected the query: "
            + "; ".join(str(e.get("message", e)) for e in payload["errors"])
        )
    data = payload.get("data")
    if not isinstance(data, dict):
        raise BufferError(f"Buffer returned no data: {str(payload)[:200]}")
    return data


@lru_cache(maxsize=1)
def organization_id() -> str:
    """The org whose channels we post to. Pin BUFFER_ORGANIZATION_ID if there are several."""
    pinned = (env("BUFFER_ORGANIZATION_ID", required=False) or "").strip()
    if pinned:
        return pinned
    orgs = (_gql("query { account { organizations { id name } } }").get("account") or {}).get(
        "organizations"
    ) or []
    if not orgs:
        raise BufferError("this Buffer account has no organization — finish signup at buffer.com")
    if len(orgs) > 1:
        listed = ", ".join(f"{o.get('name')} ({o['id']})" for o in orgs)
        raise BufferError(
            f"{len(orgs)} Buffer organizations ({listed}) — set BUFFER_ORGANIZATION_ID "
            f"to the one Klantkraan posts from."
        )
    return orgs[0]["id"]


@lru_cache(maxsize=1)
def channels() -> list[dict[str, Any]]:
    """Every channel connected to the organization (id, name, service, queue state)."""
    query = (
        "query Channels { channels(input: {organizationId: "
        + json.dumps(organization_id())
        + "}) { id name displayName service isQueuePaused } }"
    )
    return _gql(query).get("channels") or []


def label(channel: dict[str, Any]) -> str:
    return channel.get("displayName") or channel.get("name") or channel["id"]


def _connected() -> str:
    found = channels()
    return ", ".join(f"{c.get('service')}:{label(c)}" for c in found) if found else "(none)"


def channel_for(platform: str) -> dict[str, Any]:
    """The Buffer channel a platform posts to. BUFFER_CHANNEL_<PLATFORM> wins over
    matching on service, which is what you need when one service has two channels
    (personal profile + company page)."""
    found = channels()
    override = f"BUFFER_CHANNEL_{platform.upper()}"
    pinned = (env(override, required=False) or "").strip()
    if pinned:
        for ch in found:
            if pinned in (ch["id"], ch.get("name"), ch.get("displayName")):
                return ch
        raise BufferError(f"{override}={pinned!r} matches no Buffer channel — have: {_connected()}")
    wanted = _SERVICE_ALIASES.get(platform, (platform,))
    matches = [c for c in found if (c.get("service") or "").lower() in wanted]
    if not matches:
        raise BufferError(
            f"no Buffer channel for '{platform}' — connect it at buffer.com, or set "
            f"{platform}'s delivery to 'assisted' in config. Connected: {_connected()}"
        )
    if len(matches) > 1:
        listed = ", ".join(label(c) + " = " + c["id"] for c in matches)
        raise BufferError(
            f"{len(matches)} Buffer channels for '{platform}' ({listed}) — "
            f"set {override} to the one to post to."
        )
    return matches[0]


# `assets` is [AssetInput!]! — required even for a text post, so it is passed empty.
# Sentinels instead of format specifiers: GraphQL is all braces, and the values are
# JSON-encoded so the post text can carry quotes and newlines safely.
_QUEUE_POST = """
mutation QueuePost {
  createPost(input: {
    text: <TEXT>
    channelId: <CHANNEL>
    schedulingType: automatic
    mode: addToQueue
    assets: []
  }) {
    __typename
    ... on PostActionSuccess { post { id dueAt } }
    ... on MutationError { message }
  }
}
"""


def queue(platform: str, text: str) -> str:
    """Add the text to the platform's Buffer queue. Returns a note saying when it goes out."""
    if dry_run():
        return "(dry-run: not queued in Buffer)"
    channel = channel_for(platform)
    # Channel first, so post text containing the other sentinel can't be substituted into.
    query = _QUEUE_POST.replace("<CHANNEL>", json.dumps(channel["id"])).replace(
        "<TEXT>", json.dumps(text)
    )
    result = _gql(query).get("createPost") or {}
    if result.get("__typename") != "PostActionSuccess":
        raise BufferError(
            f"Buffer refused the post ({result.get('__typename') or 'unknown error'}): "
            f"{result.get('message') or 'no message given'}"
        )
    post = result.get("post") or {}
    note = f"{label(channel)} — goes out {post.get('dueAt') or 'at the next open slot'}"
    if channel.get("isQueuePaused"):
        note += " (⚠️ this queue is PAUSED in Buffer — nothing sends until you unpause it)"
    return note


def verify_auth() -> str:
    """Prove the key works and show what each platform would post to (for selftest)."""
    found = channels()
    if not found:
        raise BufferError(
            f"key works (org {organization_id()}) but no channels are connected — "
            f"connect them at buffer.com."
        )
    lines = [f"Buffer OK: org {organization_id()}, {len(found)} channel(s)"]
    for ch in found:
        paused = " [queue paused]" if ch.get("isQueuePaused") else ""
        lines.append(f"        {ch.get('service')}: {label(ch)} = {ch['id']}{paused}")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    """`python -m src.publish_buffer` — show the channels and the platform mapping."""
    try:
        print(verify_auth())
        from . import platforms

        for name, desc in platforms.registry().items():
            if desc.get("delivery") != "buffer":
                continue
            try:
                print(f"  {name} -> {label(channel_for(name))}")
            except BufferError as exc:
                print(f"  {name} -> UNRESOLVED: {exc}")
    except Exception as exc:
        print(f"publish_buffer: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
