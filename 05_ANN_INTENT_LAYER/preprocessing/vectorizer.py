"""Phase 5: ANN Preprocessing & Vectorization.

Uses TF-IDF feature extraction suited for neural multi-label classification.
"""

from typing import List, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib


def create_vectorizer(max_features: int = 2000) -> TfidfVectorizer:
    """Create sublinear TF-IDF vectorizer for input query tokens."""
    return TfidfVectorizer(
        max_features=max_features,
        ngram_range=(1, 2),
        sublinear_tf=True,
        strip_accents="unicode",
        token_pattern=r"(?u)\b\w+\b",
    )


def save_vectorizer(vectorizer: TfidfVectorizer, path: str):
    """Save vectorizer artifacts."""
    joblib.dump(vectorizer, path)


def load_vectorizer(path: str) -> TfidfVectorizer:
    """Load vectorizer artifacts."""
    return joblib.load(path)
