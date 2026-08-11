import sys
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from preprocessing.clean_text import clean_text

TRAIN_FILE = ROOT_DIR / "data" / "training_queries.csv"
EVAL_FILE = ROOT_DIR / "data" / "evaluation_queries.csv"
MODEL_FILE = ROOT_DIR / "models" / "intent_classifier.joblib"
VECTORIZER_FILE = ROOT_DIR / "models" / "tfidf_vectorizer.joblib"


def load_data(path: Path):
    df = pd.read_csv(path)
    queries = df["query"].astype(str).tolist()
    labels = df["intent"].astype(str).tolist()
    return queries, labels


def clean_queries(queries):
    return [clean_text(query) for query in queries]


def prepare_tfidf(queries):
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(queries)
    return X, vectorizer


def train_model(X, y):
    model = LogisticRegression(max_iter=1000)
    model.fit(X, y)
    return model


def save_artifacts(model, vectorizer):
    joblib.dump(model, MODEL_FILE)
    joblib.dump(vectorizer, VECTORIZER_FILE)


def main():
    train_queries, train_labels = load_data(TRAIN_FILE)
    eval_queries, eval_labels = load_data(EVAL_FILE)

    cleaned_train = clean_queries(train_queries)
    cleaned_eval = clean_queries(eval_queries)

    X_train, vectorizer = prepare_tfidf(cleaned_train)
    X_eval = vectorizer.transform(cleaned_eval)

    model = train_model(X_train, train_labels)

    predictions = model.predict(X_eval)
    accuracy = accuracy_score(eval_labels, predictions)
    report = classification_report(eval_labels, predictions)

    print("Training samples:", len(train_queries))
    print("Intent classes:", len(set(train_labels)))
    print("TF-IDF feature count:", X_train.shape[1])
    print("Model training completed.")
    print("Evaluation accuracy:", round(accuracy, 4))
    print("Classification report:")
    print(report)
    print("TF-IDF matrix shape:", X_train.shape)

    print("Sample predictions:")
    for query, actual, predicted in zip(eval_queries[:5], eval_labels[:5], predictions[:5]):
        print("Question:", query)
        print("Actual intent:", actual)
        print("Predicted intent:", predicted)
        print()

    save_artifacts(model, vectorizer)
    print("Saved model to:", MODEL_FILE)
    print("Saved vectorizer to:", VECTORIZER_FILE)


if __name__ == "__main__":
    main()
