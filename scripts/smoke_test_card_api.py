"""
Standalone smoke test for the card API (pokemontcg.io, now under Scrydex).

Validates that CARD_API_KEY / CARD_API_BASE_URL work end-to-end with a real
request before mcp_server/card_api.py is implemented in Phase 1.

Run: uv run python scripts/smoke_test_card_api.py
"""

from __future__ import annotations

import os
import sys

import httpx
from dotenv import load_dotenv


def main() -> int:
    load_dotenv()

    api_key = os.environ.get("CARD_API_KEY", "")
    base_url = os.environ.get("CARD_API_BASE_URL", "")

    if not api_key or not base_url:
        print("Error: CARD_API_KEY and/or CARD_API_BASE_URL is not set in the environment.")
        return 1

    try:
        response = httpx.get(
            f"{base_url}/cards",
            params={"q": "name:charizard", "pageSize": 1},
            headers={"X-Api-Key": api_key},
            timeout=15.0,
        )
    except httpx.HTTPError as exc:
        print(f"Request failed: {type(exc).__name__}")
        return 1

    print(f"Status code: {response.status_code}")

    if response.status_code != 200:
        return 1

    data = response.json()
    results = data.get("data", [])
    count = data.get("count", len(results))
    print(f"Result count: {count}")

    if results:
        print(f"First card name: {results[0].get('name')}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
