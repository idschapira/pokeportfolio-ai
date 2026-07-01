"""
Firestore repository — the only layer allowed to read/write the database.

Collections:
  - users/{userId}/cards/{cardDocId}   : card documents
  - users/{userId}/price_history/{id}  : price time series

Single-user MVP: userId is always "default".
"""

from __future__ import annotations

import os
from datetime import UTC, datetime

from dotenv import load_dotenv
from google.cloud import firestore

from models.models import Card, Portfolio

_client: firestore.Client | None = None


def _get_client() -> firestore.Client:
    """Lazily create the Firestore client (uses ADC — no API key involved).

    Lazy so importing this module never touches the network or requires
    GOOGLE_CLOUD_PROJECT to be set unless a repo function is actually called.
    """
    global _client
    if _client is None:
        load_dotenv()
        project = os.environ.get("GOOGLE_CLOUD_PROJECT")
        if not project:
            raise RuntimeError(
                "Missing required environment variable: GOOGLE_CLOUD_PROJECT"
            )
        _client = firestore.Client(project=project)
    return _client


def save_cards(cards: list[Card], user_id: str = "default") -> list[str]:
    """Persist each card at users/{user_id}/cards, returning the new doc IDs.

    Cards that carry a current_price also get a price_history point (schema:
    {card_id, date, price, currency}, per Especificacao_Tecnica.md §5).
    """
    client = _get_client()
    cards_collection = client.collection("users", user_id, "cards")
    price_history_collection = client.collection("users", user_id, "price_history")

    doc_ids = []
    for card in cards:
        doc_ref = cards_collection.document()
        doc_ref.set(card.model_dump())
        doc_ids.append(doc_ref.id)

        if card.current_price is not None:
            price_history_collection.document().set(
                {
                    "card_id": card.card_id,
                    "date": card.current_price.fetched_at,
                    "price": card.current_price.value,
                    "currency": card.current_price.currency,
                }
            )

    return doc_ids


def get_portfolio(user_id: str = "default") -> Portfolio:
    """Read users/{user_id}/cards and build a Portfolio with the total value.

    Reads only what's already stored — refreshing current_price via get_price
    is the tool layer's job, not this repo's.
    """
    client = _get_client()
    docs = client.collection("users", user_id, "cards").stream()

    cards = [Card(**doc.to_dict()) for doc in docs]
    total_value = sum(
        card.current_price.value * card.quantity
        for card in cards
        if card.current_price is not None
    )

    return Portfolio(
        cards=cards,
        total_value=total_value,
        updated_at=datetime.now(UTC),
    )
