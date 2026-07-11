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
- Write FOR THE BUYER — a busy local business owner (a plumber, dentist, salon owner) — not
  for other developers or the tech crowd. Lead with their money and their pain, not the tech.
- Never lead with "AI" or jargon. Say what it does for them ("answers every call 24/7 and
  books the job") — not how it's built. Anchor value in their numbers (missed calls = lost
  jobs/bookings).
- Write like a real builder talking to prospects, not a marketer.
- Be specific and concrete. Real numbers, real scenarios, real decisions beat vague claims.
- One idea per post. Earn the read; no engagement-bait.
- This account is BUILD-IN-PUBLIC: there is no past client roster to cite. Frame proof as \
work shipped live (demos, builds in progress), never invent fake clients, testimonials, or \
metrics. If a concrete number would help, frame it as an estimate or industry pattern, not a \
fabricated result.
- No hashtags on LinkedIn beyond 0-2 if truly relevant; none on X unless natural.
- Do not use em dashes as a stylistic tic; write plainly.

How to make a post land (this matters most):
- Anchor every post to ONE specific, real detail — a number, a timestamp, an exact failure,
  a concrete before/after. "The bot misheard '15' as '50' on 1 in 40 messages until I added
  a confirm step" beats "made good progress on accuracy". Vague = skippable AI slop.
- Open with the concrete moment, not a generic setup. Never start with "In today's world",
  "Most people struggle with", or "Here's why X matters".
- Structure: a hook (the real moment) then a plain takeaway the reader walks away with.
- Publish gate — before finishing, check: (1) does this prove I actually did the work?
  (2) is the takeaway specific, not vague? If either fails, rewrite it."""


_PLATFORM_SPECS = {
    # X = distribution + personality. Punchier; links are fine here.
    "x": "X post: max 280 characters, punchy, personality-forward, no hashtags unless "
         "natural. A strong first line that stands alone.",
    # LinkedIn = the primary B2B channel where buyers live. Native long-form performs best.
    "linkedin": "LinkedIn post (primary B2B channel): 150-400 words. The first 1-3 lines are "
                "a scroll-stopping hook that stands alone above the fold. Generous line "
                "breaks (1-2 sentences each), one idea, end with a genuine question to spark "
                "comments. NO links in the body. No hashtag walls.",
    "reddit": "Reddit: value-first, zero self-promotion in the body. Written to genuinely "
              "help in a relevant subreddit (e.g. r/smallbusiness, r/dentistry, r/msp). "
              "Sound like a helpful practitioner, not an ad.",
}


def platform_instructions(platforms: list[str]) -> str:
    """The per-platform formatting block, reused by every generator."""
    return "\n".join(f"- {_PLATFORM_SPECS[p]}" for p in platforms if p in _PLATFORM_SPECS)


def draft_brief(pillar: dict[str, Any], platforms: list[str], recent: list[str]) -> str:
    s = strategy()
    langs = s["languages"]
    avoid = "\n".join(f"- {t}" for t in recent) if recent else "(none yet)"
    wanted = platform_instructions(platforms)

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
