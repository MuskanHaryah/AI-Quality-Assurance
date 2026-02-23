"""
services/classifier.py
======================
Wrapper around the trained Logistic Regression model.

Responsibilities
----------------
- Load the TF-IDF vectorizer and classifier once at import time.
- Expose classify() and classify_batch() for single / bulk predictions.
- Return structured dicts with category, confidence, and per-class probabilities.
"""

import json
import os
import pickle
from typing import Any, Dict, List

from utils.logger import app_logger

# --------------------------------------------------------------------------- #
# ISO/IEC 9126 quality categories (must match training labels)                 #
# --------------------------------------------------------------------------- #
CATEGORIES = [
    "Functionality",
    "Security",
    "Reliability",
    "Usability",
    "Efficiency",
    "Maintainability",
    "Portability",
]


class RequirementClassifier:
    """
    Load and wrap the trained ML model for requirement classification.

    Args:
        model_path:      Path to classifier_model.pkl
        vectorizer_path: Path to tfidf_vectorizer.pkl
        model_info_path: Path to model_info.json  (optional, for metadata)
    """

    def __init__(self, model_path: str, vectorizer_path: str, model_info_path: str = None):
        app_logger.info("Loading ML model …")

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        if not os.path.exists(vectorizer_path):
            raise FileNotFoundError(f"Vectorizer file not found: {vectorizer_path}")

        with open(model_path, "rb") as f:
            self.model = pickle.load(f)

        with open(vectorizer_path, "rb") as f:
            self.vectorizer = pickle.load(f)

        # Load optional metadata
        self.model_info: Dict[str, Any] = {}
        if model_info_path and os.path.exists(model_info_path):
            with open(model_info_path, "r") as f:
                self.model_info = json.load(f)

        self.classes: List[str] = list(self.model.classes_)
        app_logger.info(
            f"Model loaded successfully | "
            f"accuracy={self.model_info.get('accuracy', 'N/A'):.4f} | "
            f"classes={self.classes}"
        )

    # ----------------------------------------------------------------------- #
    # Public API                                                                #
    # ----------------------------------------------------------------------- #

    def classify(self, text: str) -> Dict[str, Any]:
        """
        Classify a single requirement text.

        Args:
            text: Plain-text requirement string.

        Returns:
            {
                "text":         original input,
                "category":     predicted ISO 9126 category,
                "confidence":   confidence percentage (0–100),
                "probabilities": {category: probability, …}
            }
        """
        if not text or not text.strip():
            return {
                "text": text,
                "category": "Unknown",
                "confidence": 0.0,
                "probabilities": {},
            }

        X = self.vectorizer.transform([text.strip()])
        prediction = self.model.predict(X)[0]
        proba = self.model.predict_proba(X)[0]
        confidence = round(float(max(proba)) * 100, 2)
        probabilities = {cls: round(float(p) * 100, 2) for cls, p in zip(self.classes, proba)}

        return {
            "text": text,
            "category": prediction,
            "confidence": confidence,
            "probabilities": probabilities,
        }

    def classify_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        Classify a list of requirement strings efficiently using batch
        vectorization and prediction (single call to transform / predict).

        Args:
            texts: List of plain-text requirements.

        Returns:
            List of classify() result dicts, one per input.
        """
        if not texts:
            return []

        # Separate empty/whitespace texts from valid ones
        valid_indices: List[int] = []
        valid_texts: List[str] = []
        results: List[Dict[str, Any]] = [None] * len(texts)  # type: ignore[list-item]

        for idx, text in enumerate(texts):
            if not text or not text.strip():
                results[idx] = {
                    "text": text, "category": "Unknown",
                    "confidence": 0.0, "probabilities": {}, "index": idx,
                }
            else:
                valid_indices.append(idx)
                valid_texts.append(text.strip())

        # Batch vectorize + predict in ONE call each (major speedup)
        if valid_texts:
            X = self.vectorizer.transform(valid_texts)
            predictions = self.model.predict(X)
            probas = self.model.predict_proba(X)

            for i, orig_idx in enumerate(valid_indices):
                confidence = round(float(max(probas[i])) * 100, 2)
                probabilities = {
                    cls: round(float(p) * 100, 2)
                    for cls, p in zip(self.classes, probas[i])
                }
                results[orig_idx] = {
                    "text": texts[orig_idx],
                    "category": predictions[i],
                    "confidence": confidence,
                    "probabilities": probabilities,
                    "index": orig_idx,
                }

        app_logger.info(f"Classified {len(texts)} requirements (batch)")
        return results

    def get_model_info(self) -> Dict[str, Any]:
        """Return model metadata (accuracy, F1, trained_at, …)."""
        return {
            "model_name": self.model_info.get("model_name", "Logistic Regression"),
            "accuracy": self.model_info.get("accuracy", None),
            "f1_score": self.model_info.get("f1_score", None),
            "trained_at": self.model_info.get("trained_at", None),
            "num_features": self.model_info.get("num_features", None),
            "categories": self.classes,
        }


# --------------------------------------------------------------------------- #
# Singleton — loaded once when the module is first imported                    #
# --------------------------------------------------------------------------- #

def _load_classifier() -> RequirementClassifier:
    """Resolve model paths relative to this file's location (backend/)."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return RequirementClassifier(
        model_path=os.path.join(base_dir, "models", "classifier_model.pkl"),
        vectorizer_path=os.path.join(base_dir, "models", "tfidf_vectorizer.pkl"),
        model_info_path=os.path.join(base_dir, "models", "model_info.json"),
    )


classifier = _load_classifier()
