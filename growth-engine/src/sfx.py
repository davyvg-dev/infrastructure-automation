"""Sound design for reels — stdlib-synthesized SFX and soundtrack assembly.

Three quiet UI sounds (a keyboard tick, a message pop, a payoff ding) are synthesized
with wave + math + struct — no samples to license, no numpy. `--make-sfx` writes them
to assets/sfx/ (checked in); build_soundtrack() mixes them at the cut plan's message
beats into one full-length WAV that media.py feeds to ffmpeg.

Commercial/trending music is NEVER baked in (copyright strike risk — see docs/REELS.md);
the only allowed bed is a founder-supplied licensed/CC0 file via `media.reel.audio.bed`,
mixed far under the SFX with a fade-out.
"""

from __future__ import annotations

import math
import random
import struct
import subprocess
import sys
import tempfile
import wave
from collections.abc import Iterable
from pathlib import Path

from .settings import ROOT

RATE = 44100  # Hz, mono, 16-bit throughout
SFX_DIR = ROOT / "assets" / "sfx"
_FADE_SECONDS = 1.2  # bed fade-out at the reel's end


def _normalize(samples: list[float], peak_db: float) -> list[float]:
    """Scale so the loudest sample sits at `peak_db` dBFS."""
    peak = max((abs(s) for s in samples), default=0.0)
    if peak == 0.0:
        return samples
    gain = 10 ** (peak_db / 20) / peak
    return [s * gain for s in samples]


def _tick() -> list[float]:
    """Soft keyboard tick: ~30ms of lowpassed noise with a faint 1.9kHz body, -20 dBFS."""
    rng = random.Random(0x7EC)  # fixed seed — the checked-in file is reproducible
    n = int(0.030 * RATE)
    out: list[float] = []
    lp = 0.0
    for i in range(n):
        lp += 0.22 * (rng.uniform(-1.0, 1.0) - lp)  # one-pole lowpass takes the hiss off
        env = math.exp(-i / (0.006 * RATE))
        body = 0.4 * math.sin(2 * math.pi * 1900 * i / RATE)
        out.append((0.7 * lp + body) * env)
    return _normalize(out, -20.0)


def _pop() -> list[float]:
    """Message pop: ~120ms exponential pitch-up blip (420→980Hz), -12 dBFS."""
    n = int(0.120 * RATE)
    f0, f1 = 420.0, 980.0
    phase = 0.0
    out: list[float] = []
    for i in range(n):
        t = i / RATE
        phase += 2 * math.pi * f0 * (f1 / f0) ** (i / n) / RATE
        attack = min(i / (0.005 * RATE), 1.0)
        decay = math.exp(-max(t - 0.02, 0.0) / 0.045)
        out.append(math.sin(phase) * attack * decay)
    return _normalize(out, -12.0)


def _ding() -> list[float]:
    """Payoff ding: ~600ms 1175Hz sine, exponential decay, soft second harmonic, -12 dBFS."""
    n = int(0.600 * RATE)
    f = 1174.7  # D6 — inside the 880-1320Hz notification register
    out: list[float] = []
    for i in range(n):
        t = i / RATE
        attack = min(i / (0.003 * RATE), 1.0)
        s = math.sin(2 * math.pi * f * t) * math.exp(-t / 0.16)
        s += 0.35 * math.sin(2 * math.pi * 2 * f * t) * math.exp(-t / 0.09)
        out.append(s * attack)
    return _normalize(out, -12.0)


_GENERATORS = {"tick": _tick, "pop": _pop, "ding": _ding}


def _write_wav(path: Path, samples: list[float]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(
            struct.pack(
                f"<{len(samples)}h",
                *(int(max(-1.0, min(1.0, s)) * 32767) for s in samples),
            )
        )


def _read_wav(path: Path) -> list[float]:
    """Mono float samples at RATE (channels averaged, nearest-sample rate adapt)."""
    with wave.open(str(path), "rb") as w:
        ch, width, sr, n = w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()
        if width != 2:
            raise ValueError(f"{path}: only 16-bit WAV supported, got {8 * width}-bit")
        raw = struct.unpack(f"<{n * ch}h", w.readframes(n))
    mono = [sum(raw[i * ch : (i + 1) * ch]) / ch / 32768.0 for i in range(n)]
    if sr == RATE or not mono:
        return mono
    return [mono[min(int(i * sr / RATE), n - 1)] for i in range(int(n * RATE / sr))]


def _sfx(name: str) -> list[float]:
    """The checked-in assets/sfx file (founder-replaceable), else synthesized in-memory."""
    path = SFX_DIR / f"{name}.wav"
    if path.exists():
        return _read_wav(path)
    return _GENERATORS[name]()


def _bed_samples(bed: str, n: int, gain_db: float) -> list[float] | None:
    """Founder-supplied ambient file, decoded by ffmpeg, looped/trimmed to n samples,
    attenuated and faded out. Missing/broken bed degrades to no bed, loudly."""
    path = Path(bed)
    if not path.is_absolute():
        path = ROOT / path
    if not path.exists():
        print(f"reel audio: bed {path} does not exist — skipping bed", file=sys.stderr)
        return None
    try:
        with tempfile.TemporaryDirectory() as tmp:
            decoded = Path(tmp) / "bed.wav"
            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-v",
                    "error",
                    "-i",
                    str(path),
                    "-ac",
                    "1",
                    "-ar",
                    str(RATE),
                    "-c:a",
                    "pcm_s16le",
                    str(decoded),
                ],
                check=True,
                capture_output=True,
                text=True,
                timeout=120,
            )
            samples = _read_wav(decoded)
    except Exception as exc:
        print(f"reel audio: could not decode bed {path}: {exc}", file=sys.stderr)
        return None
    if not samples:
        return None
    gain = 10 ** (gain_db / 20)
    out = [samples[i % len(samples)] * gain for i in range(n)]  # loop/trim to length
    fade = min(int(_FADE_SECONDS * RATE), n)
    for i in range(fade):
        out[n - fade + i] *= 1.0 - (i + 1) / fade
    return out


def build_soundtrack(
    out_path: Path,
    duration: float,
    events: Iterable[tuple[float, str]],
    bed: str = "",
    bed_gain_db: float = -24.0,
) -> None:
    """Mix (time, sfx-name) events — plus an optional ambient bed — into one mono WAV
    of exactly `duration` seconds (sfx tails past the end are truncated)."""
    events = list(events)
    n = max(int(duration * RATE), 1)
    buf = [0.0] * n
    clips = {name: _sfx(name) for name in {name for _, name in events}}
    for t, name in events:
        start = int(t * RATE)
        for i, s in enumerate(clips[name]):
            j = start + i
            if 0 <= j < n:
                buf[j] += s
    if bed.strip():
        bed_buf = _bed_samples(bed.strip(), n, bed_gain_db)
        if bed_buf:
            buf = [a + b for a, b in zip(buf, bed_buf, strict=False)]
    # Overlapping SFX can sum past full scale — normalize down instead of hard-clipping.
    peak = max((abs(s) for s in buf), default=0.0)
    if peak > 0.98:
        buf = [s * 0.98 / peak for s in buf]
    # Short master fade so a truncated sfx tail can't click at the very end.
    fade = min(int(0.12 * RATE), n)
    for i in range(fade):
        buf[n - fade + i] *= 1.0 - (i + 1) / fade
    _write_wav(out_path, buf)


def make_sfx(out_dir: Path = SFX_DIR) -> list[Path]:
    """Write the three SFX WAVs; deterministic, safe to re-run."""
    paths = []
    for name, gen in _GENERATORS.items():
        path = out_dir / f"{name}.wav"
        _write_wav(path, gen())
        paths.append(path)
    return paths


if __name__ == "__main__":
    if "--make-sfx" not in sys.argv:
        print("usage: python -m src.sfx --make-sfx", file=sys.stderr)
        sys.exit(2)
    for p in make_sfx():
        print(f"wrote {p.relative_to(ROOT)}")
