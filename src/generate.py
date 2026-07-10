"""The Claude drafting engine.

Calls Claude with structured outputs so we always get back a clean, parseable draft:
a topic label plus per-platform variants. Uses claude-opus-4-8 with adaptive thinking.
"""

from __future__ import annotations

import uuid
from datetime import date
from typing import Any

import anthropic

from . import ideas, prompts
from .settings import env, strategy

# Static schema → structured outputs cache the compiled schema for 24h.
_DRAFT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "topic": {
            "type": "string",
            "description": "Short label for this post's angle (a few words).",
        },
        "variants": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "x": {"type": "string", "description": "X post, or empty string if not requested."},
                "linkedin": {"type": "string", "description": "LinkedIn post, or empty string."},
                "reddit": {"type": "string", "description": "Reddit post, or empty string."},
            },
            "required": ["x", "linkedin", "reddit"],
        },
    },
    "required": ["topic", "variants"],
}


def _client() -> anthropic.Anthropic:
    # Reads ANTHROPIC_API_KEY from the environment (loaded by settings).
    env("ANTHROPIC_API_KEY")
    return anthropic.Anthropic()


def generate_draft(platforms: list[str]) -> dict[str, Any]:
    """Generate one draft (topic + variants) for the next pillar in rotation."""
    pillar = ideas.next_pillar()
    recent = ideas.recent_topics()
    model_cfg = strategy()["model"]

    client = _client()
    response = client.messages.create(
        model=model_cfg["id"],
        max_tokens=2000,
        thinking={"type": "adaptive"},
        output_config={
            "effort": model_cfg.get("effort", "medium"),
            "format": {"type": "json_schema", "schema": _DRAFT_SCHEMA},
        },
        system=[{
            "type": "text",
            "text": prompts.system_prompt(),
            "cache_control": {"type": "ephemeral"},
        }],
        messages=[{"role": "user", "content": prompts.draft_brief(pillar, platforms, recent)}],
    )

    payload = _extract_json(response)
    variants = {k: v.strip() for k, v in payload["variants"].items() if v and v.strip()}
    # Only keep platforms that were actually requested.
    variants = {k: v for k, v in variants.items() if k in platforms}

    return {
        "id": f"{date.today():%Y%m%d}-{uuid.uuid4().hex[:4]}",
        "pillar": pillar["key"],
        "topic": payload["topic"].strip(),
        "status": "pending",
        "variants": variants,
    }


def regenerate_variant(draft: dict[str, Any], platform: str, note: str) -> str:
    """Rewrite a single platform's variant given the user's feedback note."""
    model_cfg = strategy()["model"]
    current = draft["variants"].get(platform, "")
    client = _client()
    response = client.messages.create(
        model=model_cfg["id"],
        max_tokens=1200,
        thinking={"type": "adaptive"},
        output_config={"effort": model_cfg.get("effort", "medium")},
        system=[{"type": "text", "text": prompts.system_prompt()}],
        messages=[{
            "role": "user",
            "content": (
                f"Here is a {platform} post I drafted:\n\n{current}\n\n"
                f"Rewrite it with this feedback: {note}\n\n"
                f"Return ONLY the rewritten post text, nothing else."
            ),
        }],
    )
    return "".join(b.text for b in response.content if b.type == "text").strip()


def _extract_json(response: anthropic.types.Message) -> dict[str, Any]:
    import json

    text = "".join(b.text for b in response.content if b.type == "text")
    return json.loads(text)
