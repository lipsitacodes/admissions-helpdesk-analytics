"""Phase 12: Escalation Ticket & Contact Generator.

Generates escalation package with admission helpline: 8260077222 and official emails.
"""

from typing import Any, Dict, List
import uuid
from datetime import datetime


def create_escalation_ticket(
    query: str,
    reasons: List[str],
    confidence: float,
    course: str = None,
) -> Dict[str, Any]:
    """Create structured escalation record."""
    ticket_id = f"ESC-{uuid.uuid4().hex[:8].upper()}"
    return {
        "ticket_id": ticket_id,
        "timestamp": datetime.now().isoformat(),
        "query": query,
        "course_context": course,
        "confidence": confidence,
        "escalation_reasons": reasons,
        "assigned_department": "Centurion Admissions & Student Affairs",
        "admissions_helpline": "8260077222",
        "admissions_email": "admissions@cutm.ac.in",
        "status": "pending_human_review",
    }
