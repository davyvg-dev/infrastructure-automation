"""The shared opt-out record: data/suppression.txt.

One lowercased address per line, `#` comments allowed. This is the Telecommunicatiewet
art. 11.7 opt-out list (consent withdrawn), not a deliverability list: a hard bounce is
halted in its own ledger but never suppressed, because a dead mailbox said nothing about
consent. Writers: the cold-outreach sequencer (scripts/sequence.py --opt-out) and the
cursus afmelding (app/cursus.py). Reader: pipeline.qualify's suppression gate.
"""

from __future__ import annotations

from pathlib import Path

from . import settings


def default_path() -> Path:
    # Read settings.DATA_DIR at call time, not import time, so the tests' data_dir
    # fixture (which monkeypatches settings.DATA_DIR) is honored.
    return settings.DATA_DIR / "suppression.txt"


def entries(path: Path | None = None) -> set[str]:
    """Every suppressed address, lowercased. Missing file = empty set."""
    path = path or default_path()
    if not path.exists():
        return set()
    return {
        ln.strip().lower()
        for ln in path.read_text().splitlines()
        if ln.strip() and ln[0] != "#"
    }


def suppress(email: str, path: Path | None = None) -> bool:
    """Append an address to the opt-out record. Returns False if already there."""
    path = path or default_path()
    existing = set()
    if path.exists():
        existing = {
            ln.strip().lower()
            for ln in path.read_text().splitlines()
            if ln.strip() and ln[0] != "#"
        }
    if email.lower() in existing:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as fh:
        fh.write(f"{email}\n")
    return True
