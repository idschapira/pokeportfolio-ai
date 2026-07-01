"""
HTTP client for the pokemontcg.io API (Scrydex).

Responsibilities:
  - Search cards by name/set/number via GET /cards
  - Fetch price data (TCGPlayer market price) for a given card_id
  - Authenticate with CARD_API_KEY from environment (never hardcoded)
  - Base URL read from CARD_API_BASE_URL environment variable

No MCP tool wiring here — this module is pure HTTP access. A new
httpx.AsyncClient is opened per call (simplicity over connection reuse,
since call volume here is low).
"""

from __future__ import annotations

import asyncio
import os
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from typing import TypeVar

import httpx
from dotenv import load_dotenv

load_dotenv()

CARD_API_KEY = os.environ.get("CARD_API_KEY")
CARD_API_BASE_URL = os.environ.get("CARD_API_BASE_URL")

if not CARD_API_KEY:
    raise RuntimeError("Missing required environment variable: CARD_API_KEY")
if not CARD_API_BASE_URL:
    raise RuntimeError("Missing required environment variable: CARD_API_BASE_URL")

_TIMEOUT = 15.0
_MAX_ATTEMPTS = 3
_BACKOFF_SECONDS = (0.5, 1.0, 2.0)

# Variants checked in order of how commonly they carry a market price.
_PRICE_VARIANTS = (
    "normal",
    "holofoil",
    "reverseHolofoil",
    "1stEditionHolofoil",
    "1stEditionNormal",
    "unlimitedHolofoil",
)

T = TypeVar("T")


async def _with_retry(call: Callable[[], Awaitable[T]]) -> T:
    """Retry a request up to _MAX_ATTEMPTS times with exponential backoff.

    The card API has shown intermittent ReadTimeout/ConnectError under normal
    load (observed in Phase 0/1 smoke testing) even with a generous timeout,
    so transient network errors are retried rather than failing the caller
    immediately.
    """
    for attempt in range(_MAX_ATTEMPTS):
        try:
            return await call()
        except (httpx.ReadTimeout, httpx.ConnectError):
            if attempt == _MAX_ATTEMPTS - 1:
                raise
            await asyncio.sleep(_BACKOFF_SECONDS[attempt])
    raise AssertionError("unreachable")  # loop always returns or raises


async def search_cards(
    name: str,
    set_name: str | None = None,
    number: str | None = None,
    page_size: int = 10,
) -> list[dict]:
    """Search cards by name/set/number using the API's Lucene query syntax."""
    # Quote each value so spaces/special chars don't break the Lucene query.
    terms = [f'name:"{name}"']
    if set_name:
        terms.append(f'set.name:"{set_name}"')
    if number:
        terms.append(f'number:"{number}"')
    query = " ".join(terms)

    async def _call() -> httpx.Response:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            return await client.get(
                f"{CARD_API_BASE_URL}/cards",
                params={"q": query, "pageSize": page_size},
                headers={"X-Api-Key": CARD_API_KEY},
            )

    response = await _with_retry(_call)
    response.raise_for_status()
    return response.json().get("data", [])


async def get_card_price(card_id: str) -> dict | None:
    """Fetch a card's TCGPlayer market price, if available."""

    async def _call() -> httpx.Response:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            return await client.get(
                f"{CARD_API_BASE_URL}/cards/{card_id}",
                headers={"X-Api-Key": CARD_API_KEY},
            )

    response = await _with_retry(_call)
    response.raise_for_status()
    card = response.json().get("data", {})

    prices = card.get("tcgplayer", {}).get("prices", {})
    # Prices are split by print variant (normal, holofoil, ...); use the
    # first variant that actually has a market price.
    for variant in _PRICE_VARIANTS:
        market = prices.get(variant, {}).get("market")
        if market is not None:
            return {
                "value": float(market),
                "currency": "USD",
                "source": "tcgplayer",
                "fetched_at": datetime.now(UTC).isoformat(),
            }

    return None
