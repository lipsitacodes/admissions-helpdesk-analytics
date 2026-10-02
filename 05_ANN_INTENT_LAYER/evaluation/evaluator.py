"""Phase 5: ANN Intent Classifier Evaluation.

Calculates multi-label classification metrics:
- Subset Accuracy
- Micro & Macro Precision
- Micro & Macro Recall
- Micro & Macro F1-score
"""

from __future__ import annotations

import json
from pathlib import Path
import numpy as np
import torch
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
from ..dataset.dataset_builder import TARGET_INTENTS
from ..preprocessing.vectorizer import load_vectorizer
from ..model.ann_model import MultiLabelANN

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = BASE_DIR / "model"
EVAL_DIR = BASE_DIR / "evaluation"


def evaluate_ann_model(threshold: float = 0.5) -> dict:
    """Evaluate trained ANN model on validation / test samples."""
    EVAL_DIR.mkdir(parents=True, exist_ok=True)

    dataset_file = BASE_DIR / "dataset" / "ann_intent_dataset.json"
    with open(dataset_file, "r", encoding="utf-8") as f:
        samples = json.load(f)

    # Use second half as test slice
    test_samples = samples[int(len(samples) * 0.85):]
    texts = [s["text"] for s in test_samples]
    y_true = np.array([s["labels"] for s in test_samples], dtype=np.float32)

    vectorizer = load_vectorizer(str(MODEL_DIR / "vectorizer.joblib"))
    X_test_vec = vectorizer.transform(texts).toarray()

    with open(MODEL_DIR / "classes.json", "r") as f:
        meta = json.load(f)

    model = MultiLabelANN(input_dim=meta["input_dim"], hidden_dim=128, output_dim=meta["output_dim"])
    model.load_state_dict(torch.load(MODEL_DIR / "ann_intent_weights.pt", map_location="cpu"))
    model.eval()

    with torch.no_grad():
        x_tensor = torch.tensor(X_test_vec, dtype=torch.float32)
        probs = model.predict_proba(x_tensor).numpy()

    y_pred = (probs >= threshold).astype(np.float32)

    # Multi-label metrics
    subset_acc = float(accuracy_score(y_true, y_pred))
    prec_micro = float(precision_score(y_true, y_pred, average="micro", zero_division=0))
    prec_macro = float(precision_score(y_true, y_pred, average="macro", zero_division=0))
    rec_micro = float(recall_score(y_true, y_pred, average="micro", zero_division=0))
    rec_macro = float(recall_score(y_true, y_pred, average="macro", zero_division=0))
    f1_micro = float(f1_score(y_true, y_pred, average="micro", zero_division=0))
    f1_macro = float(f1_score(y_true, y_pred, average="macro", zero_division=0))

    metrics = {
        "subset_accuracy": round(subset_acc, 4),
        "precision_micro": round(prec_micro, 4),
        "precision_macro": round(prec_macro, 4),
        "recall_micro": round(rec_micro, 4),
        "recall_macro": round(rec_macro, 4),
        "f1_micro": round(f1_micro, 4),
        "f1_macro": round(f1_macro, 4),
        "target_intents": TARGET_INTENTS,
    }

    report_path = EVAL_DIR / "ann_metrics.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    return metrics


if __name__ == "__main__":
    m = evaluate_ann_model()
    print("ANN Evaluation Metrics:", m)
