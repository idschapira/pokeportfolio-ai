"""
Pydantic models — single source of truth for data contracts shared across
agent, mcp_server, and persistence layers.

Planned models:
  - Card          : persisted card document (matches Firestore schema)
  - CardInput     : raw item extracted from user text (pre-resolution)
  - Candidate     : card candidate returned by resolve_card (MCP)
  - Price         : price snapshot {value, currency, source, fetched_at}
  - Grading       : grading info {company, grade}
  - Portfolio     : aggregated view of a user's collection + total value
"""

# TODO: implement models using Pydantic BaseModel
