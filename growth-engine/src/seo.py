"""Search Console: what klantkraan.nl actually ranks for, as a report worth reading.

The site has been live for months with no view of its own search performance. Cloudflare
Web Analytics counts visits; it cannot say which query brought them, what we nearly rank
for, or which page Google shows and nobody clicks. Search Console is the only source for
that, it is free, and it adds no visitor tracking -- this reads Google's data about us, so
there is no cookie banner, no new sub-processor and nothing to add to the DPA.

Auth is a service account, not a browser login, because this runs unattended on a timer.
Google's own client libraries pull in a large dependency tree to do one thing: sign a JWT
and swap it for an access token. That is ~30 lines here (`_access_token`), so the only new
dependency is `cryptography` for the RS256 signature.

Verified against current Search Console API docs via context7 (2026-07-29,
/websites/developers_google_webmaster-tools_v1): POST to
https://www.googleapis.com/webmasters/v3/sites/{siteUrl}/searchAnalytics/query with
{startDate, endDate, dimensions[], rowLimit} and an OAuth bearer token.

Setup (once -- see docs/SETUP.md):
  GSC_SERVICE_ACCOUNT_JSON  path to the service-account key file
  GSC_SITE_URL              the property, e.g. https://klantkraan.nl/

Run:
  python -m src.seo report            # print the last 28 days
  python -m src.seo report --send     # print it and push it to Telegram
  python -m src.seo report --days 7
"""

from __future__ import annotations

import argparse
import base64
import json
import sys
import time
import urllib.parse
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import httpx

from .settings import MissingSetting, env

API = "https://www.googleapis.com/webmasters/v3/sites"
TOKEN_URL = "https://oauth2.googleapis.com/token"
SCOPE = "https://www.googleapis.com/auth/webmasters.readonly"

# Search Console finalises a day's data two to three days late. Asking for yesterday
# returns a half-empty row that reads like a traffic collapse, so the window ends here.
LAG_DAYS = 3


# --- Auth ---------------------------------------------------------------------------------


def _b64(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def _service_account() -> dict[str, Any]:
    path = Path(env("GSC_SERVICE_ACCOUNT_JSON"))  # type: ignore[arg-type]
    if not path.exists():
        raise MissingSetting(
            f"GSC_SERVICE_ACCOUNT_JSON points at {path}, which does not exist. "
            "Download the key from the Google Cloud service account and put it there."
        )
    return json.loads(path.read_text(encoding="utf-8"))


def _access_token() -> str:
    """Sign a JWT with the service-account key and swap it for an access token.

    This is the whole of what google-auth would do for us here.
    """
    # Config first, then the dependency: an unconfigured founder should be told what to set
    # up, not what to pip install.
    account = _service_account()
    try:
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import padding
    except ModuleNotFoundError as exc:  # pragma: no cover - install-time problem
        raise MissingSetting(
            "The `cryptography` package is required to sign the Search Console JWT. "
            "Run: pip install -r requirements.txt"
        ) from exc

    now = int(time.time())
    header = _b64(json.dumps({"alg": "RS256", "typ": "JWT"}).encode())
    claims = _b64(
        json.dumps(
            {
                "iss": account["client_email"],
                "scope": SCOPE,
                "aud": TOKEN_URL,
                "iat": now,
                "exp": now + 3600,
            }
        ).encode()
    )
    signing_input = f"{header}.{claims}".encode()
    key = serialization.load_pem_private_key(account["private_key"].encode(), password=None)
    signature = key.sign(signing_input, padding.PKCS1v15(), hashes.SHA256())  # type: ignore[union-attr]
    assertion = f"{header}.{claims}.{_b64(signature)}"

    resp = httpx.post(
        TOKEN_URL,
        data={
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "assertion": assertion,
        },
        timeout=30,
    )
    if resp.status_code >= 400:
        raise RuntimeError(
            f"Google refused the service-account token ({resp.status_code}): {resp.text[:300]}"
        )
    return resp.json()["access_token"]


# --- Query --------------------------------------------------------------------------------


def _window(days: int, *, offset: int = 0) -> tuple[str, str]:
    """A closed date window ending `LAG_DAYS` ago. `offset` steps back whole windows, so
    offset=1 is the equally long period before this one -- what the deltas compare against."""
    end = date.today() - timedelta(days=LAG_DAYS + offset * days)
    start = end - timedelta(days=days - 1)
    return start.isoformat(), end.isoformat()


def query(
    token: str,
    *,
    start: str,
    end: str,
    dimensions: list[str] | None = None,
    limit: int = 25,
) -> dict[str, Any]:
    site = env("GSC_SITE_URL")
    url = f"{API}/{urllib.parse.quote(site, safe='')}/searchAnalytics/query"  # type: ignore[arg-type]
    body: dict[str, Any] = {"startDate": start, "endDate": end, "rowLimit": limit}
    if dimensions:
        body["dimensions"] = dimensions
    resp = httpx.post(url, json=body, headers={"Authorization": f"Bearer {token}"}, timeout=60)
    if resp.status_code == 403:
        raise RuntimeError(
            f"Search Console refused access to {site}. Add the service account "
            f"({_service_account()['client_email']}) as a user on that property in "
            "Search Console -> Settings -> Users and permissions."
        )
    if resp.status_code >= 400:
        raise RuntimeError(f"Search Console query failed ({resp.status_code}): {resp.text[:300]}")
    return resp.json()


def _totals(rows: list[dict[str, Any]]) -> dict[str, float]:
    clicks = sum(r.get("clicks", 0) for r in rows)
    impressions = sum(r.get("impressions", 0) for r in rows)
    # Position has to be weighted by impressions; averaging the per-row averages would let
    # a query with two impressions count as much as one with two thousand.
    weighted = sum(r.get("position", 0) * r.get("impressions", 0) for r in rows)
    return {
        "clicks": clicks,
        "impressions": impressions,
        "position": (weighted / impressions) if impressions else 0.0,
        "ctr": (clicks / impressions * 100) if impressions else 0.0,
    }


# --- Report -------------------------------------------------------------------------------


def _delta(now: float, before: float, *, lower_is_better: bool = False, digits: int = 1) -> str:
    """Change against the previous window. A number with nothing beside it is not a signal."""
    if not before:
        return ""
    diff = now - before
    if abs(diff) < (0.5 if digits == 0 else 0.05):
        return "  (flat)"
    better = (diff < 0) if lower_is_better else (diff > 0)
    return f"  ({'+' if diff > 0 else ''}{diff:.{digits}f}, {'better' if better else 'worse'})"


def format_report(
    *,
    start: str,
    end: str,
    days: int,
    queries: list[dict[str, Any]],
    pages: list[dict[str, Any]],
    prev: list[dict[str, Any]],
) -> str:
    """Pure: rows in, report out. Split from the fetch so the selftest can check the shape
    of the thing the founder actually reads without a network or a key."""
    now_t = _totals(queries)
    prev_t = _totals(prev)

    lines = [
        f"Klantkraan search — {start} to {end} ({days} days)",
        "",
        f"clicks       {now_t['clicks']:>6.0f}"
        f"{_delta(now_t['clicks'], prev_t['clicks'], digits=0)}",
        f"impressions  {now_t['impressions']:>6.0f}"
        f"{_delta(now_t['impressions'], prev_t['impressions'], digits=0)}",
        f"ctr          {now_t['ctr']:>6.1f}%{_delta(now_t['ctr'], prev_t['ctr'])}",
        f"avg position {now_t['position']:>6.1f}"
        f"{_delta(now_t['position'], prev_t['position'], lower_is_better=True)}",
    ]

    if not queries:
        lines += ["", "No search data in this window. The site is not being shown yet."]
        return "\n".join(lines)

    top = sorted(queries, key=lambda r: (-r.get("clicks", 0), -r.get("impressions", 0)))[:8]
    lines += ["", "TOP QUERIES"]
    for row in top:
        lines.append(
            f"  {row['keys'][0][:44]:<44} pos {row.get('position', 0):>4.1f}  "
            f"{row.get('clicks', 0):>3.0f} clicks  {row.get('impressions', 0):>5.0f} impr"
        )

    # Positions 11-20: page two. These are the cheapest wins on the whole site -- Google
    # already thinks the page is relevant, it is just below the fold of results.
    near = [r for r in queries if 10 < r.get("position", 999) <= 20]
    near.sort(key=lambda r: -r.get("impressions", 0))
    if near:
        lines += ["", "ONE PAGE OFF (position 11-20, most-seen first)"]
        for row in near[:8]:
            lines.append(
                f"  {row['keys'][0][:44]:<44} pos {row.get('position', 0):>4.1f}  "
                f"{row.get('impressions', 0):>5.0f} impr"
            )

    # Shown often, never clicked: the ranking is fine and the title or description is not.
    ignored = [r for r in queries if r.get("impressions", 0) >= 20 and not r.get("clicks", 0)]
    ignored.sort(key=lambda r: -r.get("impressions", 0))
    if ignored:
        lines += ["", "SEEN BUT NOT CLICKED (rewrite the title/description)"]
        for row in ignored[:5]:
            lines.append(
                f"  {row['keys'][0][:44]:<44} pos {row.get('position', 0):>4.1f}  "
                f"{row.get('impressions', 0):>5.0f} impr"
            )

    if pages:
        best = sorted(pages, key=lambda r: -r.get("clicks", 0))[:5]
        lines += ["", "TOP PAGES"]
        for row in best:
            path = urllib.parse.urlparse(row["keys"][0]).path or "/"
            lines.append(
                f"  {path[:44]:<44} {row.get('clicks', 0):>3.0f} clicks  "
                f"{row.get('impressions', 0):>5.0f} impr"
            )

    return "\n".join(lines)


def build_report(days: int = 28) -> str:
    """Fetch the window and the one before it, then format. Two windows because a number
    with nothing to compare it to tells the founder nothing."""
    token = _access_token()
    start, end = _window(days)
    prev_start, prev_end = _window(days, offset=1)
    return format_report(
        start=start,
        end=end,
        days=days,
        queries=query(token, start=start, end=end, dimensions=["query"], limit=200).get("rows", []),
        pages=query(token, start=start, end=end, dimensions=["page"], limit=100).get("rows", []),
        prev=query(token, start=prev_start, end=prev_end, dimensions=["query"], limit=200).get(
            "rows", []
        ),
    )


def send(text: str) -> bool:
    """Push the report to the founder's Telegram. Same seam the drafts use."""
    import asyncio

    from telegram import Bot

    async def _go() -> None:
        bot = Bot(env("TELEGRAM_BOT_TOKEN"))
        async with bot:
            await bot.send_message(
                int(env("TELEGRAM_CHAT_ID")), f"```\n{text}\n```", parse_mode="MarkdownV2"
            )

    asyncio.run(_go())
    return True


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="python -m src.seo", description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_report = sub.add_parser("report", help="Search performance for the last N days.")
    p_report.add_argument("--days", type=int, default=28)
    p_report.add_argument("--send", action="store_true", help="Also push it to Telegram.")
    args = parser.parse_args(argv)

    if args.cmd == "report":
        try:
            text = build_report(args.days)
        except (MissingSetting, RuntimeError) as exc:
            # Surface it: a report nobody can build must not fail silently on a timer.
            print(f"seo: {exc}", file=sys.stderr)
            return 1
        print(text)
        if args.send:
            send(text)
            print("\n(sent to Telegram)")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
