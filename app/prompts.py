"""
System prompt and instruction strings for the root agent.

Keeps the agent's personality, rules, and step-by-step instructions
separated from agent wiring in agent.py.
"""

# Placeholder instruction — the full flow (entity extraction, ambiguity
# resolution, confirmation before save_cards) lands in a later Phase 1 step.
ROOT_AGENT_INSTRUCTION = (
    "You are PokéPortfolio, a concierge assistant that catalogues Pokémon "
    "cards. Use resolve_card to match card descriptions and get_price to "
    "fetch prices."
)

# TODO: expand ROOT_AGENT_INSTRUCTION (ambiguity flow, confirmation rule,
#       save_cards only after explicit user approval)
