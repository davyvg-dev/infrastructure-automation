"""Pre-approval draft verification: one cheap LLM-judge call before Telegram.

Every draft is graded against an explicit checklist by claude-haiku-4-5
(temperature 0, structured output) BEFORE it reaches the founder's approval
message. PASS -> proceed unchanged. FAIL -> ONE auto-revise via the drafting
model, then one re-judge; a still-failing draft goes to Telegram anyway with
the failure reasons prepended (see formatting.verify_flags) so the founder
sees the flags. A judge exception never breaks the pipeline: fail-open with a
"verify pass errored" note on the draft. Drafts are never dropped silently.

Toggle: GROWTH_ENGINE_VERIFY (settings.verify_enabled, default on).
The human approval gate in bot.py is untouched — this only reduces rejects.
"""

from __future__ import annotations

import json
import logging
from typing import Any

import anthropic

from . import generate, platforms
from .settings import env, strategy, verify_enabled

log = logging.getLogger(__name__)

# Cheap judge, separate from the drafting model (config model.id). Haiku 4.5:
# no thinking/effort params; temperature is supported and pinned to 0.
JUDGE_MODEL = "claude-haiku-4-5"

# criterion id -> what the judge grades. Ids are stable: they feed the JSON
# schema enum, the failure records on the draft, and the Telegram flags.
CRITERIA: dict[str, str] = {
    "ai_tells": (
        "The text reads like a professional copywriter, not AI. FAIL on decorative "
        "em-dashes (—) used as a stylistic tic, or AI-tell phrasing (e.g. 'in today's "
        "fast-paced world', 'game-changer', 'unlock', 'let's dive in', hollow hype)."
    ),
    "founder_name": (
        "The founder's first name ('Davy') must NOT appear anywhere. Customer-facing "
        "text says 'de oprichter' or 'Klantkraan' instead. FAIL on any occurrence."
    ),
    "invented_stats": (
        "No invented statistics. Any specific number presented as an established fact "
        "(percentages, counts, money amounts other than the allowed prices) must be "
        "clearly framed as an estimate, example or industry pattern - this account has "
        "no client roster to cite. When in doubt, FAIL."
    ),
    "language": (
        "Customer-facing posts are Dutch. English is allowed ONLY for a build-log post "
        "aimed at the international builder crowd (pillar 'build_log'). One language per "
        "post, never mixed. FAIL otherwise."
    ),
    "pricing": (
        "No pricing improvisation. The ONLY amounts that may appear as Klantkraan "
        "pricing are €299 (chat), €499 (voice/Compleet) and €249 setup. Any other "
        "Klantkraan price, discount or payment term FAILS. Posts naming no price pass. "
        "Illustrative numbers about the buyer's own business are judged under "
        "invented_stats, not here."
    ),
    "platform_fit": (
        "Each variant is a sensible length and shape for its platform (hard char limits "
        "and format guidelines are given per variant). FAIL if a variant is over a hard "
        "limit or wildly off its format."
    ),
}

# Static schema (structured outputs cache the compiled schema for 24h).
_VERDICT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "checks": {
            "type": "array",
            "description": "Exactly one entry per criterion.",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "criterion": {"type": "string", "enum": list(CRITERIA)},
                    "passed": {"type": "boolean"},
                    "reason": {
                        "type": "string",
                        "description": "One short sentence on why it failed; empty when passed.",
                    },
                },
                "required": ["criterion", "passed", "reason"],
            },
        },
    },
    "required": ["checks"],
}


def _client() -> anthropic.Anthropic:
    # Reads ANTHROPIC_API_KEY from the environment (loaded by settings).
    env("ANTHROPIC_API_KEY")
    return anthropic.Anthropic()


def _system_prompt() -> str:
    rules = "\n".join(f"- {key}: {text}" for key, text in CRITERIA.items())
    return (
        "You are the pre-publication reviewer for social posts drafted for Klantkraan "
        "(klantkraan.nl), AI receptionists for Dutch trade businesses. You grade a draft "
        "(all its platform variants together) against a fixed checklist. Be strict and "
        "literal; a criterion fails if ANY variant violates it.\n\n"
        f"Checklist:\n{rules}\n\n"
        "Return one check per criterion with passed true/false and, on failure, a short "
        "concrete reason that quotes or names the offending part."
    )


def _brief(draft: dict[str, Any]) -> str:
    langs = strategy().get("languages", {})
    reg = platforms.registry()
    parts = [
        f"PILLAR: {draft.get('pillar', 'unknown')}",
        f"LANGUAGE RULE: buyer-facing posts are {langs.get('primary', 'Dutch')}; "
        f"{langs.get('secondary', 'English')} is allowed only for the build_log pillar.",
        "",
        "VARIANTS:",
    ]
    for name, text in draft["variants"].items():
        desc = reg.get(name, {})
        limit = desc.get("char_limit")
        length = f"{len(text)} chars" + (f", hard limit {limit}" if limit else "")
        parts.append(f"--- {name} ({length}) ---")
        if desc.get("writing"):
            parts.append(f"[format guideline: {desc['writing']}]")
        parts.append(text)
        parts.append("")
    return "\n".join(parts)


def verify_draft(draft: dict[str, Any]) -> dict[str, Any]:
    """One judge call. Returns the parsed verdict ({'checks': [...]}); raises on API error."""
    response = _client().messages.create(
        model=JUDGE_MODEL,
        max_tokens=1000,
        temperature=0,
        output_config={"format": {"type": "json_schema", "schema": _VERDICT_SCHEMA}},
        system=[{"type": "text", "text": _system_prompt()}],
        messages=[{"role": "user", "content": _brief(draft)}],
    )
    text = "".join(b.text for b in response.content if b.type == "text")
    return json.loads(text)


def _failures(verdict: dict[str, Any]) -> list[dict[str, str]]:
    return [
        {
            "criterion": check.get("criterion", "unknown"),
            "reason": (check.get("reason") or "").strip(),
        }
        for check in verdict.get("checks", [])
        if not check.get("passed", False)
    ]


def _revision_note(failures: list[dict[str, str]]) -> str:
    issues = "; ".join(f"{f['criterion']}: {f['reason']}" for f in failures)
    return (
        f"An editorial review flagged these issues: {issues}. "
        f"Rewrite the post to fix ALL of them while keeping the same core idea, "
        f"language and platform format."
    )


def check_and_revise(draft: dict[str, Any]) -> dict[str, Any]:
    """The pre-approval pass. Always returns the draft; never raises, never drops.

    Annotates draft['verify'] with {'status': 'pass'|'fail'|'error', ...} which
    formatting.verify_flags renders into the approval message on fail/error.
    """
    if not verify_enabled() or not draft.get("variants"):
        return draft
    try:
        failures = _failures(verify_draft(draft))
        if not failures:
            draft["verify"] = {"status": "pass", "failures": [], "revised": False}
            return draft

        # One auto-revise: hand the failed criteria back to the drafting model,
        # per variant, then re-judge ONCE. Never more than one revise loop.
        log.info("draft %s failed pre-check (%d issue(s)); revising once", draft.get("id"), len(failures))
        note = _revision_note(failures)
        new_variants: dict[str, str] = {}
        for name, text in draft["variants"].items():
            try:
                new_variants[name] = generate.regenerate_variant(draft, name, note).strip() or text
            except Exception:  # keep the original variant; the re-judge will flag it
                log.exception("revise of %s variant failed; keeping the original", name)
                new_variants[name] = text
        draft["variants"] = new_variants

        failures = _failures(verify_draft(draft))
        status = "fail" if failures else "pass"
        draft["verify"] = {"status": status, "failures": failures, "revised": True}
        return draft
    except Exception as exc:
        # Fail-open: the founder still gets the draft, with an errored-check note.
        log.exception("verify pass errored; sending draft to Telegram unchecked")
        draft["verify"] = {"status": "error", "failures": [], "error": str(exc)}
        return draft
