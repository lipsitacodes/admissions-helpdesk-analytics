"""Phase 13: Master Comprehensive Evaluation Suite.

Executes evaluations across all layers:
1. ANN Intent Classification (Accuracy, Precision, Recall, F1)
2. RAG Retrieval (Recall@K, MRR, Precision)
3. Grounded Answer Generation (Correctness, Groundedness)
4. Escalation Trigger Appropriateness
Saves unified master report to 12_EVALUATION/master_evaluation_report.json.
"""

from pathlib import Path
import json
import logging
from datetime import datetime

from .intent.eval_intent import run_intent_eval
from .retrieval.eval_retrieval import run_retrieval_eval
from .answer.eval_answer import run_answer_eval
from .escalation.eval_escalation import run_escalation_eval

logger = logging.getLogger("Phase13_MasterEvaluator")
logging.basicConfig(level=logging.INFO)

BASE_DIR = Path(__file__).resolve().parent


def run_all_evaluations() -> dict:
    """Run all system evaluations and compile master report."""
    logger.info("Executing Phase 13 Comprehensive System Evaluation...")

    intent_metrics = run_intent_eval()
    retrieval_metrics = run_retrieval_eval()
    answer_metrics = run_answer_eval()
    escalation_metrics = run_escalation_eval()

    master_report = {
        "timestamp": datetime.now().isoformat(),
        "project": "CUTM Multilingual Admissions & Student Query Helpdesk",
        "institutional_source": "CUTM_Category_CSVs/*.csv",
        "evaluation_summary": {
            "ann_intent": intent_metrics,
            "rag_retrieval": retrieval_metrics,
            "answer_generation": answer_metrics,
            "escalation": escalation_metrics,
        },
    }

    report_path = BASE_DIR / "master_evaluation_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(master_report, f, indent=2)

    logger.info("Master evaluation report written successfully to %s", report_path)
    return master_report


if __name__ == "__main__":
    report = run_all_evaluations()
    print(json.dumps(report, indent=2))
