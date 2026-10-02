"""Phase 7 & 8: RAG Retrieval Evaluation.

Evaluates:
- Recall@1, Recall@3, Recall@5
- Mean Reciprocal Rank (MRR)
- Retrieval Precision
Based on ground-truth queries mapped to canonical CUTM knowledge records.
"""

import sys
import json
from pathlib import Path
from typing import Dict, List
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR.parent
for p in (BASE_DIR, PROJECT_ROOT):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

try:
    from retriever import retrieve_context
except ImportError:
    try:
        # pyrefly: ignore [missing-import]
        from ..retriever import retrieve_context
    except (ImportError, ValueError):
        import importlib
        _ret_mod = importlib.import_module("07_RAG_LAYER.retriever")
        retrieve_context = _ret_mod.retrieve_context

EVAL_DIR = BASE_DIR / "evaluation"

# Representative evaluation query test set with expected course target
TEST_BENCHMARK = [
    {
        "query": "What is the fee for BSc Agriculture?",
        "expected_course": "B Sc Hons Agriculture",
        "expected_intent": "fees",
    },
    {
        "query": "BTech CSE Bhubaneswar fee structure",
        "expected_course": "Bachelor Of Technology In Computer Science And Engineering",
        "expected_intent": "fees",
    },
    {
        "query": "Aerospace engineering fees",
        "expected_course": "Bachelor Of Technology In Aerospace Engineering",
        "expected_intent": "fees",
    },
    {
        "query": "Fisheries science course details and eligibility",
        "expected_course": "Bachelor Of Fisheries Science",
        "expected_intent": "course_information",
    },
    {
        "query": "MBA fees at Centurion University",
        "expected_course": "Master Of Business Administration",
        "expected_intent": "fees",
    },
    {
        "query": "BSc Nursing fee and admission",
        "expected_course": "B Sc Nursing",
        "expected_intent": "fees",
    },
    {
        "query": "Diploma in Mechanical Engineering fees",
        "expected_course": "Diploma In Mechanical Engineering",
        "expected_intent": "fees",
    },
]


def evaluate_rag_retrieval(top_k: int = 5) -> Dict[str, float]:
    """Calculate Recall@K, MRR, and Retrieval Precision."""
    EVAL_DIR.mkdir(parents=True, exist_ok=True)

    recalls_at_1 = []
    recalls_at_3 = []
    recalls_at_5 = []
    reciprocal_ranks = []
    precisions = []

    for item in TEST_BENCHMARK:
        q = item["query"]
        expected_course = item["expected_course"].lower()

        results = retrieve_context(q, top_k=top_k)
        retrieved_courses = [r.get("course", "").lower() for r in results]

        # Check ranks
        rank = None
        for idx, c in enumerate(retrieved_courses):
            if c == expected_course or expected_course in c or c in expected_course:
                rank = idx + 1
                break

        # Recall@K
        recalls_at_1.append(1.0 if rank == 1 else 0.0)
        recalls_at_3.append(1.0 if rank and rank <= 3 else 0.0)
        recalls_at_5.append(1.0 if rank and rank <= 5 else 0.0)

        # MRR
        reciprocal_ranks.append(1.0 / rank if rank else 0.0)

        # Precision (at least one relevant chunk in top_k)
        precisions.append(1.0 if rank and rank <= top_k else 0.0)

    metrics = {
        "recall_at_1": round(float(np.mean(recalls_at_1)), 4),
        "recall_at_3": round(float(np.mean(recalls_at_3)), 4),
        "recall_at_5": round(float(np.mean(recalls_at_5)), 4),
        "mrr": round(float(np.mean(reciprocal_ranks)), 4),
        "retrieval_precision": round(float(np.mean(precisions)), 4),
        "eval_sample_count": len(TEST_BENCHMARK),
    }

    report_path = EVAL_DIR / "rag_metrics.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    return metrics


if __name__ == "__main__":
    m = evaluate_rag_retrieval()
    print("RAG Retrieval Metrics:", m)
