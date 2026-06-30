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

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel

Condition = Literal["NM", "LP", "MP", "HP", "DMG"]


class Grading(BaseModel):
    """Third-party grading info for a card (company + numeric grade)."""

    company: Literal["PSA", "CGC"]
    grade: float


class Price(BaseModel):
    """A price snapshot for a card, captured from a given source at a point in time."""

    value: float
    currency: str = "USD"
    source: str
    fetched_at: datetime


class CardInput(BaseModel):
    """Raw item extracted from free-text user input, before resolving against the card API."""

    raw_text: str
    name: str
    set: str | None = None
    number: str | None = None
    quantity: int = 1
    condition: Condition | None = None
    language: str | None = None
    grading: Grading | None = None


class Candidate(BaseModel):
    """A candidate card match returned by the resolve_card MCP tool."""

    card_id: str
    name: str
    set: str
    number: str
    rarity: str | None = None
    image_url: str | None = None
    match_score: float


class Card(BaseModel):
    """A card document persisted at users/{userId}/cards/{cardDocId} in Firestore."""

    card_id: str | None
    name: str
    set: str | None = None
    number: str | None = None
    quantity: int
    condition: Condition | None = None
    language: str | None = None
    grading: Grading | None = None
    source: Literal["auto", "manual"]
    status: Literal["resolved", "unresolved"]
    added_price: Price | None = None
    current_price: Price | None = None
    added_at: datetime


class Portfolio(BaseModel):
    """Aggregated view of a user's card collection and its total value."""

    cards: list[Card]
    total_value: float
    currency: str = "USD"
    updated_at: datetime
