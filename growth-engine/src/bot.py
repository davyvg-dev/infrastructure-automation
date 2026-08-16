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
import logging
from zoneinfo import ZoneInfo

import httpx
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
from telegram.request import HTTPXRequest

from . import (
    buildlog,
    formatting,
    generate,
    media,
    newsletter,
    pagekit,
    platforms,
    publish_buffer,
    publish_meta,
    publish_tiktok,
    store,
    verify,
)
from .publish_x import post as post_to_x
from .settings import active_cadence, data_dir, dry_run, env, strategy

# --------------------------------------------------------------------------- #
# Sending drafts
# --------------------------------------------------------------------------- #


def _keyboard(draft_id: str, pending_reel: bool = False) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton("✅ Approve", callback_data=f"approve:{draft_id}"),
            InlineKeyboardButton("✏️ Rewrite", callback_data=f"rewrite:{draft_id}"),
            InlineKeyboardButton("❌ Skip", callback_data=f"skip:{draft_id}"),
        ]
    ]
    if pending_reel:
        rows.append(
            [InlineKeyboardButton("🎬 Send recording → reel", callback_data=f"record:{draft_id}")]
        )
    return InlineKeyboardMarkup(rows)


async def _send_media_previews(app: Application, chat_id: int, draft: dict) -> None:
    for record in draft.get("media", []):
        if record["type"] == "image":
            with open(record["path"], "rb") as fh:
                await app.bot.send_photo(
                    chat_id, fh, caption=f"🖼 card ({record['aspect']}) — save & attach"
                )
        elif record["type"] == "video" and record["status"] == "ready":
            with open(record["path"], "rb") as fh:
                await app.bot.send_video(chat_id, fh, caption="🎬 reel — save & attach")


def _approval_message(draft: dict) -> str:
    """The right approval preview per draft kind (posts vs the nieuwsbrief)."""
    if draft.get("kind") == newsletter.KIND:
        return formatting.newsletter_preview(draft)
    return formatting.preview(draft)


async def _deliver_draft(app: Application, chat_id: int, draft: dict) -> None:
    if draft.get("kind") == newsletter.KIND:
        # The .md the founder is approving rides along as a document; the approval
        # message (with buttons) stays last in the chat, same as media previews below.
        await app.bot.send_document(
            chat_id,
            document=newsletter.markdown(draft).encode("utf-8"),
            filename=newsletter.filename(draft),
            caption="📰 nieuwsbrief-editie (.md)",
        )
    else:
        # Media previews first, so the approval message (with buttons) stays last.
        await _send_media_previews(app, chat_id, draft)
    await app.bot.send_message(
        chat_id=chat_id,
        text=_approval_message(draft),
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=_keyboard(draft["id"], formatting.pending_reel(draft)),
    )
    # Marks the draft as having reached Telegram; undelivered ones are resent on startup.
    store.update_draft(draft["id"], delivered_at=store.now_iso())


async def _send_draft(app: Application, chat_id: int, draft: dict) -> None:
    # Pre-approval verify pass (LLM judge + one auto-revise; see src/verify.py, and
    # src/newsletter.py for the nieuwsbrief's own criteria).
    # Fail-open by design: check_and_revise never raises and never drops a draft —
    # a failing or unchecked draft arrives flagged via formatting.verify_flags.
    checker = (
        newsletter.check_and_revise
        if draft.get("kind") == newsletter.KIND
        else verify.check_and_revise
    )
    draft = await asyncio.to_thread(checker, draft)
    store.save_draft(draft)
    await _deliver_draft(app, chat_id, draft)


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


async def newsletter_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = context.job.chat_id
    try:
        existing = newsletter.open_edition_draft()
        if existing:  # /nieuwsbrief (or an earlier run) already drafted this edition
            await context.bot.send_message(
                chat_id,
                f"📰 Nieuwsbrief {existing['edition']} already has a draft "
                f"({existing['status']}); not drafting another. /nieuwsbrief forces one.",
            )
            return
        draft = await asyncio.to_thread(newsletter.generate_newsletter)
        await _send_draft(context.application, chat_id, draft)
    except Exception as exc:
        await context.bot.send_message(chat_id, f"⚠️ Nieuwsbrief generation failed: {exc}")


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

    # Monthly nieuwsbrief draft: the 1st of each month, mid-morning. Approval only
    # writes the .md — sending stays a separate founder command (kk nieuwsbrief send).
    tz = ZoneInfo(strategy()["cadence"]["timezone"])
    jq.run_monthly(
        newsletter_job,
        when=dt.time(hour=9, minute=30, tzinfo=tz),
        day=1,
        chat_id=chat_id,
        name="newsletter",
    )

    # Reddit runs on its own timer — only in verticals where it's enabled.
    if "reddit" not in platforms.enabled_platforms():
        return
    every_days = int(strategy()["cadence"].get("reddit_every_days", 3))
    tz = ZoneInfo(strategy()["cadence"]["timezone"])
    jq.run_repeating(
        reddit_job,
        interval=dt.timedelta(days=every_days),
        first=dt.datetime.now(tz).replace(hour=11, minute=0, second=0) + dt.timedelta(days=1),
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
        await update.message.reply_text(
            "No new commits since your last build-log. Ship something first 🙂"
        )
        return
    await update.message.reply_text(f"From {len(draft.get('source_commits', []))} commit(s):")
    await _send_draft(context.application, update.effective_chat.id, draft)


async def cmd_nieuwsbrief(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Manual trigger for a nieuwsbrief draft (the monthly job's /now equivalent)."""
    await update.message.reply_text("Drafting the monthly nieuwsbrief…")
    try:
        draft = await asyncio.to_thread(newsletter.generate_newsletter)
        await _send_draft(context.application, update.effective_chat.id, draft)
    except Exception as exc:
        await update.message.reply_text(f"⚠️ Nieuwsbrief generation failed: {exc}")


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
        "/nieuwsbrief — draft this month's nieuwsbrief (also runs itself on the 1st; "
        "approving writes the .md for `kk nieuwsbrief send`)\n"
        "/cadence — show cadence\n"
        "/start — (re)schedule jobs\n\n"
        "On each draft: ✅ approve (auto-posts X, hands you the rest to paste), "
        "✏️ rewrite (then send me a note), ❌ skip. Drafts for video platforms "
        "arrive with a generated chat-demo reel; tap 🎬 and send your own screen "
        "recording to replace it with real footage."
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
        store.update_draft(draft_id, awaiting="note")
        await query.message.reply_text(
            "✏️ Send me a one-line note and I'll rewrite this draft "
            "(e.g. 'punchier hook', 'make it Dutch', 'shorter')."
        )
    elif action == "record":
        store.update_draft(draft_id, awaiting="recording")
        await query.message.reply_text(
            "🎬 Send me the screen recording (as a video message — bots can't download "
            "files over 20MB) and I'll cut it into a branded reel."
        )
    elif action == "approve":
        await query.edit_message_reply_markup(reply_markup=None)
        if draft.get("kind") == newsletter.KIND:
            await _approve_newsletter(context, query.message.chat_id, draft)
        else:
            await _approve(context, query.message.chat_id, draft)


def _media_for(draft: dict, platform: str) -> dict | None:
    """Best ready media record for a platform: the reel wins over a card; for
    images the square card beats the story (feeds crop 9:16)."""
    records = [
        m
        for m in draft.get("media") or []
        if m.get("status") == "ready" and platform in (m.get("platform_targets") or [])
    ]
    for match in (
        lambda m: m["type"] == "video",
        lambda m: m["type"] == "image" and m.get("aspect") == "square",
        lambda m: m["type"] == "image",
    ):
        for m in records:
            if match(m):
                return m
    return None


def _pub_x(draft: dict, text: str, media: dict | None) -> str:
    result = post_to_x(text)
    if not result.ok:
        raise RuntimeError(result.error)
    return result.url


def _pub_instagram(draft: dict, text: str, media: dict | None) -> str:
    if media is None:
        raise RuntimeError("Instagram can't post caption-only; no ready image/reel on this draft.")
    return publish_meta.publish_instagram(draft, media)


def _pub_facebook(draft: dict, text: str, media: dict | None) -> str:
    return publish_meta.publish_facebook(draft, media)


# Publisher per auto-delivery platform: fn(draft, text, media) -> url, raises on
# failure. A new `delivery: auto` platform in config needs an entry here.
_PUBLISHERS = {"x": _pub_x, "instagram": _pub_instagram, "facebook": _pub_facebook}


async def _approve_newsletter(
    context: ContextTypes.DEFAULT_TYPE, chat_id: int, draft: dict
) -> None:
    """Approval writes the .md and marks the draft approved — nothing is sent from here.
    The dry-run tag lands on the record inside newsletter.approve; the file is the
    deliverable either way, and `kk nieuwsbrief send` (founder-run) does the sending."""
    try:
        path = await asyncio.to_thread(newsletter.approve, draft)
    except Exception as exc:
        await context.bot.send_message(chat_id, f"⚠️ Couldn't save the nieuwsbrief: {exc}")
        return
    note = f"✅ Nieuwsbrief approved and saved: {path}\nSend it with: kk nieuwsbrief send"
    if dry_run():
        note += "\n(dry-run: approval tagged dry_run on the record; nothing was sent anyway)"
    await context.bot.send_message(chat_id, note)


async def _approve(context: ContextTypes.DEFAULT_TYPE, chat_id: int, draft: dict) -> None:
    # In dry-run the publishers return fake notes; keep the ledger honest by tagging
    # the record dry_run and never advancing status past "approved".
    dry = dry_run()
    store.update_draft(draft["id"], status="approved", approved_at=store.now_iso())
    if dry:
        store.update_draft(draft["id"], dry_run=True)
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
        try:
            url = await asyncio.to_thread(
                publisher, draft, variants[platform], _media_for(draft, platform)
            )
            if not dry:
                store.update_draft(draft["id"], status="posted", **{f"{platform}_url": url})
            await context.bot.send_message(chat_id, f"✅ Posted to {platform.title()}: {url}")
        except Exception as exc:
            store.update_draft(draft["id"], **{f"{platform}_error": f"{store.now_iso()} {exc}"})
            await context.bot.send_message(
                chat_id,
                f"⚠️ {platform.title()} post failed ({exc}). Here it is to post by hand:",
            )
            await context.bot.send_message(chat_id, variants[platform])

    # Buffer-delivery platforms: push the text into the channel's queue. Nothing is
    # live yet — Buffer's own schedule decides when it goes out.
    queued_any = False
    for platform in platforms.buffer_platforms():
        if platform not in variants:
            continue
        try:
            note = await asyncio.to_thread(publish_buffer.queue, platform, variants[platform])
            if _media_for(draft, platform):
                note += "\nMedia stayed behind (Buffer fetches assets by URL and we have "
                note += "nowhere public to host them yet) — attach it in Buffer if you want it."
            if not dry:
                store.update_draft(draft["id"], **{f"{platform}_queued": note})
                queued_any = True
            await context.bot.send_message(chat_id, f"🗓 Queued in Buffer: {note}")
        except Exception as exc:
            store.update_draft(draft["id"], **{f"{platform}_error": f"{store.now_iso()} {exc}"})
            await context.bot.send_message(
                chat_id,
                f"⚠️ Couldn't queue {platform.title()} in Buffer ({exc}). "
                f"Here it is to post by hand:",
            )
            await context.bot.send_message(chat_id, variants[platform])
    # Queued is not posted; only say "posted" if an auto platform actually posted.
    if queued_any and (store.get_draft(draft["id"]) or {}).get("status") != "posted":
        store.update_draft(draft["id"], status="queued")

    # Draft-delivery platforms (TikTok): upload the reel to the founder's in-app
    # inbox; the caption can't ride along, so it is handed over to paste there.
    for platform in platforms.draft_platforms():
        if platform not in variants:
            continue
        media_rec = _media_for(draft, platform)
        try:
            if platform != "tiktok":
                raise RuntimeError(f"no draft-uploader wired up for {platform}")
            if media_rec is None or media_rec["type"] != "video":
                raise RuntimeError("no ready reel on this draft")
            note = await asyncio.to_thread(publish_tiktok.upload_draft, draft, media_rec)
            await context.bot.send_message(
                chat_id,
                f"📥 {platform.title()}: reel is in your in-app inbox ({note}).\n"
                f"Open the app, add a rising sound, paste the caption below, post.",
            )
        except Exception as exc:
            store.update_draft(draft["id"], **{f"{platform}_error": f"{store.now_iso()} {exc}"})
            await context.bot.send_message(
                chat_id,
                f"⚠️ {platform.title()} draft upload failed ({exc}). Post by hand — caption below:",
            )
        await context.bot.send_message(chat_id, variants[platform])

    # Assisted-delivery platforms: hand over clean text to paste.
    for platform in platforms.assisted_platforms():
        if platform in variants:
            await context.bot.send_message(chat_id, f"⬇️ {platform.title()} — copy & paste:")
            await context.bot.send_message(chat_id, variants[platform])


def _awaiting_draft(kind: str) -> dict | None:
    """The pending draft waiting on founder input of this kind. The flag lives on
    the draft record, not in chat_data, so it survives bot restarts."""
    waiting = [
        d for d in store.load_queue() if d.get("awaiting") == kind and d["status"] == "pending"
    ]
    return waiting[-1] if waiting else None


async def on_note(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    draft = _awaiting_draft("note")
    if draft is None:
        return  # not a rewrite note; ignore
    draft_id = draft["id"]
    store.update_draft(draft_id, awaiting=None)
    note = update.message.text.strip()
    await update.message.reply_text("Rewriting…")
    if draft.get("kind") == newsletter.KIND:
        # One whole-edition rewrite, then redeliver (fresh .md document + summary).
        try:
            fields = await asyncio.to_thread(newsletter.regenerate, draft, note)
        except Exception as exc:
            await update.message.reply_text(f"⚠️ Couldn't rewrite the nieuwsbrief: {exc}")
            fields = {}
        draft = store.update_draft(draft_id, **fields) or {**draft, **fields}
        await _deliver_draft(context.application, update.effective_chat.id, draft)
        return
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
        reply_markup=_keyboard(draft_id, formatting.pending_reel(draft)),
    )


async def on_recording(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """A video arrived: fulfill the draft's recording task by building the reel."""
    draft = _awaiting_draft("recording")
    msg = update.message
    if draft is None:
        await msg.reply_text(
            "Got a video, but no draft is waiting for one — tap 🎬 on a draft first."
        )
        return
    draft_id = draft["id"]
    await msg.reply_text("🎬 Building the reel…")
    raw_path = data_dir() / "media" / "raw" / f"{draft_id}-raw.mp4"
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        tg_file = await (msg.video or msg.document).get_file()
        await tg_file.download_to_drive(raw_path)
        card = draft.get("card") or {}
        headline = card.get("headline", "").strip() or draft.get("topic", "")
        record = await asyncio.to_thread(
            media.build_reel,
            raw_path,
            draft_id,
            headline,
            card.get("sub", "").strip(),
        )
    except Exception as exc:
        # `awaiting` stays set on the draft, so the founder can just resend the clip.
        await msg.reply_text(
            f"⚠️ Reel build failed: {exc}\nSend the clip again to retry "
            f"(a compressed video message avoids the 20MB bot download limit)."
        )
        return
    # Real footage supersedes the whole video story: the pending task it fulfills
    # AND any scripted demo reel attached at generation time.
    media_list = [m for m in draft.get("media", []) if m["type"] != "video"] + [record]
    draft = store.update_draft(draft_id, media=media_list, awaiting=None) or draft
    with open(record["path"], "rb") as fh:
        await msg.reply_video(fh, caption="🎬 reel — save & attach")
    # A matching cover (same scheme as the draft's cards) — set it in-app when
    # posting so the grid stays coherent. Never blocks the reel.
    try:
        cover = await asyncio.to_thread(pagekit.render_cover, headline, draft_id)
        with open(cover, "rb") as fh:
            await msg.reply_photo(fh, caption="🖼 cover — set on IG/TikTok when posting")
    except Exception as exc:
        await msg.reply_text(f"⚠️ Cover render failed (reel is fine): {exc}")
    await msg.reply_text(
        formatting.preview(draft),
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=_keyboard(draft_id, formatting.pending_reel(draft)),
    )


# --------------------------------------------------------------------------- #
# App wiring
# --------------------------------------------------------------------------- #


def _ipv4_request(pool_size: int) -> HTTPXRequest:
    # Home IPv6 routes to api.telegram.org can silently break (TLS ConnectError on
    # every new connection); binding the local side to 0.0.0.0 forces IPv4.
    transport = httpx.AsyncHTTPTransport(
        local_address="0.0.0.0",
        limits=httpx.Limits(max_connections=pool_size),
        retries=2,
    )
    return HTTPXRequest(
        connection_pool_size=pool_size,
        media_write_timeout=60.0,
        httpx_kwargs={"transport": transport},
    )


async def _on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.getLogger(__name__).error("Unhandled error", exc_info=context.error)
    try:
        await context.bot.send_message(
            int(env("TELEGRAM_CHAT_ID")), f"⚠️ Bot error: {context.error}"
        )
    except Exception:
        pass  # reporting itself failed; already logged, keep the bot alive


async def _post_init(app: Application) -> None:
    chat_id = int(env("TELEGRAM_CHAT_ID"))
    schedule_jobs(app, chat_id)
    await app.bot.send_message(
        chat_id,
        "🚀 Growth Engine started and scheduled. Send /now for a draft, or wait for the "
        "next scheduled run.",
    )
    pending = [d for d in store.load_queue() if d["status"] == "pending"]
    stuck = [d for d in pending if not d.get("delivered_at")]
    if stuck:
        await app.bot.send_message(
            chat_id, f"📬 Resending {len(stuck)} draft(s) that never reached you:"
        )
    for draft in stuck:
        try:
            await _deliver_draft(app, chat_id, draft)
        except Exception:
            logging.getLogger(__name__).exception(
                "Redelivery of %s failed; will retry on next start", draft["id"]
            )
    # Delivered but never decided: resend the approval message (buttons only, media
    # was already delivered once) so open drafts don't die in Telegram scroll-back.
    waiting = [d for d in pending if d.get("delivered_at")]
    if waiting:
        await app.bot.send_message(
            chat_id, f"⏳ {len(waiting)} draft(s) still await your decision:"
        )
    for draft in waiting:
        try:
            await app.bot.send_message(
                chat_id=chat_id,
                text=_approval_message(draft),
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=_keyboard(draft["id"], formatting.pending_reel(draft)),
            )
        except Exception:
            logging.getLogger(__name__).exception(
                "Resurfacing %s failed; will retry on next start", draft["id"]
            )


def build_app() -> Application:
    token = env("TELEGRAM_BOT_TOKEN")
    app = (
        Application.builder()
        .token(token)
        .request(_ipv4_request(pool_size=8))
        .get_updates_request(_ipv4_request(pool_size=1))
        .post_init(_post_init)
        .build()
    )
    app.add_error_handler(_on_error)
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("now", cmd_now))
    app.add_handler(CommandHandler("buildlog", cmd_buildlog))
    app.add_handler(CommandHandler("nieuwsbrief", cmd_nieuwsbrief))
    app.add_handler(CommandHandler("cadence", cmd_cadence))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CallbackQueryHandler(on_button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_note))
    app.add_handler(MessageHandler(filters.VIDEO | filters.Document.VIDEO, on_recording))
    return app
