"""
MCP server — exposes resolve_card and get_price tools to the ADK agent.

Tools:
  - resolve_card(name, set_name=None, number=None) -> list[dict]
      Matches a card description against the pokemontcg.io catalogue and
      returns ranked Candidate dicts.
  - get_price(card_id) -> dict | None
      Fetches the current market price for a canonical card_id.

Retry-with-backoff for the underlying HTTP calls lives in card_api.py
(_with_retry), not here — these tools just call search_cards/get_card_price
and shape the results.
"""

from __future__ import annotations

from difflib import SequenceMatcher

from mcp.server.fastmcp import FastMCP

from mcp_server.card_api import get_card_price, search_cards
from models.models import Candidate, Price

mcp = FastMCP("pokeportfolio-cards")


def _match_score(query_name: str, candidate_name: str) -> float:
    """Similarity between the requested name and a candidate's name (0-1).

    Simple case-insensitive ratio via difflib.SequenceMatcher — good enough
    to rank near-duplicates (e.g. "charizard" vs "Charizard ex") without
    pulling in a fuzzy-matching dependency.
    """
    return SequenceMatcher(None, query_name.lower(), candidate_name.lower()).ratio()


@mcp.tool()
async def resolve_card(
    name: str, set_name: str | None = None, number: str | None = None
) -> list[dict]:
    """Search the card catalogue and return ranked candidates for the given name/set/number."""
    raw_cards = await search_cards(name, set_name=set_name, number=number)

    candidates = [
        Candidate(
            card_id=card["id"],
            name=card["name"],
            set=card.get("set", {}).get("name", ""),
            number=card.get("number", ""),
            rarity=card.get("rarity"),
            image_url=card.get("images", {}).get("small"),
            match_score=_match_score(name, card["name"]),
        )
        for card in raw_cards
    ]
    candidates.sort(key=lambda c: c.match_score, reverse=True)

    return [c.model_dump() for c in candidates]


@mcp.tool()
async def get_price(card_id: str) -> dict | None:
    """Fetch the current market price for a card_id, validated against the Price model."""
    price_data = await get_card_price(card_id)
    if price_data is None:
        return None
    return Price(**price_data).model_dump()


if __name__ == "__main__":
    mcp.run()
