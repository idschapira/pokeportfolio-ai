"""
MCP server — exposes resolve_card and get_price tools to the ADK agent.

Tools:
  - resolve_card(text: str) -> list[Candidate]
      Matches free-text card description against the pokemontcg.io catalogue
      and returns ranked candidates.
  - get_price(card_id: str) -> Price
      Fetches the current market price for a canonical card_id.
"""

# TODO: implement MCP server using FastMCP (mcp SDK)
# TODO: register resolve_card and get_price as MCP tools
# TODO: wire card_api.py as the HTTP backend
