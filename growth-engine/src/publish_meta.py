"""Instagram + Facebook Page publishing via the official Meta Graph API (v25.0).

Instagram (professional account linked to the Facebook Page):
  image — container from a PUBLIC image_url (Meta downloads the file, so
          META_MEDIA_BASE_URL must serve data/<vertical>/media/ over HTTPS),
          then media_publish.
  reel  — resumable upload: the local file goes straight to rupload.facebook.com
          (no public hosting needed), poll status_code, then media_publish.
Facebook Page:
  text  — POST /{page}/feed
  photo — POST /{page}/photos (multipart local file, no hosting needed)
  reel  — POST /{page}/video_reels start → rupload → finish

One credential covers both: a long-lived Page access token (no expiry) for the Page
the IG account is linked to. The app can stay in Development mode — Standard Access
publishes fine for accounts whose owner has a role on the app, no App Review.
Setup + token curl commands: docs/AUTOPUBLISH.md.
"""

from __future__ import annotations

import json
import mimetypes
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path
from typing import Any

from .settings import dry_run, env

_GRAPH = "https://graph.facebook.com"
_RUPLOAD = "https://rupload.facebook.com"
_REQUIRED = ("META_ACCESS_TOKEN", "META_FB_PAGE_ID", "META_IG_USER_ID")
_POLL_INTERVAL = 4  # seconds between container status checks
_POLL_LIMIT = 300  # give a reel five minutes to transcode


class MetaPublishError(RuntimeError):
    """Anything that stops a Meta publish — always with an actionable message."""


def _version() -> str:
    return env("META_GRAPH_VERSION", required=False) or "v25.0"


def _creds() -> tuple[str, str, str]:
    vals = {n: (env(n, required=False) or "").strip() for n in _REQUIRED}
    missing = [n for n, v in vals.items() if not v]
    if missing:
        raise MetaPublishError(
            "missing env: " + ", ".join(missing)
            + " — fill .env per docs/AUTOPUBLISH.md (Meta section)."
        )
    return vals["META_ACCESS_TOKEN"], vals["META_FB_PAGE_ID"], vals["META_IG_USER_ID"]


def _call(url: str, *, data: bytes | None = None, headers: dict[str, str] | None = None,
          method: str | None = None, timeout: int = 120) -> dict[str, Any]:
    """One HTTP round-trip; Graph errors surface as MetaPublishError with Meta's message."""
    req = urllib.request.Request(url, data=data, headers=headers or {}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", "replace")
        try:
            err = json.loads(body)["error"]
            detail = f"{err.get('message')} (code {err.get('code')})"
            if err.get("code") == 190:
                detail += " — token invalid/expired; redo the token steps in docs/AUTOPUBLISH.md"
        except (ValueError, KeyError, TypeError):
            detail = body[:300]
        raise MetaPublishError(
            f"Graph API {exc.code} on {url.split('?')[0]}: {detail}"
        ) from None
    except urllib.error.URLError as exc:
        raise MetaPublishError(f"cannot reach {url.split('?')[0]}: {exc.reason}") from None


def _graph(path: str, params: dict[str, str], method: str = "POST",
           timeout: int = 120) -> dict[str, Any]:
    qs = urllib.parse.urlencode(params)
    url = f"{_GRAPH}/{_version()}/{path}"
    if method == "GET":
        return _call(f"{url}?{qs}", timeout=timeout)
    return _call(url, data=qs.encode(), method="POST", timeout=timeout)


def _multipart(fields: dict[str, str], file_field: str, path: Path) -> tuple[bytes, str]:
    """multipart/form-data body for a local-file upload (stdlib only, no requests)."""
    boundary = uuid.uuid4().hex
    body = bytearray()
    for name, value in fields.items():
        body += (
            f"--{boundary}\r\nContent-Disposition: form-data; "
            f'name="{name}"\r\n\r\n{value}\r\n'
        ).encode()
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    body += (
        f"--{boundary}\r\nContent-Disposition: form-data; "
        f'name="{file_field}"; filename="{path.name}"\r\n'
        f"Content-Type: {mime}\r\n\r\n"
    ).encode()
    body += path.read_bytes()
    body += f"\r\n--{boundary}--\r\n".encode()
    return bytes(body), f"multipart/form-data; boundary={boundary}"


def _media_path(media: dict[str, Any] | None, need: str) -> Path:
    if not media or media.get("status") != "ready" or not media.get("path"):
        raise MetaPublishError(f"{need} — this draft has no ready media record.")
    path = Path(media["path"])
    if not path.exists():
        raise MetaPublishError(f"media file missing on disk: {path}")
    return path


def _wait_finished(container_id: str, token: str) -> None:
    """Poll the IG container until Meta has ingested the media (FINISHED)."""
    deadline = time.monotonic() + _POLL_LIMIT
    status = "IN_PROGRESS"
    while time.monotonic() < deadline:
        info = _graph(container_id, {"fields": "status_code,status",
                                     "access_token": token}, method="GET")
        status = info.get("status_code", "")
        if status == "FINISHED":
            return
        if status in ("ERROR", "EXPIRED"):
            raise MetaPublishError(
                f"IG container {container_id} ended {status}: {info.get('status')}"
            )
        time.sleep(_POLL_INTERVAL)
    raise MetaPublishError(
        f"IG container {container_id} still {status} after {_POLL_LIMIT}s — "
        "check the video specs (MP4 H.264, 9:16, 3s-15min) and retry."
    )


def verify_auth() -> str:
    """Prove the token works; returns an identity summary (for selftest use)."""
    token, page_id, ig_id = _creds()
    page = _graph(page_id, {"fields": "name,instagram_business_account",
                            "access_token": token}, method="GET")
    ig = _graph(ig_id, {"fields": "username", "access_token": token}, method="GET")
    linked = (page.get("instagram_business_account") or {}).get("id")
    note = "" if linked == ig_id else (
        f" — WARNING: the Page's linked IG account is {linked!r}, not META_IG_USER_ID"
    )
    return (
        f"Meta OK: Page '{page.get('name')}' ({page_id}), "
        f"IG @{ig.get('username')} ({ig_id}){note}"
    )


def publish_instagram(draft: dict[str, Any], media: dict[str, Any]) -> str:
    """Publish the draft's IG variant with its media; returns the post permalink."""
    if dry_run():
        return "(dry-run: not actually posted)"
    caption = (draft.get("variants") or {}).get("instagram", "")
    token, _, ig_id = _creds()
    path = _media_path(media, "Instagram requires an image or reel")

    if media["type"] == "image":
        base = (env("META_MEDIA_BASE_URL", required=False) or "").strip()
        if not base:
            raise MetaPublishError(
                "META_MEDIA_BASE_URL is not set. IG image posts need a public URL "
                "(Meta downloads the file); serve data/<vertical>/media/ over HTTPS "
                "and set the base URL — docs/AUTOPUBLISH.md § IG image hosting. "
                "(Reels are unaffected: they upload the local file directly.)"
            )
        container = _graph(f"{ig_id}/media", {
            "image_url": f"{base.rstrip('/')}/{path.name}",
            "caption": caption,
            "access_token": token,
        })["id"]
    else:  # video → Reel via resumable upload (local file, no hosting)
        init = _graph(f"{ig_id}/media", {
            "media_type": "REELS",
            "upload_type": "resumable",
            "share_to_feed": "true",
            "caption": caption,
            "access_token": token,
        })
        container = init["id"]
        upload_uri = init.get("uri") or f"{_RUPLOAD}/ig-api-upload/{_version()}/{container}"
        blob = path.read_bytes()
        _call(upload_uri, data=blob, method="POST", timeout=600, headers={
            "Authorization": f"OAuth {token}",
            "offset": "0",
            "file_size": str(len(blob)),
            "Content-Type": "application/octet-stream",
        })

    _wait_finished(container, token)
    media_id = _graph(f"{ig_id}/media_publish", {
        "creation_id": container, "access_token": token,
    })["id"]
    info = _graph(media_id, {"fields": "permalink", "access_token": token}, method="GET")
    return info.get("permalink") or f"https://www.instagram.com/ (media id {media_id})"


def publish_facebook(draft: dict[str, Any], media: dict[str, Any] | None = None) -> str:
    """Publish the draft's FB variant (text / photo / reel); returns the post URL."""
    if dry_run():
        return "(dry-run: not actually posted)"
    message = (draft.get("variants") or {}).get("facebook", "")
    token, page_id, _ = _creds()

    if media and media.get("path"):
        path = _media_path(media, "Facebook media record is not ready")
        if media["type"] == "image":
            body, ctype = _multipart(
                {"message": message, "access_token": token}, "source", path
            )
            resp = _call(f"{_GRAPH}/{_version()}/{page_id}/photos", data=body,
                         method="POST", timeout=300, headers={"Content-Type": ctype})
            return f"https://www.facebook.com/{resp.get('post_id') or resp['id']}"
        # video → Page Reel: start → binary upload → finish
        start = _graph(f"{page_id}/video_reels", {
            "upload_phase": "start", "access_token": token,
        })
        video_id = start["video_id"]
        upload_url = start.get("upload_url") or f"{_RUPLOAD}/video-upload/{_version()}/{video_id}"
        blob = path.read_bytes()
        _call(upload_url, data=blob, method="POST", timeout=600, headers={
            "Authorization": f"OAuth {token}",
            "offset": "0",
            "file_size": str(len(blob)),
        })
        _graph(f"{page_id}/video_reels", {
            "upload_phase": "finish",
            "video_id": video_id,
            "video_state": "PUBLISHED",
            "description": message,
            "access_token": token,
        }, timeout=300)
        return f"https://www.facebook.com/reel/{video_id}"

    if not message.strip():
        raise MetaPublishError("Facebook draft has neither text nor media — nothing to post.")
    resp = _graph(f"{page_id}/feed", {"message": message, "access_token": token})
    return f"https://www.facebook.com/{resp['id']}"


def _main() -> int:
    """--check: report credential state (never posts). Clean message, no traceback."""
    try:
        print(verify_auth())
    except MetaPublishError as exc:
        print(f"publish_meta: {exc}", file=sys.stderr)
        return 1
    if not (env("META_MEDIA_BASE_URL", required=False) or "").strip():
        print("note: META_MEDIA_BASE_URL unset — IG image posts will fail until "
              "data/<vertical>/media/ is served publicly (reels are unaffected).")
    return 0


if __name__ == "__main__":
    sys.exit(_main())
