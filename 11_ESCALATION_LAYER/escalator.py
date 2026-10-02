"""Phase 12: Unified Escalation Layer Interface.

Evaluates confidence check:
If confidence meets threshold -> ANSWER
If confidence is low / escalation trigger met -> ESCALATE
"""

from typing import Any, Dict
from .rules.escalation_rules import evaluate_escalation_triggers
from .escalation.ticket_generator import create_escalation_ticket


def process_confidence_and_escalation(
    query_data: Dict[str, Any],
    answer_data: Dict[str, Any],
    confidence_threshold: float = 0.50,
) -> Dict[str, Any]:
    """Perform confidence check and route to ANSWER or ESCALATION."""
    route = query_data.get("route", "INSTITUTIONAL_QUERY")
    confidence = answer_data.get("confidence", 0.0)
    retrieved_chunks = query_data.get("retrieved_context", [])
    query = query_data.get("original_query", "")
    target_course = query_data.get("query_plan", {}).get("course")

    should_escalate, reasons = evaluate_escalation_triggers(
        route=route,
        confidence=confidence,
        retrieved_chunks=retrieved_chunks,
        confidence_threshold=confidence_threshold,
    )

    ticket = None
    if should_escalate:
        ticket = create_escalation_ticket(
            query=query,
            reasons=reasons,
            confidence=confidence,
            course=target_course,
        )

    return {
        "should_escalate": should_escalate,
        "escalation_reasons": reasons,
        "confidence": confidence,
        "decision": "ESCALATION" if should_escalate else "ANSWER",
        "ticket": ticket,
    }
