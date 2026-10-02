"""Phase 13: Intent Classifier Evaluation Runner."""

import importlib
from typing import Dict, Any


def run_intent_eval() -> Dict[str, Any]:
    ev = importlib.import_module("05_ANN_INTENT_LAYER.evaluation.evaluator")
    return ev.evaluate_ann_model()


if __name__ == "__main__":
    print(run_intent_eval())
