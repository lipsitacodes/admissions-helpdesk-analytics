import sys
from pathlib import Path

import joblib

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from preprocessing.clean_text import clean_text

VECTORIZER_PATH = ROOT_DIR / "models" / "tfidf_vectorizer.joblib"
MODEL_PATH = ROOT_DIR / "models" / "intent_classifier.joblib"


def predict_intent(text: str):
    """Predict the intent of a single student query and return confidence."""
    cleaned_text = clean_text(text)

    vectorizer = joblib.load(VECTORIZER_PATH)
    model = joblib.load(MODEL_PATH)

    text_vector = vectorizer.transform([cleaned_text])
    predicted_intent = model.predict(text_vector)[0]
    probabilities = model.predict_proba(text_vector)[0]
    confidence = float(max(probabilities))

    return predicted_intent, confidence


def main():
    test_queries = [
        "How much do I have to pay for tuition?",
        "How can I get a hostel room?",
        "What documents do I need to submit?",
        "Can I get financial aid?",
    ]

    for query in test_queries:
        intent, confidence = predict_intent(query)
        print("Question:", query)
        print("Predicted intent:", intent)
        print("Confidence:", round(confidence, 4))
        print()


if __name__ == "__main__":
    main()
