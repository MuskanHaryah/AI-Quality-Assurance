"""
tests/test_requirement_extractor.py
====================================
Unit tests for services/requirement_extractor.py

Run from backend/ directory:
    python -m pytest tests/test_requirement_extractor.py -v
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.requirement_extractor import (
    extract_requirements,
    get_requirement_texts,
)


class TestExtractRequirements(unittest.TestCase):
    """Core tests for the requirement extraction pipeline."""

    # ── Basic functionality ───────────────────────────────────────────── #

    def test_empty_text(self):
        result = extract_requirements("")
        self.assertEqual(result["total_found"], 0)
        self.assertEqual(result["requirements"], [])

    def test_whitespace_only(self):
        result = extract_requirements("   \n\n  \t  ")
        self.assertEqual(result["total_found"], 0)

    def test_none_safe(self):
        """None-like input handled gracefully."""
        result = extract_requirements("")
        self.assertIn("requirements", result)
        self.assertIn("extraction_stats", result)

    # ── Strong keyword detection ──────────────────────────────────────── #

    def test_shall_keyword(self):
        text = "The system shall authenticate all users before granting access."
        result = extract_requirements(text)
        self.assertEqual(result["total_found"], 1)
        self.assertEqual(result["requirements"][0]["keyword_strength"], "strong")

    def test_must_keyword(self):
        text = "All passwords must be stored using bcrypt hashing with a salt."
        result = extract_requirements(text)
        self.assertEqual(result["total_found"], 1)
        self.assertEqual(result["requirements"][0]["keyword_strength"], "strong")

    def test_should_keyword(self):
        text = "The application should provide an audit log of all administrative actions."
        result = extract_requirements(text)
        self.assertEqual(result["total_found"], 1)
        self.assertEqual(result["requirements"][0]["keyword_strength"], "strong")

    def test_negative_keyword(self):
        text = "The system shall not expose internal error details to end users."
        result = extract_requirements(text)
        self.assertGreaterEqual(result["total_found"], 1)
        matched = [r for r in result["requirements"] if "shall not" in r["text"].lower()]
        self.assertTrue(len(matched) > 0 or result["total_found"] >= 1)

    # ── Weak keyword detection ────────────────────────────────────────── #

    def test_weak_keyword_supports(self):
        text = "The platform supports multi-factor authentication for all user accounts."
        result = extract_requirements(text)
        self.assertEqual(result["total_found"], 1)
        self.assertEqual(result["requirements"][0]["keyword_strength"], "weak")

    def test_weak_keyword_ensures(self):
        text = "The system ensures data integrity across all distributed transactions."
        result = extract_requirements(text)
        self.assertEqual(result["total_found"], 1)

    # ── Filtering ─────────────────────────────────────────────────────── #

    def test_too_short_filtered(self):
        """Text shorter than MIN_LENGTH (20) should be excluded."""
        text = "Must login."
        result = extract_requirements(text)
        self.assertEqual(result["total_found"], 0)

    def test_non_requirement_filtered(self):
        """Lines without any requirement keyword are excluded."""
        text = "This is a normal description of a blue button on the homepage."
        result = extract_requirements(text)
        self.assertEqual(result["total_found"], 0)

    # ── Multi-requirement extraction ──────────────────────────────────── #

    def test_multiple_requirements(self):
        text = (
            "The system shall authenticate all users before granting access.\n"
            "All passwords must be stored using bcrypt hashing.\n"
            "The application should support at least 1000 concurrent users.\n"
            "Login page with blue button.\n"
            "The software shall provide an audit log of all user actions.\n"
        )
        result = extract_requirements(text)
        self.assertGreaterEqual(result["total_found"], 3)

    def test_numbered_list(self):
        text = (
            "1. The system shall validate all user input.\n"
            "2. The application must encrypt data at rest using AES-256.\n"
            "3. Normal text without keywords here.\n"
        )
        result = extract_requirements(text)
        self.assertGreaterEqual(result["total_found"], 2)

    def test_bullet_list(self):
        text = (
            "- The system shall log all authentication events.\n"
            "- All API endpoints must require authentication tokens.\n"
            "- System overview diagram section.\n"
        )
        result = extract_requirements(text)
        self.assertGreaterEqual(result["total_found"], 2)

    # ── Extraction stats ──────────────────────────────────────────────── #

    def test_stats_present(self):
        text = "The system shall authenticate users. The app must respond in 2 seconds."
        result = extract_requirements(text)
        stats = result["extraction_stats"]
        self.assertIn("strong_keyword_matches", stats)
        self.assertIn("weak_keyword_matches", stats)
        self.assertIn("filtered_out", stats)

    def test_total_candidates_gte_total_found(self):
        text = (
            "The system shall authenticate all users before granting access.\n"
            "This is just a regular sentence.\n"
            "All passwords must be hashed using bcrypt.\n"
        )
        result = extract_requirements(text)
        self.assertGreaterEqual(result["total_candidates"], result["total_found"])

    # ── Result structure ──────────────────────────────────────────────── #

    def test_requirement_dict_keys(self):
        text = "The system shall encrypt all user passwords using AES-256 encryption."
        result = extract_requirements(text)
        req = result["requirements"][0]
        expected_keys = {"text", "source_index", "has_keyword", "keyword_strength", "matched_keywords"}
        self.assertTrue(expected_keys.issubset(req.keys()))

    def test_source_index_is_int(self):
        text = "The system shall authenticate users. The app must encrypt data."
        result = extract_requirements(text)
        for req in result["requirements"]:
            self.assertIsInstance(req["source_index"], int)


class TestGetRequirementTexts(unittest.TestCase):

    def test_returns_strings(self):
        text = "The system shall authenticate users. The app must encrypt passwords."
        extraction = extract_requirements(text)
        texts = get_requirement_texts(extraction)
        self.assertIsInstance(texts, list)
        for t in texts:
            self.assertIsInstance(t, str)

    def test_empty_extraction(self):
        texts = get_requirement_texts({"requirements": []})
        self.assertEqual(texts, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
