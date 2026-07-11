"""Turn real git commits into a build-in-public 'build log' post.

Reads the commits made since the last time you generated a build log, summarizes what
actually shipped, and asks Claude to write an honest, specific build-log post. It never
invents work — it only draws from the commit subjects and changed files.
"""

from __future__ import annotations

import subprocess
from typing import Any

from . import generate, prompts, store
from .settings import ROOT, strategy

# Record separator (0x1e) and unit separator (0x1f) keep parsing robust against newlines
# in commit bodies.
_FMT = "%H%x1f%s%x1f%b%x1e"

_BRIEF = """These are the git commits I've shipped since my last build-log post:

{material}

Write ONE honest build-in-public "build log" post about this work. Guidance:
- Pick the single most interesting or relatable thread — a decision, a bug, a small win.
  Do NOT dump a changelog or list every commit.
- Be specific and concrete about what changed and, where you can infer it, WHY.
- It's fine for the work to be small. Do not overclaim, do not invent features, metrics,
  users, or clients that aren't evidenced by the commits.
- Keep the builder-to-peers voice.

Then adapt it per platform:
{platforms}"""


def _git(repo: str, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", repo, *args], capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git command failed")
    return result.stdout


def _files_for(repo: str, sha: str, limit: int = 12) -> list[str]:
    out = _git(repo, "show", "--name-only", "--pretty=format:", sha)
    files = [line for line in out.splitlines() if line.strip()]
    return files[:limit]


def _recent_commits(repo: str, since_sha: str | None, max_commits: int) -> list[dict[str, Any]]:
    args = ["log", "--no-merges", f"--pretty=format:{_FMT}"]
    if since_sha:
        args.append(f"{since_sha}..HEAD")
    else:
        args += ["-n", str(max_commits)]
    try:
        out = _git(repo, *args)
    except RuntimeError:
        # since_sha may be unreachable (rebased/rewritten history) — fall back to last N.
        if since_sha:
            return _recent_commits(repo, None, max_commits)
        raise

    commits: list[dict[str, Any]] = []
    for record in out.split("\x1e"):
        record = record.strip()
        if not record:
            continue
        sha, subject, body = (record.split("\x1f") + ["", "", ""])[:3]
        commits.append({
            "sha": sha.strip(),
            "subject": subject.strip(),
            "body": body.strip(),
            "files": _files_for(repo, sha.strip()),
        })
    commits.reverse()  # oldest -> newest
    return commits


def _format(commits: list[dict[str, Any]]) -> str:
    lines = []
    for c in commits:
        files = ", ".join(c["files"]) or "(no files)"
        lines.append(f"- {c['subject']}\n    files: {files}")
    return "\n".join(lines)


def build_draft(platforms: list[str]) -> dict[str, Any] | None:
    """Draft a build-log post from new commits. Returns None if there are none."""
    cfg = strategy()
    bl = cfg.get("buildlog", {})
    if not bl.get("enabled", True):
        return None
    repo = str((ROOT / bl.get("repo_path", "..")).resolve())
    since = store.get_state("buildlog_last_sha")
    commits = _recent_commits(repo, since, int(bl.get("max_commits", 25)))
    if not commits:
        return None

    brief = _BRIEF.format(material=_format(commits), platforms=prompts.platform_instructions(platforms))
    draft = generate.generate_from_brief("build_log", brief, platforms)
    draft["source_commits"] = [c["sha"][:8] for c in commits]
    store.set_state("buildlog_last_sha", commits[-1]["sha"])  # newest processed
    return draft
