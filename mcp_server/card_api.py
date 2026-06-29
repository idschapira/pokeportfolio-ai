"""
HTTP client for the pokemontcg.io API (Scrydex).

Responsibilities:
  - Search cards by name/set/number via GET /cards
  - Fetch price data (TCGPlayer market price) for a given card_id
  - Authenticate with CARD_API_KEY from environment (never hardcoded)
  - Base URL read from CARD_API_BASE_URL environment variable
"""

# TODO: implement async client using httpx
# TODO: define search_cards(query: str) -> list[dict]
# TODO: define get_card_price(card_id: str) -> dict
