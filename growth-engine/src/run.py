"""Entrypoint: start the bot + scheduler.

    python -m src.run

Runs until interrupted. Put it on any always-on host (laptop overnight, a small VPS,
or a free Fly.io/Railway instance).
"""

from __future__ import annotations

from .bot import build_app
from .settings import ensure_dirs


def main() -> None:
    ensure_dirs()
    app = build_app()
    app.run_polling()


if __name__ == "__main__":
    main()
