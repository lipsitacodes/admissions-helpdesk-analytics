"""Interaction logging for the helpdesk API.

This project uses MongoDB for the production path, while keeping a SQLite
fallback for tests and local debugging when a temporary ``database_path`` is
provided.
"""

from __future__ import annotations

import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from database import get_database

logger = logging.getLogger(__name__)

DATABASE_PATH = Path(__file__).resolve().parent.parent / "data" / "helpdesk_logs.db"


def initialize_database(database_path: Path = DATABASE_PATH) -> None:
    """Create support table if a legacy SQLite fallback is used."""
    with sqlite3.connect(database_path) as connection:
        connection.execute(
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
                escalation_reason TEXT,
                cleaned_query TEXT,
                answer TEXT,
                grounded INTEGER,
                response_metadata TEXT
            )
            """
        )


def _sqlite_log_interaction(
    *,
    query: str,
    predicted_intent: str,
    classifier_confidence: float,
    source_document: Optional[str],
    retrieval_similarity: Optional[float],
    escalated: bool,
    escalation_reason: Optional[str],
    cleaned_query: Optional[str] = None,
    answer: Optional[str] = None,
    grounded: Optional[bool] = None,
    response_metadata: Optional[Dict[str, Any]] = None,
    database_path: Path = DATABASE_PATH,
) -> None:
    """Store a local SQLite record when tests or fallback flows need it."""
    initialize_database(database_path)
    timestamp = datetime.now(timezone.utc).isoformat()
    with sqlite3.connect(database_path) as connection:
        connection.execute(
            """
            INSERT INTO helpdesk_interactions (
                timestamp, query, predicted_intent, classifier_confidence,
                source_document, retrieval_similarity, escalated, escalation_reason,
                cleaned_query, answer, grounded, response_metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                timestamp,
                query,
                predicted_intent,
                float(classifier_confidence),
                source_document,
                retrieval_similarity,
                int(escalated),
                escalation_reason,
                cleaned_query,
                answer,
                int(bool(grounded)) if grounded is not None else None,
                str(response_metadata) if response_metadata is not None else None,
            ),
        )


def _mongo_log_interaction(
    *,
    query: str,
    predicted_intent: str,
    classifier_confidence: float,
    source_document: Optional[str],
    retrieval_similarity: Optional[float],
    escalated: bool,
    escalation_reason: Optional[str],
    cleaned_query: Optional[str] = None,
    answer: Optional[str] = None,
    grounded: Optional[bool] = None,
    response_metadata: Optional[Dict[str, Any]] = None,
    collection_name: str = "helpdesk_interactions",
) -> None:
    """Persist one interaction to MongoDB Atlas using the configured database."""
    document: Dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc),
        "query": query,
        "cleaned_query": cleaned_query,
        "predicted_intent": predicted_intent,
        "classifier_confidence": float(classifier_confidence),
        "source_document": source_document,
        "retrieval_similarity": retrieval_similarity,
        "escalated": bool(escalated),
        "escalation_reason": escalation_reason,
        "answer": answer,
        "grounded": bool(grounded) if grounded is not None else None,
    }
    if response_metadata:
        document["response_metadata"] = response_metadata
    db = get_database()
    collection = db[collection_name]
    result = collection.insert_one(document)
    logger.info("MongoDB interaction saved: %s", result.inserted_id)


def log_interaction(
    *,
    query: str,
    predicted_intent: str,
    classifier_confidence: float,
    source_document: Optional[str],
    retrieval_similarity: Optional[float],
    escalated: bool,
    escalation_reason: Optional[str],
    cleaned_query: Optional[str] = None,
    answer: Optional[str] = None,
    grounded: Optional[bool] = None,
    response_metadata: Optional[Dict[str, Any]] = None,
    database_path: Optional[Path] = None,
    collection_name: str = "helpdesk_interactions",
) -> None:
    """Write one interaction to MongoDB by default, with SQLite fallback only when forced."""
    if database_path is not None:
        _sqlite_log_interaction(
            query=query,
            predicted_intent=predicted_intent,
            classifier_confidence=classifier_confidence,
            source_document=source_document,
            retrieval_similarity=retrieval_similarity,
            escalated=escalated,
            escalation_reason=escalation_reason,
            cleaned_query=cleaned_query,
            answer=answer,
            grounded=grounded,
            response_metadata=response_metadata,
            database_path=database_path,
        )
        return

    _mongo_log_interaction(
        query=query,
        predicted_intent=predicted_intent,
        classifier_confidence=classifier_confidence,
        source_document=source_document,
        retrieval_similarity=retrieval_similarity,
        escalated=escalated,
        escalation_reason=escalation_reason,
        cleaned_query=cleaned_query,
        answer=answer,
        grounded=grounded,
        response_metadata=response_metadata,
        collection_name=collection_name,
    )

