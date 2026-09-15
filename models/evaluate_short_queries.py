from __future__ import annotations

import sys
from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from preprocessing.clean_text import clean_text

STRESS_FILE = ROOT_DIR / "data" / "evaluation_short_queries.csv"
MODEL_FILE = ROOT_DIR / "models" / "intent_classifier_bilingual.joblib"
VECTORIZER_FILE = ROOT_DIR / "models" / "tfidf_vectorizer_bilingual.joblib"


def main() -> int:
    stress = pd.read_csv(STRESS_FILE)
    model = joblib.load(MODEL_FILE)
    vectorizer = joblib.load(VECTORIZER_FILE)
    cleaned = stress["query"].astype(str).map(clean_text)
    vectors = vectorizer.transform(cleaned)
    predictions = model.predict(vectors)
    probabilities = model.predict_proba(vectors).max(axis=1)

    print(f"Stress-test samples: {len(stress)}")
    print(f"Accuracy: {accuracy_score(stress['intent'], predictions):.4f}")
    print(classification_report(stress["intent"], predictions, zero_division=0))
    for query, expected, predicted, confidence in zip(
        stress["query"], stress["intent"], predictions, probabilities
    ):
        print(
            f"{query} => {predicted} confidence={confidence:.4f} "
            f"expected={expected} correct={predicted == expected}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
