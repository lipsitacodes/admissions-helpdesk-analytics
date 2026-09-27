"""MongoDB logging for helpdesk interaction metadata."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from backend.database import get_database


def _sqlite_log_interaction(
    database_path: Path,
    *,
    query: str,
    predicted_intent: str,
    classifier_confidence: float,
    source_document: Optional[str],
    retrieval_similarity: Optional[float],
    escalated: bool,
    escalation_reason: Optional[str],
) -> None:
    with sqlite3.connect(database_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS helpdesk_interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                query TEXT NOT NULL,
                predicted_intent TEXT NOT NULL,
                classifier_confidence REAL NOT NULL,
                source_document TEXT,
                retrieval_similarity REAL,
                escalated INTEGER NOT NULL,
                escalation_reason TEXT
            )
            """
        )
        conn.execute(
            """
            INSERT INTO helpdesk_interactions (
                timestamp, query, predicted_intent, classifier_confidence,
                source_document, retrieval_similarity, escalated, escalation_reason
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.now(timezone.utc).isoformat(),
                query,
                predicted_intent,
                float(classifier_confidence),
                source_document,
                retrieval_similarity,
                int(escalated),
                escalation_reason,
            ),
        )


def log_interaction(
    *,
    query: str,
    predicted_intent: str,
    classifier_confidence: float,
    source_document: Optional[str],
    retrieval_similarity: Optional[float],
    escalated: bool,
    escalation_reason: Optional[str],
    database_path: Optional[Path] = None,
    **kwargs: Any,
) -> None:
    """Save one helpdesk interaction in MongoDB without failing the API."""
    if database_path is not None:
        _sqlite_log_interaction(
            database_path,
            query=query,
            predicted_intent=predicted_intent,
            classifier_confidence=classifier_confidence,
            source_document=source_document,
            retrieval_similarity=retrieval_similarity,
            escalated=escalated,
            escalation_reason=escalation_reason,
        )
        return

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