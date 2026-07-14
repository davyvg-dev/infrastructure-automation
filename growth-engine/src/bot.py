"""Telegram approval bot + scheduler.

One long-running process that:
  - schedules generation runs per the active cadence,
  - sends each draft with one-tap ✅ / ✏️ / ❌ buttons,
  - auto-posts the X variant on approval and hands you LinkedIn/Reddit to paste.

Run it with `python -m src.run`.
"""

from __future__ import annotations

import asyncio
import datetime as dt
from zoneinfo import ZoneInfo

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from . import buildlog, formatting, generate, platforms, store
from .publish_x import post as post_to_x
from .settings import active_cadence, env, strategy


# --------------------------------------------------------------------------- #
# Sending drafts
# --------------------------------------------------------------------------- #

def _keyboard(draft_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Approve", callback_data=f"approve:{draft_id}"),
        InlineKeyboardButton("✏️ Rewrite", callback_data=f"rewrite:{draft_id}"),
        InlineKeyboardButton("❌ Skip", callback_data=f"skip:{draft_id}"),
    ]])


async def _send_draft(app: Application, chat_id: int, draft: dict) -> None:
    store.save_draft(draft)
    await app.bot.send_message(
        chat_id=chat_id,
        text=formatting.preview(draft),
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=_keyboard(draft["id"]),
    )


# --------------------------------------------------------------------------- #
# Scheduled jobs
# --------------------------------------------------------------------------- #

async def generation_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = context.job.chat_id
    cadence = active_cadence()
    platforms = cadence["platforms_per_draft"]
    for _ in range(int(cadence["drafts_per_run"])):
        try:
            draft = await asyncio.to_thread(generate.generate_draft, platforms)
            await _send_draft(context.application, chat_id, draft)
        except Exception as exc:  # keep the loop alive; report the failure
            await context.bot.send_message(chat_id, f"⚠️ Generation failed: {exc}")


async def reddit_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = context.job.chat_id
    try:
        draft = await asyncio.to_thread(generate.generate_draft, ["reddit"])
        await _send_draft(context.application, chat_id, draft)
    except Exception as exc:
        await context.bot.send_message(chat_id, f"⚠️ Reddit generation failed: {exc}")


def _run_times(runs_per_day: int) -> list[dt.time]:
    """Evenly spread run times across the waking window (avoids quiet hours)."""
    cad = strategy()["cadence"]
    tz = ZoneInfo(cad["timezone"])
    start, end = int(cad["quiet_hours_end"]), int(cad["quiet_hours_start"])
    span = max(1, end - start)  # e.g. 8:00 -> 22:00 = 14 hours
    if runs_per_day <= 1:
        offsets = [span // 2]
    else:
        step = span / runs_per_day
        offsets = [step * (i + 0.5) for i in range(runs_per_day)]
    times = []
    for off in offsets:
        hour = start + int(off)
        minute = int((off - int(off)) * 60)
        times.append(dt.time(hour=min(hour, 23), minute=minute, tzinfo=tz))
    return times


def schedule_jobs(app: Application, chat_id: int) -> None:
    jq = app.job_queue
    for job in jq.jobs():
        job.schedule_removal()

    cadence = active_cadence()
    for i, t in enumerate(_run_times(int(cadence["runs_per_day"]))):
        jq.run_daily(generation_job, time=t, chat_id=chat_id, name=f"gen-{i}")

    # Reddit runs on its own timer — only in verticals where it's enabled.
    if "reddit" not in platforms.enabled_platforms():
        return
    every_days = int(strategy()["cadence"].get("reddit_every_days", 3))
    tz = ZoneInfo(strategy()["cadence"]["timezone"])
    jq.run_repeating(
        reddit_job,
        interval=dt.timedelta(days=every_days),
        first=dt.datetime.now(tz).replace(hour=11, minute=0, second=0)
        + dt.timedelta(days=1),
        chat_id=chat_id,
        name="reddit",
    )


# --------------------------------------------------------------------------- #
# Commands
# --------------------------------------------------------------------------- #

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    schedule_jobs(context.application, chat_id)
    cad = strategy()["cadence"]
    await update.message.reply_text(
        f"Growth Engine online. Cadence: {cad['active']} "
        f"({active_cadence()['runs_per_day']} run(s)/day, "
        f"{active_cadence()['drafts_per_run']} drafts each).\n\n"
        f"Commands: /now (generate a draft immediately), /cadence, /help"
    )


async def cmd_now(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Generating a draft…")
    platforms = active_cadence()["platforms_per_draft"]
    try:
        draft = await asyncio.to_thread(generate.generate_draft, platforms)
        await _send_draft(context.application, update.effective_chat.id, draft)
    except Exception as exc:
        await update.message.reply_text(f"⚠️ Generation failed: {exc}")


async def cmd_buildlog(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Reading your recent commits…")
    platforms = active_cadence()["platforms_per_draft"]
    try:
        draft = await asyncio.to_thread(buildlog.build_draft, platforms)
    except Exception as exc:
        await update.message.reply_text(f"⚠️ Build-log failed: {exc}")
        return
    if draft is None:
        await update.message.reply_text("No new commits since your last build-log. Ship something first 🙂")
        return
    await update.message.reply_text(
        f"From {len(draft.get('source_commits', []))} commit(s):"
    )
    await _send_draft(context.application, update.effective_chat.id, draft)


async def cmd_cadence(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    cad = strategy()["cadence"]
    profiles = ", ".join(cad["profiles"].keys())
    await update.message.reply_text(
        f"Active cadence: *{cad['active']}*\nProfiles available: {profiles}\n"
        f"Edit `config/content_strategy.yaml` (cadence.active) and /start to reschedule.",
        parse_mode=ParseMode.MARKDOWN,
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "/now — generate a draft now\n"
        "/buildlog — draft a build-in-public post from your recent git commits\n"
        "/cadence — show cadence\n"
        "/start — (re)schedule jobs\n\n"
        "On each draft: ✅ approve (auto-posts X, hands you LinkedIn/Reddit to paste), "
        "✏️ rewrite (then send me a note), ❌ skip."
    )


# --------------------------------------------------------------------------- #
# Button + note handling
# --------------------------------------------------------------------------- #

async def on_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    action, draft_id = query.data.split(":", 1)
    draft = store.get_draft(draft_id)
    if draft is None:
        await query.edit_message_reply_markup(reply_markup=None)
        return

    if action == "skip":
        store.update_draft(draft_id, status="skipped")
        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text("❌ Skipped.")
    elif action == "rewrite":
        context.chat_data["awaiting_note"] = draft_id
        await query.message.reply_text(
            "✏️ Send me a one-line note and I'll rewrite this draft "
            "(e.g. 'punchier hook', 'make it Dutch', 'shorter')."
        )
    elif action == "approve":
        await query.edit_message_reply_markup(reply_markup=None)
        await _approve(context, query.message.chat_id, draft)


# Publisher per auto-delivery platform. X is the only one wired up today; a new
# `delivery: auto` platform in config needs an entry here before it can post.
_PUBLISHERS = {"x": post_to_x}


async def _approve(context: ContextTypes.DEFAULT_TYPE, chat_id: int, draft: dict) -> None:
    store.update_draft(draft["id"], status="approved", approved_at=store.now_iso())
    variants = draft["variants"]

    # Auto-delivery platforms: post via API.
    for platform in platforms.auto_platforms():
        if platform not in variants:
            continue
        publisher = _PUBLISHERS.get(platform)
        if publisher is None:  # config says auto, but no publisher exists — surface it
            await context.bot.send_message(
                chat_id,
                f"⚠️ No publisher wired up for {platform}. Here it is to post by hand:",
            )
            await context.bot.send_message(chat_id, variants[platform])
            continue
        result = await asyncio.to_thread(publisher, variants[platform])
        if result.ok:
            store.update_draft(draft["id"], status="posted", **{f"{platform}_url": result.url})
            await context.bot.send_message(
                chat_id, f"✅ Posted to {platform.title()}: {result.url}"
            )
        else:
            await context.bot.send_message(
                chat_id,
                f"⚠️ {platform.title()} post failed ({result.error}). "
                f"Here it is to post by hand:",
            )
            await context.bot.send_message(chat_id, variants[platform])

    # Assisted-delivery platforms: hand over clean text to paste.
    for platform in platforms.assisted_platforms():
        if platform in variants:
            await context.bot.send_message(chat_id, f"⬇️ {platform.title()} — copy & paste:")
            await context.bot.send_message(chat_id, variants[platform])


async def on_note(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    draft_id = context.chat_data.pop("awaiting_note", None)
    if not draft_id:
        return  # not a rewrite note; ignore
    draft = store.get_draft(draft_id)
    if draft is None:
        return
    note = update.message.text.strip()
    await update.message.reply_text("Rewriting…")
    new_variants = {}
    for platform, text in draft["variants"].items():
        try:
            new_variants[platform] = await asyncio.to_thread(
                generate.regenerate_variant, draft, platform, note
            )
        except Exception as exc:
            new_variants[platform] = text
            await update.message.reply_text(f"⚠️ Couldn't rewrite {platform}: {exc}")
    draft = store.update_draft(draft_id, variants=new_variants) or draft
    await update.message.reply_text(
        formatting.preview(draft),
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=_keyboard(draft_id),
    )


# --------------------------------------------------------------------------- #
# App wiring
# --------------------------------------------------------------------------- #

async def _post_init(app: Application) -> None:
    chat_id = int(env("TELEGRAM_CHAT_ID"))
    schedule_jobs(app, chat_id)
    await app.bot.send_message(
        chat_id,
        "🚀 Growth Engine started and scheduled. Send /now for a draft, or wait for the "
        "next scheduled run.",
    )


def build_app() -> Application:
    token = env("TELEGRAM_BOT_TOKEN")
    app = Application.builder().token(token).post_init(_post_init).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("now", cmd_now))
    app.add_handler(CommandHandler("buildlog", cmd_buildlog))
    app.add_handler(CommandHandler("cadence", cmd_cadence))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CallbackQueryHandler(on_button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_note))
    return app
