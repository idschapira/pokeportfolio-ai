"""
Standalone smoke test for the Firestore repository (persistence/firestore_repo.py).

Validates a real save -> read -> cleanup round trip against Firestore
(ADC auth, GOOGLE_CLOUD_PROJECT from the environment) before wiring the
repo into the agent's save/portfolio tools.

Run: uv run python scripts/smoke_test_firestore.py
"""

from __future__ import annotations

import os
import sys
import uuid
from datetime import UTC, datetime

from dotenv import load_dotenv
from google.api_core.exceptions import PermissionDenied, Unauthenticated
from google.auth.exceptions import DefaultCredentialsError, RefreshError
from google.cloud.firestore_v1.base_query import FieldFilter

from models.models import Card, Price
from persistence import firestore_repo

_AUTH_HELP = (
    "Authentication problem talking to Firestore (ADC). This script does not "
    "attempt to log in — see _mentoria/AUTENTICACAO.md and re-authenticate, "
    "then re-run."
)

_TEST_USER_ID = "default"


def main() -> int:
    load_dotenv()

    if not os.environ.get("GOOGLE_CLOUD_PROJECT"):
        print("Error: GOOGLE_CLOUD_PROJECT is not set in the environment.")
        return 1

    # Unique marker so this run's test doc can't collide with a previous one.
    test_name = f"Smoke Test Card {uuid.uuid4().hex[:8]}"
    test_card = Card(
        card_id="smoke-test-card",
        name=test_name,
        set="Smoke Test Set",
        number="1",
        quantity=1,
        condition="NM",
        language="EN",
        grading=None,
        source="manual",
        status="resolved",
        added_price=None,
        current_price=Price(value=1.23, currency="USD", source="smoke-test", fetched_at=datetime.now(UTC)),
        added_at=datetime.now(UTC),
    )

    doc_ids: list[str] = []
    found = False
    try:
        doc_ids = firestore_repo.save_cards([test_card], user_id=_TEST_USER_ID)
        print(f"saved {len(doc_ids)}")

        portfolio = firestore_repo.get_portfolio(user_id=_TEST_USER_ID)
        found = any(card.name == test_name for card in portfolio.cards)
        print(f"portfolio has the test card: {found}")
    except (DefaultCredentialsError, RefreshError, Unauthenticated, PermissionDenied):
        print(_AUTH_HELP)
        return 1
    finally:
        # Best-effort cleanup: never leave test data behind. Swallow auth
        # errors here too so a broken ADC surfaces via the message above,
        # not as an unhandled traceback from this cleanup step.
        try:
            _cleanup(doc_ids, test_card.card_id)
        except (DefaultCredentialsError, RefreshError, Unauthenticated, PermissionDenied):
            pass

    return 0 if found else 1


def _cleanup(doc_ids: list[str], test_card_id: str) -> None:
    client = firestore_repo._get_client()
    for doc_id in doc_ids:
        client.collection("users", _TEST_USER_ID, "cards").document(doc_id).delete()
    for doc in (
        client.collection("users", _TEST_USER_ID, "price_history")
        .where(filter=FieldFilter("card_id", "==", test_card_id))
        .stream()
    ):
        doc.reference.delete()
    print("cleaned up")


if __name__ == "__main__":
    sys.exit(main())
