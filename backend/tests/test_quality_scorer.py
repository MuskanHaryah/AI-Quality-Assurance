"""
tests/test_quality_scorer.py
==============================
Unit tests for services/quality_scorer.py

Run from backend/ directory:
    python -m pytest tests/test_quality_scorer.py -v
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.quality_scorer import (
    ALL_CATEGORIES,
    CATEGORY_WEIGHTS,
    build_full_report,
    calculate_category_scores,
    detect_domain,
    generate_gap_analysis,
    generate_recommendations,
)


def _make_classified(categories: list[str]) -> list[dict]:
    """Helper to build a classified-requirements list for a given category distribution."""
    return [
        {"text": f"Req {i}", "category": cat, "confidence": 80.0}
        for i, cat in enumerate(categories)
    ]


class TestCategoryScores(unittest.TestCase):

    def test_empty_input(self):
        scores = calculate_category_scores([])
        for cat in ALL_CATEGORIES:
            self.assertEqual(scores[cat]["count"], 0)
            self.assertFalse(scores[cat]["meets_minimum"])

    def test_single_category(self):
        reqs = _make_classified(["Security"] * 5)
        scores = calculate_category_scores(reqs)
        self.assertEqual(scores["Security"]["count"], 5)
        self.assertEqual(scores["Security"]["percentage"], 100.0)
        self.assertEqual(scores["Functionality"]["count"], 0)

    def test_all_categories_present(self):
        reqs = _make_classified(ALL_CATEGORIES)
        scores = calculate_category_scores(reqs)
        for cat in ALL_CATEGORIES:
            self.assertEqual(scores[cat]["count"], 1)

    def test_weight_values_sum_to_1(self):
        total = sum(CATEGORY_WEIGHTS.values())
        self.assertAlmostEqual(total, 1.0, places=5)

    def test_meets_minimum_flag(self):
        reqs = _make_classified(["Functionality"] * 5 + ["Security"] * 1)
        scores = calculate_category_scores(reqs)
        self.assertTrue(scores["Functionality"]["meets_minimum"])
        self.assertFalse(scores["Security"]["meets_minimum"])  # needs 3


class TestDomainDetection(unittest.TestCase):

    def test_banking_domain(self):
        reqs = [
            {"text": "The system shall process bank transactions securely.", "category": "Security", "confidence": 90},
            {"text": "Credit must be updated after each payment.", "category": "Functionality", "confidence": 85},
        ]
        result = detect_domain(reqs)
        self.assertEqual(result["domain"], "Banking / Finance")
        self.assertGreater(result["confidence"], 0)
        self.assertIn("Security", result["critical_categories"])

    def test_healthcare_domain(self):
        reqs = [
            {"text": "The system shall store patient medical records.", "category": "Functionality", "confidence": 90},
            {"text": "Clinical diagnosis data must be encrypted.", "category": "Security", "confidence": 85},
        ]
        result = detect_domain(reqs)
        self.assertEqual(result["domain"], "Healthcare")

    def test_library_management_domain(self):
        reqs = [
            {"text": "The system shall allow members to borrow books.", "category": "Functionality", "confidence": 90},
            {"text": "Patron can search catalog by ISBN or title.", "category": "Usability", "confidence": 85},
            {"text": "Overdue items shall generate fine notifications.", "category": "Functionality", "confidence": 88},
        ]
        result = detect_domain(reqs)
        self.assertEqual(result["domain"], "Library Management")
        self.assertIn("Usability", result["critical_categories"])

    def test_general_domain_when_no_keywords(self):
        reqs = [
            {"text": "The system shall do something.", "category": "Functionality", "confidence": 80},
        ]
        result = detect_domain(reqs)
        self.assertEqual(result["domain"], "General")
        self.assertEqual(result["confidence"], 0.0)

    def test_domain_from_raw_text(self):
        reqs = [{"text": "Requirement one", "category": "Functionality", "confidence": 80}]
        raw = "This banking application handles credit card transactions and loan management."
        result = detect_domain(reqs, raw_text=raw)
        self.assertEqual(result["domain"], "Banking / Finance")

    def test_critical_categories_present(self):
        reqs = [
            {"text": "Process financial transaction.", "category": "Functionality", "confidence": 80},
            {"text": "Secure bank transfer access.", "category": "Security", "confidence": 80},
        ]
        result = detect_domain(reqs)
        self.assertIn("Security", result["critical_categories"])
        self.assertIn("Reliability", result["critical_categories"])


class TestRecommendations(unittest.TestCase):

    def test_empty_has_recommendations(self):
        scores = calculate_category_scores([])
        recs = generate_recommendations(scores)
        self.assertGreater(len(recs), 0)

    def test_domain_aware_recommendation(self):
        """Banking domain with missing Security should get a critical recommendation."""
        scores = calculate_category_scores(_make_classified(["Functionality"] * 5))
        domain_info = {
            "domain": "Banking / Finance",
            "confidence": 0.8,
            "critical_categories": {"Security": "critical", "Reliability": "critical"},
        }
        recs = generate_recommendations(scores, domain_info)
        sec_recs = [r for r in recs if r["category"] == "Security"]
        self.assertEqual(len(sec_recs), 1)
        self.assertEqual(sec_recs[0]["priority"], "critical")
        self.assertIn("Banking / Finance", sec_recs[0]["message"])

    def test_full_coverage_no_high_recommendations(self):
        reqs = _make_classified(
            ["Functionality"] * 5 + ["Security"] * 3 + ["Reliability"] * 3
            + ["Efficiency"] * 2 + ["Usability"] * 2
            + ["Maintainability"] * 1 + ["Portability"] * 1
        )
        scores = calculate_category_scores(reqs)
        recs = generate_recommendations(scores)
        high_recs = [r for r in recs if r["priority"] == "high"]
        self.assertEqual(len(high_recs), 0)

    def test_sorted_by_priority(self):
        scores = calculate_category_scores([])
        domain_info = {
            "domain": "Banking / Finance",
            "confidence": 0.8,
            "critical_categories": {"Security": "critical"},
        }
        recs = generate_recommendations(scores, domain_info)
        order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        priorities = [order.get(r["priority"], 99) for r in recs]
        self.assertEqual(priorities, sorted(priorities))


class TestGapAnalysis(unittest.TestCase):

    def test_all_missing(self):
        scores = calculate_category_scores([])
        gaps = generate_gap_analysis(scores)
        self.assertEqual(len(gaps), len(ALL_CATEGORIES))
        for g in gaps:
            self.assertEqual(g["gap_type"], "missing")

    def test_no_gaps_when_all_met(self):
        reqs = _make_classified(
            ["Functionality"] * 5 + ["Security"] * 3 + ["Reliability"] * 3
            + ["Efficiency"] * 2 + ["Usability"] * 2
            + ["Maintainability"] * 1 + ["Portability"] * 1
        )
        scores = calculate_category_scores(reqs)
        gaps = generate_gap_analysis(scores)
        self.assertEqual(len(gaps), 0)

    def test_insufficient_gap(self):
        reqs = _make_classified(["Security"] * 1)  # needs 3
        scores = calculate_category_scores(reqs)
        gaps = generate_gap_analysis(scores)
        sec_gaps = [g for g in gaps if g["category"] == "Security"]
        self.assertEqual(len(sec_gaps), 1)
        self.assertEqual(sec_gaps[0]["gap_type"], "insufficient")
        self.assertEqual(sec_gaps[0]["shortage"], 2)


class TestBuildFullReport(unittest.TestCase):

    def test_empty_input(self):
        report = build_full_report([])
        self.assertEqual(report["total_requirements"], 0)
        self.assertIsInstance(report["recommendations"], list)
        self.assertIn("domain", report)

    def test_report_keys(self):
        reqs = _make_classified(["Functionality", "Security"])
        report = build_full_report(reqs)
        expected_keys = {
            "total_requirements", "category_scores", "domain",
            "recommendations", "gap_analysis",
            "categories_present", "categories_missing",
        }
        self.assertTrue(expected_keys.issubset(report.keys()))
        # overall_score and risk should NOT be in the new report
        self.assertNotIn("overall_score", report)
        self.assertNotIn("risk", report)

    def test_domain_in_report(self):
        reqs = _make_classified(["Functionality", "Security"])
        report = build_full_report(reqs)
        self.assertIn("domain", report["domain"])
        self.assertIn("confidence", report["domain"])

    def test_categories_present_and_missing(self):
        reqs = _make_classified(["Functionality", "Security"])
        report = build_full_report(reqs)
        self.assertIn("Functionality", report["categories_present"])
        self.assertIn("Security", report["categories_present"])
        self.assertIn("Portability", report["categories_missing"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
