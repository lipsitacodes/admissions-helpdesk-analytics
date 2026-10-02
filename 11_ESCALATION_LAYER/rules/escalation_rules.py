"""Phase 12: Escalation Rules.

Explicit escalation triggers based on institutional HOD guidelines:
1. Low retrieval confidence
2. Out-of-scope query
3. Sensitive / grievance / complaint query
4. Repeated query failure / missing knowledge records
"""

from typing import Any, Dict, List, Optional, Tuple


def evaluate_escalation_triggers(
    route: str,
    confidence: float,
    retrieved_chunks: List[Dict[str, Any]],
    confidence_threshold: float = 0.50,
) -> Tuple[bool, List[str]]:
    """Determine if a query requires human / admissions office escalation."""
    # Unwanted / Out-of-scope queries do not need to be managed or escalated
    if route == "OUT_OF_SCOPE":
        return False, []

    reasons = []

    if route == "COMPLAINT_GRIEVANCE":
        reasons.append("sensitive_complaint_grievance")

    if not retrieved_chunks and route == "INSTITUTIONAL_QUERY" and confidence < 0.95:
        reasons.append("insufficient_institutional_knowledge")

    if confidence < confidence_threshold and route not in ("GREETING", "OUT_OF_SCOPE"):
        reasons.append("low_retrieval_confidence")

    should_escalate = len(reasons) > 0
    return should_escalate, reasons
