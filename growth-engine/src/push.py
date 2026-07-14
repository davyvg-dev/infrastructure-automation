"""Headless generation + push (no approval buttons).

For when you don't have an always-on host: run this on a schedule (e.g. GitHub Actions
cron). It generates a batch of drafts and pushes them to Telegram as plain, copy-ready
messages. You review on your phone and post manually — including X (no auto-post here,
since there's no long-running process to handle button taps).

    python -m src.push
"""

from __future__ import annotations

import asyncio

from telegram import Bot

from . import generate, store
from .settings import active_cadence, ensure_dirs, env


async def _main() -> None:
    ensure_dirs()
    bot = Bot(env("TELEGRAM_BOT_TOKEN"))
    chat_id = int(env("TELEGRAM_CHAT_ID"))
    cadence = active_cadence()
    platforms = cadence["platforms_per_draft"]

    async with bot:
        await bot.send_message(chat_id, "🗒️ Today's drafts (review & post manually):")
        for _ in range(int(cadence["drafts_per_run"])):
            draft = await asyncio.to_thread(generate.generate_draft, platforms)
            store.save_draft(draft)
            await bot.send_message(
                chat_id, f"— {draft['pillar']} · {draft['topic']} —"
            )
            for record in draft.get("media", []):
                if record["type"] == "image":
                    with open(record["path"], "rb") as fh:
                        await bot.send_photo(chat_id, fh, caption=f"🖼 {record['aspect']}")
            for platform, text in draft["variants"].items():
                await bot.send_message(chat_id, f"[{platform}]")
                await bot.send_message(chat_id, text)


if __name__ == "__main__":
    asyncio.run(_main())
