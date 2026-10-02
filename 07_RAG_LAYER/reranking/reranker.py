"""Phase 8: Metadata Filtering & Multi-Signal Reranker.

Reranks semantic candidates using institutional signals:
1. Course exact & fuzzy alignment
2. Academic category match
3. Campus location match
4. Intent semantic alignment (e.g. fees intent -> fees section chunk)
5. Base semantic vector similarity
"""

from typing import Any, Dict, List, Optional, Tuple


def rerank_and_filter(
    candidates: List[Tuple[Dict[str, Any], float]],
    target_course: Optional[str] = None,
    target_category: Optional[str] = None,
    target_campuses: Optional[List[str]] = None,
    target_intents: Optional[List[str]] = None,
    top_k: int = 5,
) -> List[Dict[str, Any]]:
    """Rerank candidates using metadata filters and heuristic feature scores."""
    reranked = []
    target_campuses = target_campuses or []
    target_intents = target_intents or []

    has_institutional_signals = bool(
        target_course or target_category or target_campuses or (target_intents and any(i in target_intents for i in ("fees", "hostel", "faculty", "eligibility", "admission", "scholarship")))
    )

    for chunk, base_sim in candidates:
        # Filter out candidates if query has no recognized admissions entities and semantic similarity is low
        if not has_institutional_signals and base_sim < 0.42:
            continue

        score = base_sim

        chunk_course = chunk.get("course", "").lower()
        chunk_category = chunk.get("category", "").lower()
        chunk_section = chunk.get("section_type", "").lower()
        chunk_campuses = [c.lower() for c in chunk.get("campuses", [])]

        # 1. Course Match Signal (+0.35 if exact match)
        if target_course:
            t_course_lower = target_course.lower()
            if chunk_course == t_course_lower:
                score += 0.35
            elif t_course_lower in chunk_course or chunk_course in t_course_lower:
                score += 0.20

        # 2. Category Match Signal (+0.15)
        if target_category:
            if chunk.get("academic_category", "").lower() == target_category.lower():
                score += 0.15

        # 3. Campus Match Signal (+0.20)
        if target_campuses:
            for campus in target_campuses:
                if campus.lower() in chunk_campuses or campus.lower() in chunk.get("text", "").lower():
                    score += 0.20
                    break

        # 4. Intent Alignment Signal (+0.25)
        if target_intents:
            for intent in target_intents:
                if intent == "fees" and chunk_section == "fees":
                    score += 0.25
                elif intent == "course_information" and chunk_section == "course_information":
                    score += 0.20
                elif intent == "faculty" and chunk_section == "faculty":
                    score += 0.30

        item = dict(chunk)
        item["rerank_score"] = float(round(score, 4))
        item["semantic_similarity"] = float(round(base_sim, 4))
        reranked.append(item)

    # Sort descending by rerank_score
    reranked.sort(key=lambda x: x["rerank_score"], reverse=True)
    return reranked[:top_k]


if __name__ == "__main__":
    sample_candidate = ({"course": "B Sc Hons Agriculture", "category": "Agriculture", "section_type": "fees"}, 0.75)
    reranked = rerank_and_filter([sample_candidate], target_course="B Sc Hons Agriculture", target_intents=["fees"])
    print(f"[OK] Reranker tested successfully. Top score: {reranked[0]['rerank_score']}")
