"""TikTok draft upload via the official Content Posting API (inbox flow).

The reel lands in the founder's TikTok inbox as a draft; they add a trending sound
and post from the app (sounds can only be added in-app anyway). This uses the
`video.upload` scope — the audit-gated SELF_ONLY restriction applies to *direct
posting* (`video.publish`), which we deliberately don't use.

Tokens: access 24h, refresh 365d, both rotate on refresh; persisted to
data/<vertical>/tiktok_token.json (data/ is gitignored). Bootstrap once:
`python -m src.publish_tiktok --auth-url` → log in → `--code <code>`.
Setup runbook: docs/AUTOPUBLISH.md.
"""

from __future__ import annotations

import json
import secrets
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from .settings import data_dir, dry_run, env

_API = "https://open.tiktokapis.com"
_TOKEN_URL = f"{_API}/v2/oauth/token/"
_INIT_URL = f"{_API}/v2/post/publish/inbox/video/init/"
_STATUS_URL = f"{_API}/v2/post/publish/status/fetch/"
_AUTHORIZE_URL = "https://www.tiktok.com/v2/auth/authorize/"
_SCOPE = "video.upload"
_CHUNK_MAX = 64 * 2**20  # chunks are 5-64MB; the final one may run to 128MB
_MIME = {".mov": "video/quicktime", ".webm": "video/webm"}  # default video/mp4


class TikTokPublishError(RuntimeError):
    """Anything that stops a TikTok upload — always with an actionable message."""


def _client_creds() -> tuple[str, str]:
    key = (env("TIKTOK_CLIENT_KEY", required=False) or "").strip()
    secret = (env("TIKTOK_CLIENT_SECRET", required=False) or "").strip()
    missing = [n for n, v in (("TIKTOK_CLIENT_KEY", key),
                              ("TIKTOK_CLIENT_SECRET", secret)) if not v]
    if missing:
        raise TikTokPublishError(
            "missing env: " + ", ".join(missing)
            + " — fill .env per docs/AUTOPUBLISH.md (TikTok section)."
        )
    return key, secret


# --------------------------------------------------------------------------- #
# Token lifecycle (data/<vertical>/tiktok_token.json)
# --------------------------------------------------------------------------- #

def _token_path() -> Path:
    return data_dir() / "tiktok_token.json"


def _save_token(resp: dict[str, Any]) -> dict[str, Any]:
    now = time.time()
    tok = {
        "access_token": resp["access_token"],
        "refresh_token": resp["refresh_token"],
        "expires_at": now + float(resp.get("expires_in", 86400)),
        "refresh_expires_at": now + float(resp.get("refresh_expires_in", 31536000)),
        "open_id": resp.get("open_id", ""),
        "scope": resp.get("scope", ""),
    }
    path = _token_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(tok, indent=2), encoding="utf-8")
    return tok


def _load_token() -> dict[str, Any]:
    path = _token_path()
    if not path.exists():
        raise TikTokPublishError(
            f"no TikTok token yet ({path}). Run `python -m src.publish_tiktok "
            "--auth-url`, log in, then `--code <code>` — docs/AUTOPUBLISH.md."
        )
    return json.loads(path.read_text(encoding="utf-8"))


def _oauth_call(params: dict[str, str]) -> dict[str, Any]:
    req = urllib.request.Request(
        _TOKEN_URL,
        data=urllib.parse.urlencode(params).encode(),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            payload = json.load(resp)
    except urllib.error.HTTPError as exc:
        payload = json.loads(exc.read().decode("utf-8", "replace") or "{}")
    except urllib.error.URLError as exc:
        raise TikTokPublishError(f"cannot reach {_TOKEN_URL}: {exc.reason}") from None
    if payload.get("error") or "access_token" not in payload:
        raise TikTokPublishError(
            f"TikTok OAuth failed: {payload.get('error', 'no access_token')} — "
            f"{payload.get('error_description', json.dumps(payload)[:200])}"
        )
    return payload


def _refresh(tok: dict[str, Any]) -> dict[str, Any]:
    if time.time() >= tok.get("refresh_expires_at", 0):
        raise TikTokPublishError(
            "TikTok refresh token expired (365-day limit) — redo the --auth-url / "
            "--code flow from docs/AUTOPUBLISH.md."
        )
    key, secret = _client_creds()
    return _save_token(_oauth_call({
        "client_key": key,
        "client_secret": secret,
        "grant_type": "refresh_token",
        "refresh_token": tok["refresh_token"],
    }))


def _fresh_token(force_refresh: bool = False) -> dict[str, Any]:
    tok = _load_token()
    if force_refresh or time.time() >= tok.get("expires_at", 0) - 60:
        tok = _refresh(tok)
    return tok


def auth_url() -> str:
    """The one-time authorization URL the founder opens in a browser."""
    key, _ = _client_creds()
    redirect = (env("TIKTOK_REDIRECT_URI", required=False) or "").strip()
    if not redirect:
        raise TikTokPublishError(
            "missing env: TIKTOK_REDIRECT_URI — must exactly match the redirect URI "
            "registered on the TikTok app (docs/AUTOPUBLISH.md)."
        )
    return _AUTHORIZE_URL + "?" + urllib.parse.urlencode({
        "client_key": key,
        "scope": _SCOPE,
        "response_type": "code",
        "redirect_uri": redirect,
        "state": secrets.token_hex(8),
    })


def exchange_code(code: str) -> dict[str, Any]:
    """Trade the ?code= from the redirect for tokens and persist them."""
    key, secret = _client_creds()
    redirect = (env("TIKTOK_REDIRECT_URI", required=False) or "").strip()
    return _save_token(_oauth_call({
        "client_key": key,
        "client_secret": secret,
        "grant_type": "authorization_code",
        "code": urllib.parse.unquote(code),
        "redirect_uri": redirect,
    }))


# --------------------------------------------------------------------------- #
# Upload
# --------------------------------------------------------------------------- #

def _api(url: str, payload: dict[str, Any], access_token: str) -> dict[str, Any]:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; charset=UTF-8",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = json.load(resp)
    except urllib.error.HTTPError as exc:
        try:
            body = json.loads(exc.read().decode("utf-8", "replace"))
        except ValueError:
            raise TikTokPublishError(f"TikTok API {exc.code} on {url}") from None
    except urllib.error.URLError as exc:
        raise TikTokPublishError(f"cannot reach {url}: {exc.reason}") from None
    err = body.get("error") or {}
    if err.get("code") not in ("ok", None):
        raise TikTokPublishError(
            f"TikTok API error on {url}: {err.get('code')} — {err.get('message')} "
            f"(log_id {err.get('log_id')})"
        )
    return body.get("data") or {}


def _put_chunk(upload_url: str, blob: bytes, start: int, end: int,
               total: int, mime: str) -> None:
    req = urllib.request.Request(upload_url, data=blob, method="PUT", headers={
        "Content-Type": mime,
        "Content-Range": f"bytes {start}-{end}/{total}",
    })
    try:
        with urllib.request.urlopen(req, timeout=600) as resp:
            if resp.status not in (200, 201, 206):
                raise TikTokPublishError(
                    f"chunk upload got unexpected HTTP {resp.status}"
                )
    except urllib.error.HTTPError as exc:
        raise TikTokPublishError(
            f"chunk upload failed (HTTP {exc.code}): "
            f"{exc.read().decode('utf-8', 'replace')[:300]}"
        ) from None


def _poll_status(publish_id: str, access_token: str) -> str:
    """Wait until TikTok routed the upload to the inbox; returns the final status."""
    deadline = time.monotonic() + 90
    status = "PROCESSING_UPLOAD"
    while time.monotonic() < deadline:
        data = _api(_STATUS_URL, {"publish_id": publish_id}, access_token)
        status = data.get("status", "")
        if status in ("SEND_TO_USER_INBOX", "PUBLISH_COMPLETE"):
            return status
        if status == "FAILED":
            raise TikTokPublishError(
                f"TikTok rejected the upload: {data.get('fail_reason', 'unknown reason')}"
            )
        time.sleep(5)
    return f"{status} (still processing — the inbox notification may take a minute)"


def verify_auth() -> str:
    """Prove the stored refresh token works; returns an identity summary."""
    _client_creds()
    # Force a refresh: succeeding is the proof the grant is still alive.
    tok = _fresh_token(force_refresh=True)
    days = max(int((tok["refresh_expires_at"] - time.time()) // 86400), 0)
    return (
        f"TikTok OK: open_id {tok.get('open_id') or '?'}, scope '{tok.get('scope')}', "
        f"refresh token valid ~{days} more days"
    )


def upload_draft(draft: dict[str, Any], media: dict[str, Any]) -> str:
    """Upload the draft's reel to the founder's TikTok inbox; returns a confirmation.

    The caption (draft['variants']['tiktok']) cannot ride along on inbox uploads —
    the founder pastes it in-app; the bot still sends it to Telegram for that.
    """
    if dry_run():
        return "(dry-run: not actually uploaded)"
    if not media or media.get("type") != "video" or media.get("status") != "ready" \
            or not media.get("path"):
        raise TikTokPublishError("TikTok needs a ready reel; this draft has none.")
    path = Path(media["path"])
    if not path.exists():
        raise TikTokPublishError(f"media file missing on disk: {path}")

    size = path.stat().st_size
    # <=64MB uploads as one chunk (files under 5MB MUST be whole); bigger files use
    # 64MB chunks with the remainder merged into the final chunk (<=128MB allowed).
    chunk = min(size, _CHUNK_MAX)
    count = max(size // chunk, 1)

    tok = _fresh_token()
    init = _api(_INIT_URL, {"source_info": {
        "source": "FILE_UPLOAD",
        "video_size": size,
        "chunk_size": chunk,
        "total_chunk_count": count,
    }}, tok["access_token"])
    publish_id, upload_url = init.get("publish_id"), init.get("upload_url")
    if not publish_id or not upload_url:
        raise TikTokPublishError(f"init returned no upload_url: {init}")

    mime = _MIME.get(path.suffix.lower(), "video/mp4")
    with path.open("rb") as fh:
        for i in range(count):
            start = i * chunk
            end = size - 1 if i == count - 1 else start + chunk - 1
            _put_chunk(upload_url, fh.read(end - start + 1), start, end, size, mime)

    status = _poll_status(publish_id, tok["access_token"])
    return (
        f"TikTok draft uploaded ({status}, publish_id {publish_id}) — open the TikTok "
        "app inbox notification, add a trending sound + the caption, and post."
    )


def _main(argv: list[str]) -> int:
    try:
        if "--auth-url" in argv:
            print(auth_url())
            print("Open this in a browser, log in as the founder's TikTok account, "
                  "then run: python -m src.publish_tiktok --code <code-from-redirect>")
            return 0
        if "--code" in argv:
            idx = argv.index("--code")
            if idx + 1 >= len(argv):
                raise TikTokPublishError("usage: python -m src.publish_tiktok --code <code>")
            tok = exchange_code(argv[idx + 1])
            print(f"token saved to {_token_path()} (open_id {tok.get('open_id')}, "
                  f"scope '{tok.get('scope')}')")
            return 0
        # default / --check: report credential state (never uploads)
        print(verify_auth())
        return 0
    except TikTokPublishError as exc:
        print(f"publish_tiktok: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
