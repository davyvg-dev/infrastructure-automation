"""Telegram channel for the receptionist.

A long-running polling bot: every text message a customer sends becomes a receptionist
turn, and the reply goes straight back. No public URL needed.

    python -m app.channels.telegram_bot

Note: this uses its OWN bot token (the business's receptionist), separate from the
growth-engine approval bot. Create a second bot with @BotFather.
"""

from __future__ import annotations

import asyncio

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from .. import sessions
from ..settings import ensure_dirs, env


async def on_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    sessions.reset("telegram", str(update.effective_chat.id))
    await update.message.reply_text(sessions.greeting())


async def on_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_chat.id)
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    reply = await asyncio.to_thread(sessions.respond, "telegram", user_id, update.message.text)
    await update.message.reply_text(reply)


def main() -> None:
    ensure_dirs()
    app = Application.builder().token(env("TELEGRAM_BOT_TOKEN")).build()
    app.add_handler(CommandHandler("start", on_start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_message))
    print("Receptionist Telegram bot running. Message it to test.")
    app.run_polling()


if __name__ == "__main__":
    main()
