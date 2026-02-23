"""
tests/test_classifier.py
========================
Unit tests for services/classifier.py

Run from backend/ directory:
    python -m pytest tests/test_classifier.py -v
    OR
    python tests/test_classifier.py
"""

import os
import sys
import unittest

# Ensure backend/ is on the path when running directly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.classifier import classifier


class TestRequirementClassifier(unittest.TestCase):

    # ── Model loading ─────────────────────────────────────────────────── #

    def test_model_loaded(self):
        """Classifier and vectorizer must be loaded at import time."""
        self.assertIsNotNone(classifier.model)
        self.assertIsNotNone(classifier.vectorizer)

    def test_classes_populated(self):
        """Model must expose all 7 ISO 9126 categories."""
        expected = {"Functionality", "Security", "Reliability",
                    "Efficiency", "Usability", "Maintainability", "Portability"}
        self.assertEqual(set(classifier.classes), expected)

    def test_model_info_has_accuracy(self):
        info = classifier.get_model_info()
        self.assertIn("accuracy", info)
        self.assertGreater(info["accuracy"], 0.7)   # Must be above 70 %

    # ── Single classification ─────────────────────────────────────────── #

    def test_classify_returns_required_keys(self):
        result = classifier.classify("The system shall encrypt all passwords using AES-256.")
        self.assertIn("text",          result)
        self.assertIn("category",      result)
        self.assertIn("confidence",    result)
        self.assertIn("probabilities", result)

    def test_classify_category_is_known(self):
        result = classifier.classify("The system shall encrypt all passwords using AES-256.")
        self.assertIn(result["category"], classifier.classes)

    def test_classify_confidence_range(self):
        result = classifier.classify("The system must respond within 2 seconds under load.")
        self.assertGreaterEqual(result["confidence"], 0.0)
        self.assertLessEqual(result["confidence"], 100.0)

    def test_classify_probabilities_sum_to_100(self):
        result = classifier.classify("Users shall be able to reset their password via email.")
        total = sum(result["probabilities"].values())
        self.assertAlmostEqual(total, 100.0, places=1)

    def test_classify_empty_text(self):
        """Empty text should return category=Unknown and confidence=0."""
        result = classifier.classify("")
        self.assertEqual(result["category"],   "Unknown")
        self.assertEqual(result["confidence"], 0.0)

    def test_classify_whitespace_only(self):
        result = classifier.classify("   ")
        self.assertEqual(result["category"],   "Unknown")

    # ── Batch classification ─────────────────────────────────────────── #

    def test_classify_batch_returns_list(self):
        texts = [
            "The system shall encrypt passwords.",
            "The system must respond in under 2 seconds.",
            "Users should be able to upload files up to 100 MB.",
        ]
        results = classifier.classify_batch(texts)
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 3)

    def test_classify_batch_each_has_index(self):
        texts = ["The system shall authenticate users.", "The app must load in 3 seconds."]
        results = classifier.classify_batch(texts)
        for i, r in enumerate(results):
            self.assertEqual(r["index"], i)

    def test_classify_batch_all_categories_valid(self):
        texts = [
            "The system shall handle 1000 concurrent sessions without degradation.",
            "All data shall be backed up every 24 hours.",
            "The interface shall be accessible on mobile devices.",
        ]
        results = classifier.classify_batch(texts)
        for r in results:
            self.assertIn(r["category"], classifier.classes)

    # ── Known category spot-checks ────────────────────────────────────── #

    def test_security_requirement(self):
        result = classifier.classify(
            "The system shall use TLS 1.3 for all data in transit."
        )
        # Confidence-weighted: if confidence > 60 it must be Security
        if result["confidence"] > 60:
            self.assertEqual(result["category"], "Security")

    def test_efficiency_requirement(self):
        result = classifier.classify(
            "The system must process requests within 500 milliseconds under normal load."
        )
        if result["confidence"] > 60:
            self.assertEqual(result["category"], "Efficiency")


if __name__ == "__main__":
    unittest.main(verbosity=2)
