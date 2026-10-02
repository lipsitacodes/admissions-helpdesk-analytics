"""Phase 13: RAG Retrieval Evaluation Runner."""

import importlib
from typing import Dict, Any


def run_retrieval_eval() -> Dict[str, Any]:
    ev = importlib.import_module("07_RAG_LAYER.evaluation.evaluator")
    return ev.evaluate_rag_retrieval()


if __name__ == "__main__":
    print(run_retrieval_eval())
