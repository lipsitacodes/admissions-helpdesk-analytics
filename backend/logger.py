"""MongoDB logging and persistence for helpdesk interactions, conversations, and escalation tickets."""

from __future__ import annotations

import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from backend.database import get_database

logger = logging.getLogger(__name__)


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
    session_id: Optional[str] = None,
    candidate_name: Optional[str] = None,
    answer: Optional[str] = None,
    grounded: bool = True,
    ticket: Optional[Dict[str, Any]] = None,
    cleaned_query: Optional[str] = None,
    target_language: Optional[str] = None,
    detected_language: Optional[str] = None,
    response_time_sec: Optional[float] = None,
    accuracy_percentage: Optional[float] = None,
    database_path: Optional[Path] = None,
    **kwargs: Any,
) -> None:
    """Save the interaction, update conversation session, and record escalation tickets in MongoDB."""
    # Test Isolation: when test passes a local sqlite db path
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
        now = datetime.now(timezone.utc)
        now_iso = now.isoformat()

        acc_pct = (
            float(accuracy_percentage)
            if accuracy_percentage is not None
            else round(float(classifier_confidence) * 100.0, 1)
        )
        resp_time = (
            round(float(response_time_sec), 2)
            if response_time_sec is not None
            else 0.25
        )

        # 1. Audit Log: helpdesk_interactions
        interaction_doc = {
            "timestamp": now,
            "session_id": session_id,
            "candidate_name": candidate_name or "Student",
            "query": query,
            "cleaned_query": cleaned_query or query,
            "answer": answer,
            "accuracy_percentage": acc_pct,
            "response_time_sec": resp_time,
            "target_language": target_language or "en",
            "detected_language": detected_language or "English",
            "classifier_confidence": float(classifier_confidence),
            "predicted_intent": predicted_intent,
            "source_document": source_document,
            "retrieval_similarity": float(retrieval_similarity) if retrieval_similarity is not None else None,
            "grounded": bool(grounded),
            "escalated": bool(escalated),
            "escalation_reason": escalation_reason,
        }
        db["helpdesk_interactions"].insert_one(interaction_doc)

        # 2. Multi-turn Session History: helpdesk_conversations
        if session_id:
            chat_title = query.strip()
            if len(chat_title) > 36:
                chat_title = chat_title[:36].strip() + "..."

            msg_entries = [
                {
                    "role": "user",
                    "content": query,
                    "timestamp": now_iso,
                    "language": target_language or "en",
                }
            ]

            if answer:
                msg_entries.append(
                    {
                        "role": "assistant",
                        "content": answer,
                        "timestamp": now_iso,
                        "metadata": {
                            "predicted_intent": predicted_intent,
                            "classifier_confidence": float(classifier_confidence),
                            "accuracy_percentage": acc_pct,
                            "response_time_sec": resp_time,
                            "target_language": target_language or "en",
                            "detected_language": detected_language or "English",
                            "source_document": source_document,
                            "grounded": bool(grounded),
                            "escalated": bool(escalated),
                        },
                    }
                )

            update_data: Dict[str, Any] = {
                "updated_at": now,
                "latest_query": query,
                "latest_answer": answer,
                "target_language": target_language or "en",
                "candidate_name": candidate_name or "Student",
                "last_accuracy_percentage": acc_pct,
                "last_response_time_sec": resp_time,
                "last_confidence": float(classifier_confidence),
            }

            db["helpdesk_conversations"].update_one(
                {"conversation_id": session_id},
                {
                    "$setOnInsert": {
                        "conversation_id": session_id,
                        "created_at": now,
                        "title": chat_title,
                    },
                    "$set": update_data,
                    "$push": {
                        "messages": {"$each": msg_entries}
                    },
                },
                upsert=True,
            )

        # 3. Escalation Ticket Collection: escalation_tickets
        if escalated and ticket:
            ticket_doc = {
                "ticket_id": ticket.get("ticket_id"),
                "session_id": session_id,
                "candidate_name": candidate_name or "Student",
                "query": query,
                "course_context": ticket.get("course_context"),
                "confidence": float(ticket.get("confidence", classifier_confidence)),
                "escalation_reasons": ticket.get("escalation_reasons", [escalation_reason]),
                "assigned_department": ticket.get("assigned_department", "Centurion Admissions & Student Affairs"),
                "admissions_helpline": ticket.get("admissions_helpline", "8260077222"),
                "admissions_email": ticket.get("admissions_email", "admissions@cutm.ac.in"),
                "status": ticket.get("status", "pending_human_review"),
                "created_at": now,
            }
            db["escalation_tickets"].insert_one(ticket_doc)

    except Exception as exc:
        # Atlas logging should be fail-safe; network blips will not break user answering flow
        logger.warning("MongoDB logging notice: %s", exc)