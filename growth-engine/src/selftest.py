"""Isolated self-tests — verify each process on its own before wiring them together.

Run one layer at a time (see TASK.md):

    python -m src.selftest config      # config + env sanity, no network
    python -m src.selftest platforms   # platform registry sanity, no network
    python -m src.selftest generate    # Claude drafting (needs ANTHROPIC_API_KEY)
    python -m src.selftest telegram    # send a test message (needs Telegram vars)
    python -m src.selftest x           # verify X auth, does NOT post (needs X vars)
    python -m src.selftest all         # run every check in order, stop on first failure

Each check prints a clear PASS/FAIL and returns a non-zero exit code on failure, so it's
safe to gate a TASK.md step on it.
"""

from __future__ import annotations

import sys

from . import settings
from .settings import MissingSetting, active_cadence, dry_run, env, strategy


def _ok(msg: str) -> None:
    print(f"  ✅ {msg}")


def _fail(msg: str) -> bool:
    print(f"  ❌ {msg}")
    return False


def check_config() -> bool:
    print("• config")
    try:
        s = strategy()
        cad = active_cadence()
    except Exception as exc:
        return _fail(f"could not load config: {exc}")
    if s["model"]["id"] != "claude-opus-4-8":
        _ok(f"model override in use: {s['model']['id']}")
    _ok(f"vertical: {settings.vertical()} (config: {settings.CONFIG_PATH.name}, "
        f"data: {settings.data_dir().relative_to(settings.ROOT)})")
    _ok(f"offer: {s['brand']['offer'][:60]}…")
    _ok(f"pillars: {', '.join(p['key'] for p in s['pillars'])}")
    _ok(f"cadence '{strategy()['cadence']['active']}': "
        f"{cad['runs_per_day']} run(s)/day × {cad['drafts_per_run']} drafts "
        f"→ {cad['platforms_per_draft']}")
    return True


def check_platforms() -> bool:
    print("• platforms (registry)")
    from . import platforms  # imported lazily so `config` stays independent of it

    try:
        reg = platforms.registry()
    except Exception as exc:
        return _fail(f"registry failed to load: {exc}")
    if not reg:
        return _fail("no enabled platforms in config")
    for name, desc in reg.items():
        for key in ("label", "writing"):
            if not desc.get(key):
                return _fail(f"'{name}' is missing '{key}'")
        # Repo rule: X is the only platform allowed to auto-post (LinkedIn/Reddit ToS).
        if desc["delivery"] == "auto" and name != "x":
            return _fail(f"'{name}' has delivery: auto — only x may auto-post")
    if "x" in reg and reg["x"]["char_limit"] != 280:
        return _fail(f"x char_limit must be 280, got {reg['x']['char_limit']}")
    _ok(f"enabled: {', '.join(platforms.enabled_platforms())}")
    _ok(f"auto: {', '.join(platforms.auto_platforms()) or '(none)'} — "
        f"assisted: {', '.join(platforms.assisted_platforms()) or '(none)'}")
    return True


def check_generate() -> bool:
    print("• generate (Claude)")
    try:
        env("ANTHROPIC_API_KEY")
    except MissingSetting as exc:
        return _fail(str(exc))
    from . import generate  # imported lazily so `config` works without the SDK installed

    try:
        draft = generate.generate_draft(active_cadence()["platforms_per_draft"])
    except Exception as exc:
        return _fail(f"generation failed: {exc}")
    if not draft["variants"]:
        return _fail("draft came back with no variants")
    _ok(f"pillar={draft['pillar']}  topic={draft['topic']}")
    for platform, text in draft["variants"].items():
        flag = " (over 280!)" if platform == "x" and len(text) > 280 else ""
        _ok(f"[{platform}] {len(text)} chars{flag}")
        print(f"      {text[:160]}{'…' if len(text) > 160 else ''}")
    return True


def check_telegram() -> bool:
    print("• telegram")
    import asyncio

    try:
        token = env("TELEGRAM_BOT_TOKEN")
        chat_id = int(env("TELEGRAM_CHAT_ID"))
    except MissingSetting as exc:
        return _fail(str(exc))
    from telegram import Bot

    async def _send() -> None:
        bot = Bot(token)
        async with bot:
            me = await bot.get_me()
            await bot.send_message(chat_id, "🧪 Growth Engine self-test: Telegram is wired up.")
            return me.username

    try:
        username = asyncio.run(_send())
    except Exception as exc:
        return _fail(f"telegram failed (did you message the bot first?): {exc}")
    _ok(f"sent test message via @{username} to chat {chat_id}")
    return True


def check_x() -> bool:
    print("• x (auth only — does NOT post)")
    try:
        env("X_API_KEY"); env("X_API_SECRET")
        env("X_ACCESS_TOKEN"); env("X_ACCESS_TOKEN_SECRET")
    except MissingSetting as exc:
        return _fail(str(exc))
    import tweepy

    try:
        client = tweepy.Client(
            consumer_key=env("X_API_KEY"),
            consumer_secret=env("X_API_SECRET"),
            access_token=env("X_ACCESS_TOKEN"),
            access_token_secret=env("X_ACCESS_TOKEN_SECRET"),
        )
        me = client.get_me()
    except Exception as exc:
        return _fail(
            f"X auth failed: {exc}\n"
            f"      (Common cause: access token generated before enabling Read+Write — "
            f"regenerate it.)"
        )
    _ok(f"authenticated as @{me.data.username}")
    print("      To test an actual post safely, run the bot with GROWTH_ENGINE_DRY_RUN=1.")
    return True


CHECKS = {
    "config": check_config,
    "platforms": check_platforms,
    "generate": check_generate,
    "telegram": check_telegram,
    "x": check_x,
}
ORDER = ["config", "platforms", "generate", "telegram", "x"]


def main(argv: list[str]) -> int:
    which = argv[1] if len(argv) > 1 else "all"
    if dry_run():
        print("(GROWTH_ENGINE_DRY_RUN is set)\n")
    names = ORDER if which == "all" else [which]
    if which != "all" and which not in CHECKS:
        print(f"Unknown check '{which}'. Choose from: {', '.join(ORDER)}, all")
        return 2
    for name in names:
        if not CHECKS[name]():
            print(f"\nStopped at '{name}'. Fix it, then re-run.")
            return 1
        print()
    print("All requested checks passed. ✅")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
