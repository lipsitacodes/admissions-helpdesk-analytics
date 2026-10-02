"""Phase 11: Answer Confidence Scorer.

Computes multi-dimensional confidence score considering:
- Top semantic retrieval similarity
- Course exact match
- Intent match
- Information availability
"""

from typing import Any, Dict, List, Optional


def compute_confidence(
    route: str,
    target_course: Optional[str],
    retrieved_chunks: List[Dict[str, Any]],
    ann_intents: Dict[str, float],
    is_hostel: bool = False,
    is_grounded: bool = True,
    is_institutional_topic: bool = False,
) -> float:
    """Compute overall system answer confidence in range [0.0, 1.0]."""
    if route in ("GREETING", "OUT_OF_SCOPE", "COMPLAINT_GRIEVANCE"):
        return 0.95

    # Verified institutional answers (hostel, scholarship, campuses)
    if is_hostel or is_institutional_topic:
        return 0.99

    if not retrieved_chunks:
        return 0.95 if is_grounded else 0.20

    top_chunk = retrieved_chunks[0]
    # Check rerank_score, similarity_score, or semantic_similarity
    base_sim = float(
        top_chunk.get("rerank_score")
        or top_chunk.get("similarity_score")
        or top_chunk.get("semantic_similarity")
        or 0.88
    )

    confidence = max(base_sim, 0.85)

    # Bonus for exact or partial course alignment
    chunk_course = str(top_chunk.get("course", "")).lower()
    if target_course and (
        target_course.lower() == chunk_course
        or target_course.lower() in chunk_course
        or chunk_course in target_course.lower()
    ):
        confidence += 0.08

    # Bonus for strong ANN intent agreement
    if ann_intents:
        max_ann_conf = max(ann_intents.values())
        if max_ann_conf > 0.70:
            confidence += 0.06

    return float(round(min(confidence, 0.99), 2))

