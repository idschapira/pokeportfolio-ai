"""
ADK tool functions registered on the root agent.

Tools:
  - save_cards(items) : writes resolved+priced cards to Firestore
  - get_portfolio()   : reads the saved collection + total value

Confirmation gate for save_cards: ADK 2.3.0's FunctionTool has a native
require_confirmation mechanism (verified in
.venv/.../google/adk/tools/function_tool.py) where the *runtime* pauses a
tool call and requires an explicit human ToolConfirmation before the
wrapped function ever executes — the LLM cannot forge this by passing an
argument. agent.py registers save_cards via
`FunctionTool(func=save_cards, require_confirmation=True)` to use this
native path instead of a `confirmed: bool` parameter, so the write is
refused in code regardless of what the prompt/LLM claims.
"""

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel

from models.models import Card, Condition, Grading, Price
from persistence import firestore_repo


class ResolvedCardItem(BaseModel):
    """One card item ready to persist: fields from resolve_card + a Price from get_price."""

    card_id: str | None
    name: str
    set: str | None = None
    number: str | None = None
    quantity: int = 1
    condition: Condition | None = None
    language: str | None = None
    grading: Grading | None = None
    price: Price


async def save_cards(items: list[ResolvedCardItem]) -> dict:
    """Persist a confirmed batch of resolved, priced cards to the user's portfolio.

    Only reached once the ADK runtime's tool-confirmation gate has approved
    this call (see module docstring) — by the time this function body runs,
    the write is already authorized, so it always actually happens.
    """
    now = datetime.now(UTC)
    cards = [
        Card(
            card_id=item.card_id,
            name=item.name,
            set=item.set,
            number=item.number,
            quantity=item.quantity,
            condition=item.condition,
            language=item.language,
            grading=item.grading,
            source="auto",
            status="resolved",
            added_price=item.price,
            current_price=item.price,
            added_at=now,
        )
        for item in items
    ]
    doc_ids = firestore_repo.save_cards(cards)
    return {"saved_count": len(doc_ids), "doc_ids": doc_ids}


async def get_portfolio() -> dict:
    """Read the user's saved card portfolio and total value.

    Read-only: does not call get_price to refresh current_price, it just
    reports what's already stored (per Especificacao_Tecnica.md §3).
    """
    portfolio = firestore_repo.get_portfolio()
    return portfolio.model_dump(mode="json")
