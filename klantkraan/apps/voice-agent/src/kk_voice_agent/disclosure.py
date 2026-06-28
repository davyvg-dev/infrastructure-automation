"""EU AI Act art. 50(1) disclosure -- VERBATIM, non-waivable.

Source of truth: klantkraan/docs/04-legal/ai-act-disclosure.md
Mirrored in:     packages/prompts/nl/<vertical>.v1.md (opening line).

Spoken as the first utterance of every call via AgentSession.say() (exact
text), never generate_reply() (which paraphrases). Drift from the source doc
is a compliance defect, fine up to EUR 15M or 3% global turnover (art.
99(4)(g)). CI MUST assert render_disclosure() equals the source-doc string
before any deploy.
"""

from __future__ import annotations

DISCLOSURE_TEMPLATE = (
    "Goedendag, u spreekt met {agent_naam}, de digitale assistent van "
    "{client_name}. Dit gesprek wordt gevoerd door een AI-systeem en kan "
    "worden opgenomen voor kwaliteits- en trainingsdoeleinden. Wilt u liever "
    "een mens spreken? Zeg dan 'medewerker'. Waarmee kan ik u helpen?"
)

# Spoken when the caller asks "Bent u echt?" / "Bent u een mens?". The agent
# never claims to be human (art. 50, hard rule in the system prompt).
HUMAN_CHECK_TEMPLATE = (
    "Nee, ik ben de digitale assistent van {client_name}. "
    "Maar uw bericht komt direct bij {owner_naam} terecht."
)


def render_disclosure(agent_naam: str, client_name: str) -> str:
    return DISCLOSURE_TEMPLATE.format(agent_naam=agent_naam, client_name=client_name)


def render_human_check(client_name: str, owner_naam: str) -> str:
    return HUMAN_CHECK_TEMPLATE.format(client_name=client_name, owner_naam=owner_naam)
