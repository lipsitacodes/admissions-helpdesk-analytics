"""MongoDB logging for helpdesk interaction metadata."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from database import get_database


def log_interaction(
    *,
    query: str,
    predicted_intent: str,
    classifier_confidence: float,
    source_document: Optional[str],
    retrieval_similarity: Optional[float],
    escalated: bool,
    escalation_reason: Optional[str],
) -> None:
    """Save one helpdesk interaction in MongoDB without failing the API."""

    try:
        db = get_database()
        interactions = db["helpdesk_interactions"]

        interaction = {
            "timestamp": datetime.now(timezone.utc),
            "query": query,
            "predicted_intent": predicted_intent,
            "classifier_confidence": float(classifier_confidence),
            "source_document": source_document,
            "retrieval_similarity": retrieval_similarity,
            "escalated": escalated,
            "escalation_reason": escalation_reason,
        }

        interactions.insert_one(interaction)
    except Exception:
        # Atlas may be temporarily unavailable; the API and RAG flow should keep
        # working without turning a logging outage into a user-visible escalation.
        return