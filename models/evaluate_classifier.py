from __future__ import annotations

import sys
from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from preprocessing.clean_text import clean_text

EVAL_FILE = ROOT_DIR / "data" / "evaluation_queries_bilingual_draft.csv"
MODEL_FILE = ROOT_DIR / "models" / "intent_classifier_bilingual.joblib"
VECTORIZER_FILE = ROOT_DIR / "models" / "tfidf_vectorizer_bilingual.joblib"


def main() -> int:
    evaluation = pd.read_csv(EVAL_FILE)
    required = {"query", "intent", "language"}
    missing = sorted(required - set(evaluation.columns))
    if missing:
        raise ValueError(f"Evaluation dataset is missing required columns: {missing}")

    model = joblib.load(MODEL_FILE)
    vectorizer = joblib.load(VECTORIZER_FILE)
    cleaned = evaluation["query"].astype(str).map(clean_text)
    predictions = model.predict(vectorizer.transform(cleaned))
    labels = sorted(set(evaluation["intent"]) | set(predictions))

    print(f"Evaluation samples: {len(evaluation)}")
    print(f"Accuracy: {accuracy_score(evaluation['intent'], predictions):.4f}")
    print(classification_report(evaluation["intent"], predictions, zero_division=0))
    print("Confusion matrix labels:", labels)
    print(confusion_matrix(evaluation["intent"], predictions, labels=labels))
    for language, group in evaluation.assign(prediction=predictions).groupby("language"):
        print(f"{language} accuracy: {accuracy_score(group['intent'], group['prediction']):.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
