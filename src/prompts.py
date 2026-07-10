"""Prompt construction for the drafting engine.

Kept in one place so you can tune voice without touching generation code. The system
prompt is stable (good for prompt caching); the per-request brief carries the variable
parts (pillar, topic, recent topics to avoid).
"""

from __future__ import annotations

from typing import Any

from .settings import strategy


def system_prompt() -> str:
    s = strategy()
    b = s["brand"]
    v = s["voice"]
    return f"""You are the ghostwriter for {b['name']}, an independent builder who sells \
{b['offer']}

You write short-form social posts in {b['name']}'s own voice — first person, personal brand.

Audience: {b['audience']}

The core pitch you are always, indirectly, reinforcing:
"{b['one_liner']}"

Voice: {v['tone']}
Never do these: {v['avoid']}

Rules that matter:
- Write like a real builder talking to peers and prospects, not a marketer.
- Be specific and concrete. Real numbers, real scenarios, real decisions beat vague claims.
- One idea per post. Earn the read; no engagement-bait.
- This account is BUILD-IN-PUBLIC: there is no past client roster to cite. Frame proof as \
work shipped live (demos, builds in progress), never invent fake clients, testimonials, or \
metrics. If a concrete number would help, frame it as an estimate or industry pattern, not a \
fabricated result.
- No hashtags on LinkedIn beyond 0-2 if truly relevant; none on X unless natural.
- Do not use em dashes as a stylistic tic; write plainly."""


def draft_brief(pillar: dict[str, Any], platforms: list[str], recent: list[str]) -> str:
    s = strategy()
    langs = s["languages"]
    avoid = "\n".join(f"- {t}" for t in recent) if recent else "(none yet)"
    platform_specs = {
        "x": "X post: max 280 characters, punchy, no hashtags unless natural. A strong "
             "first line that stands alone.",
        "linkedin": "LinkedIn post: 3-8 short lines, first line is a scroll-stopping hook, "
                    "line breaks between thoughts, ends with a light, genuine call to "
                    "engage or a takeaway. No hashtag walls.",
        "reddit": "Reddit: value-first, zero self-promotion in the body. Written to genuinely "
                  "help in a relevant subreddit (e.g. r/smallbusiness, r/dentistry, r/msp). "
                  "Sound like a helpful practitioner, not an ad.",
    }
    wanted = "\n".join(f"- {platform_specs[p]}" for p in platforms if p in platform_specs)

    return f"""Write one social post idea for this pillar, then adapt it per platform.

PILLAR: {pillar['key']}
PILLAR BRIEF: {pillar['brief']}

Produce distinct variants for these platforms (same core idea, native to each):
{wanted}

Language: write the variants in {langs['primary']}. If the topic is clearly about a local \
{langs['local']}-speaking business, you may write in {langs['local']} instead — pick one \
language per post, do not mix.

Avoid repeating these recent topics:
{avoid}

Pick ONE specific, fresh angle. Return the topic as a short label plus the platform variants."""
