"""
Firestore repository — the only layer allowed to read/write the database.

Collections:
  - users/{userId}/cards/{cardDocId}   : card documents
  - users/{userId}/price_history/{id}  : price time series

Single-user MVP: userId is always "default".
"""

# TODO: implement using google-cloud-firestore
# TODO: define save_cards(items: list[CardInput]) -> list[str]
# TODO: define get_portfolio(user_id: str) -> Portfolio
