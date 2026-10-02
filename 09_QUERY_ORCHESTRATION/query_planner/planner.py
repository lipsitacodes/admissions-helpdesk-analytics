"""Phase 10: Query Planner.

Constructs structured query execution plans defining:
- target_course
- target_academic_category
- target_campuses
- required_information (list of required information blocks, e.g. ['fees', 'hostel'])
"""

from typing import Any, Dict, List, Optional


class QueryPlanner:
    """Plans retrieval targets and information requirements."""

    def create_plan(
        self,
        course: Optional[str],
        academic_category: Optional[str],
        campuses: List[str],
        ann_intents: Dict[str, float],
        keyword_intents: List[str],
    ) -> Dict[str, Any]:
        """Synthesize entities and intents into an execution plan."""
        # Merge ANN intents and keyword intents with strict confidence gating
        required_blocks = []
        for intent in keyword_intents:
            if intent not in required_blocks and intent != "course_information":
                required_blocks.append(intent)

        sorted_ann = sorted(ann_intents.items(), key=lambda x: x[1], reverse=True)
        if not required_blocks:
            if sorted_ann and sorted_ann[0][1] >= 0.4:
                required_blocks.append(sorted_ann[0][0])
            else:
                required_blocks.append("course_information")
        else:
            # Secondary ANN intents only included if very high confidence (>= 0.80)
            for intent, score in sorted_ann:
                if intent not in required_blocks and score >= 0.80:
                    required_blocks.append(intent)

        return {
            "course": course,
            "academic_category": academic_category,
            "campuses": campuses,
            "required_information": required_blocks,
            "ann_confidence_scores": ann_intents,
        }
