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
    calculate_overall_score,
    generate_gap_analysis,
    generate_recommendations,
    get_risk_level,
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


class TestOverallScore(unittest.TestCase):

    def test_empty_returns_zero(self):
        scores = calculate_category_scores([])
        self.assertEqual(calculate_overall_score(scores, []), 0.0)

    def test_score_range(self):
        reqs = _make_classified(["Functionality"] * 3 + ["Security"] * 2)
        scores = calculate_category_scores(reqs)
        overall = calculate_overall_score(scores, reqs)
        self.assertGreaterEqual(overall, 0.0)
        self.assertLessEqual(overall, 100.0)

    def test_more_categories_higher_score(self):
        """Covering more categories should yield a higher coverage component."""
        reqs_narrow = _make_classified(["Functionality"] * 7)
        reqs_wide = _make_classified(ALL_CATEGORIES)

        scores_narrow = calculate_category_scores(reqs_narrow)
        scores_wide = calculate_category_scores(reqs_wide)

        overall_narrow = calculate_overall_score(scores_narrow, reqs_narrow)
        overall_wide = calculate_overall_score(scores_wide, reqs_wide)
        self.assertGreater(overall_wide, overall_narrow)

    def test_capped_at_100(self):
        reqs = _make_classified(ALL_CATEGORIES * 10)
        for r in reqs:
            r["confidence"] = 100.0
        scores = calculate_category_scores(reqs)
        overall = calculate_overall_score(scores, reqs)
        self.assertLessEqual(overall, 100.0)


class TestRiskLevel(unittest.TestCase):

    def test_low_risk(self):
        self.assertEqual(get_risk_level(85)["level"], "Low")

    def test_medium_risk(self):
        self.assertEqual(get_risk_level(65)["level"], "Medium")

    def test_high_risk(self):
        self.assertEqual(get_risk_level(45)["level"], "High")

    def test_critical_risk(self):
        self.assertEqual(get_risk_level(20)["level"], "Critical")

    def test_boundary_80(self):
        self.assertEqual(get_risk_level(80)["level"], "Low")

    def test_colour_present(self):
        result = get_risk_level(50)
        self.assertIn("colour", result)


class TestRecommendations(unittest.TestCase):

    def test_empty_has_recommendations(self):
        scores = calculate_category_scores([])
        recs = generate_recommendations(scores, 0.0)
        self.assertGreater(len(recs), 0)

    def test_critical_general_recommendation(self):
        scores = calculate_category_scores([])
        recs = generate_recommendations(scores, 30.0)
        priorities = [r["priority"] for r in recs]
        self.assertIn("critical", priorities)

    def test_full_coverage_no_high_recommendations(self):
        reqs = _make_classified(
            ["Functionality"] * 5 + ["Security"] * 3 + ["Reliability"] * 3
            + ["Efficiency"] * 2 + ["Usability"] * 2
            + ["Maintainability"] * 1 + ["Portability"] * 1
        )
        scores = calculate_category_scores(reqs)
        recs = generate_recommendations(scores, 85.0)
        high_recs = [r for r in recs if r["priority"] == "high"]
        self.assertEqual(len(high_recs), 0)

    def test_sorted_by_priority(self):
        scores = calculate_category_scores([])
        recs = generate_recommendations(scores, 20.0)
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
        self.assertEqual(report["overall_score"], 0.0)
        self.assertIsInstance(report["recommendations"], list)

    def test_report_keys(self):
        reqs = _make_classified(["Functionality", "Security"])
        report = build_full_report(reqs)
        expected_keys = {
            "total_requirements", "category_scores", "overall_score",
            "risk", "recommendations", "gap_analysis",
            "categories_present", "categories_missing",
        }
        self.assertTrue(expected_keys.issubset(report.keys()))

    def test_categories_present_and_missing(self):
        reqs = _make_classified(["Functionality", "Security"])
        report = build_full_report(reqs)
        self.assertIn("Functionality", report["categories_present"])
        self.assertIn("Security", report["categories_present"])
        self.assertIn("Portability", report["categories_missing"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
