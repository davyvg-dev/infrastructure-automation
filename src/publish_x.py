"""X (Twitter) posting via the v2 API using OAuth 1.0a user context.

The free tier allows a limited number of writes per month, which is plenty for a
personal brand. If posting fails (rate limit, auth), the error is surfaced so the bot
can tell you and fall back to hand-posting.
"""

from __future__ import annotations

from dataclasses import dataclass

import tweepy

from .settings import dry_run, env


@dataclass
class PostResult:
    ok: bool
    url: str | None = None
    error: str | None = None


def _client() -> tweepy.Client:
    return tweepy.Client(
        consumer_key=env("X_API_KEY"),
        consumer_secret=env("X_API_SECRET"),
        access_token=env("X_ACCESS_TOKEN"),
        access_token_secret=env("X_ACCESS_TOKEN_SECRET"),
    )


def post(text: str) -> PostResult:
    if dry_run():
        return PostResult(ok=True, url="(dry-run: not actually posted)")
    if len(text) > 280:
        return PostResult(ok=False, error=f"Post is {len(text)} chars (X limit is 280).")
    try:
        client = _client()
        resp = client.create_tweet(text=text)
        tweet_id = resp.data["id"]
        return PostResult(ok=True, url=f"https://x.com/i/web/status/{tweet_id}")
    except Exception as exc:  # tweepy raises several types; surface any of them
        return PostResult(ok=False, error=str(exc))
