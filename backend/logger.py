"""Minimal SQLite logging for non-sensitive helpdesk interaction metadata."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

ROOT_DIR = Path(__file__).resolve().parents[1]
DATABASE_PATH = ROOT_DIR / "data" / "helpdesk_interactions.db"


def initialize_database(database_path: Path = DATABASE_PATH) -> None:
    """Create the interaction-log table when it does not already exist."""
    database_path.parent.mkdir(parents=True, exist_ok=True)
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
                escalation_reason TEXT
            )
            """
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
    database_path: Path = DATABASE_PATH,
) -> None:
    """Write one helpdesk interaction without accessing student-record data."""
    initialize_database(database_path)
    timestamp = datetime.now(timezone.utc).isoformat()
    with sqlite3.connect(database_path) as connection:
        connection.execute(
            """
            INSERT INTO helpdesk_interactions (
                timestamp, query, predicted_intent, classifier_confidence,
                source_document, retrieval_similarity, escalated, escalation_reason
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
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
            ),
        )
