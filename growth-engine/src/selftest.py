"""Isolated self-tests — verify each process on its own before wiring them together.

Run one layer at a time (see TASK.md):

    python -m src.selftest config      # config + env sanity, no network
    python -m src.selftest platforms   # platform registry sanity, no network
    python -m src.selftest media       # offline image-card render (Pillow + fonts)
    python -m src.selftest reel        # offline reel build (needs ffmpeg)
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


def check_media() -> bool:
    print("• media (offline card render)")
    from . import brand

    if not brand.cards_enabled():
        _ok("media.cards disabled in config — skipping render")
        return True
    import tempfile
    from pathlib import Path

    from . import media

    try:
        with tempfile.TemporaryDirectory() as tmp:
            records = media.render_cards(
                "Een gemiste oproep is een gemiste klus.",
                "Zo verlies je stilletjes omzet — elke week weer.",
                "selftest",
                out_dir=Path(tmp),
            )
            from PIL import Image

            for rec in records:
                with Image.open(rec["path"]) as img:
                    expected = {"square": (1080, 1080), "story": (1080, 1920)}[rec["aspect"]]
                    if img.size != expected:
                        return _fail(f"{rec['aspect']} rendered {img.size}, want {expected}")
                _ok(f"{rec['aspect']}: {expected[0]}×{expected[1]} → targets {rec['platform_targets']}")
            # Every scheme must render (a bad hex value should fail here, not at 11:00).
            for i, scheme in enumerate(brand.schemes()):
                media._render("Schemacheck", "", (540, 540), Path(tmp) / f"s{i}.png",
                              scheme, None)
            _ok(f"{len(brand.schemes())} scheme(s) render")
    except Exception as exc:
        return _fail(f"card render failed: {exc}")
    import os

    stock = brand.stock()
    if stock["enabled"]:
        has_key = bool(os.getenv("PEXELS_API_KEY", "").strip())
        _ok(f"stock photos: every {stock['every']}th card — "
            f"PEXELS_API_KEY {'set' if has_key else 'NOT set (flat fallback)'}")
    return True


def check_reel() -> bool:
    print("• reel (offline build from a synthetic clip)")
    import shutil

    from . import brand

    cfg = brand.reel()
    if not cfg["enabled"]:
        _ok("media.reel disabled in config — skipping")
        return True
    for tool in ("ffmpeg", "ffprobe"):
        if shutil.which(tool) is None:
            return _fail(f"{tool} not installed but media.reel.enabled is true")
    import subprocess
    import tempfile
    from pathlib import Path

    from . import media

    try:
        with tempfile.TemporaryDirectory() as tmp:
            raw = Path(tmp) / "raw.mp4"
            # A fake chat recording at a real iPhone ratio, 12s: idle stretches
            # (static color), a "typing" stretch (a keystroke-sized box flickering
            # 4×/s from 2s-6s, like a keyboard in use), and two hard full-frame
            # changes (messages popping in at 6s and 9s). All three frame classes.
            subprocess.run(
                ["ffmpeg", "-y", "-v", "error",
                 "-f", "lavfi", "-i", "color=c=Gray:size=390x844:rate=30:duration=6",
                 "-f", "lavfi", "-i", "color=c=White:size=90x60:rate=30:duration=6",
                 "-f", "lavfi", "-i", "color=c=Blue:size=390x844:rate=30:duration=3",
                 "-f", "lavfi", "-i", "color=c=Yellow:size=390x844:rate=30:duration=3",
                 "-filter_complex",
                 "[0][1]overlay=x=150:y=650:"
                 "enable='between(t,2,6)*lt(mod(t,0.5),0.25)'[a];"
                 "[a][2][3]concat=n=3:v=1:a=0",
                 "-pix_fmt", "yuv420p", str(raw)],
                check=True, capture_output=True, text=True,
            )
            record = media.build_reel(
                raw, "selftest", "Testkop voor de reel", "Een sublijn.",
                out_dir=Path(tmp),
            )
            w, h, duration = media._probe(Path(record["path"]))
            if (w, h) != (1080, 1920):
                return _fail(f"reel rendered {w}×{h}, want 1080×1920")
            cap = float(cfg["target_seconds"]) + 0.5  # rounding headroom
            if duration > cap:
                return _fail(f"reel is {duration:.1f}s, cap is {cfg['target_seconds']}s")
            if cfg["pop_cuts"]:
                demo = duration - float(cfg["cta_seconds"])
                # Expected band: 3 pop holds (3×dwell = 4.2s) + 4s typing at
                # typing_speed (~1.3s) + cold open (1s) + suspense beat (0.6s)
                # ≈ 7.1s. Above it = idle survived; below it = typing was cut.
                if demo > 8.2:
                    return _fail(f"idle not cut: {demo:.1f}s demo from 12s raw")
                if demo < 6.2:
                    return _fail(f"typing was cut, not sped up: {demo:.1f}s demo "
                                 f"(holds + cold open + beat alone are ~5.8s)")
            _ok(f"reel: 1080×1920, {duration:.1f}s from a 12s raw (cold open + "
                f"hook-on-footage, idle cut, typing {cfg['typing_speed']}×, "
                f"suspense beat, CTA freeze) → {record['platform_targets']}")
            _ok(f"crop_top {cfg['crop_top']} · cap {cfg['target_seconds']}s · "
                f"dwell ≤{cfg['dwell_seconds']}s · max speed {cfg['max_speed']}×")
            # Sound layer: the reel must carry a real audio stream with actual
            # content (SFX beats) — a silent track means the layer regressed.
            import re as _re
            streams = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "stream=codec_type",
                 "-of", "csv=p=0", record["path"]],
                check=True, capture_output=True, text=True,
            ).stdout.split()
            if cfg["audio"]["enabled"]:
                if streams.count("video") != 1 or streams.count("audio") != 1:
                    return _fail(f"want 1 video + 1 audio stream, got {streams}")
                vd = subprocess.run(
                    ["ffmpeg", "-hide_banner", "-i", record["path"], "-map", "0:a:0",
                     "-af", "volumedetect", "-f", "null", "-"],
                    capture_output=True, text=True,
                )
                m = _re.search(r"mean_volume:\s*(-?[\d.]+) dB", vd.stderr)
                if not m:
                    return _fail("volumedetect gave no mean_volume for the audio track")
                mean = float(m.group(1))
                if mean <= -80.0:
                    return _fail(f"audio is effectively silent (mean {mean:.1f} dB)")
                _ok(f"audio: aac stream present, mean {mean:.1f} dB (sfx "
                    f"{'on' if cfg['audio']['sfx'] else 'off'}, bed "
                    f"{cfg['audio']['bed'] or 'none'})")
            else:
                if "audio" in streams:
                    return _fail("media.reel.audio disabled but reel has an audio stream")
                _ok("audio disabled in config — reel is video-only, as configured")
    except subprocess.CalledProcessError as exc:
        return _fail(f"ffmpeg failed: {exc.stderr.strip()[-300:]}")
    except Exception as exc:
        return _fail(f"reel build failed: {exc}")
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
    "media": check_media,
    "reel": check_reel,
    "generate": check_generate,
    "telegram": check_telegram,
    "x": check_x,
}
# Offline checks first, so a broken render can't waste an API call.
ORDER = ["config", "platforms", "media", "reel", "generate", "telegram", "x"]


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
