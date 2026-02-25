"""
tests/test_quality_plan.py
===========================
Tests for the Quality Plan analyzer service and API routes.
"""

import io
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.quality_plan_analyzer import (
    analyze_quality_plan,
    _find_evidence,
    CATEGORY_EVIDENCE_KEYWORDS,
    ALL_CATEGORIES,
)


# ──────────────────────────────────────────────────────────────────────────── #
# Unit tests for the analyzer service                                          #
# ──────────────────────────────────────────────────────────────────────────── #

class TestQualityPlanAnalyzer(unittest.TestCase):
    """Test the core analyze_quality_plan() function."""

    def setUp(self):
        """Set up common SRS data to compare against."""
        self.srs_category_scores = {
            "Functionality":   {"count": 5, "percentage": 35},
            "Security":        {"count": 3, "percentage": 20},
            "Reliability":     {"count": 2, "percentage": 15},
            "Efficiency":      {"count": 2, "percentage": 15},
            "Usability":       {"count": 1, "percentage": 10},
            "Maintainability": {"count": 0, "percentage": 0},
            "Portability":     {"count": 0, "percentage": 0},
        }
        self.srs_present = ["Functionality", "Security", "Reliability", "Efficiency", "Usability"]
        self.srs_missing = ["Maintainability", "Portability"]

    def test_full_coverage_plan(self):
        """A plan covering all categories should get high scores."""
        plan_text = """
        Quality Plan v1.0

        1. Functional Testing
        We will conduct unit tests, integration tests, and acceptance tests
        for all functional requirements.

        2. Security Testing
        Penetration testing and vulnerability scanning will be performed.
        Authentication and authorization will be verified.

        3. Reliability Testing
        Stress testing and failover testing will ensure system reliability.
        Disaster recovery procedures will be tested.

        4. Performance Testing
        Load testing and response time benchmarks will be established.
        Throughput and latency will be measured under load.

        5. Usability Testing
        User acceptance testing and accessibility reviews will be performed.
        User experience surveys will be collected.

        6. Code Quality
        Code reviews and static analysis will ensure maintainability.
        Code coverage targets will be set at 80%.

        7. Compatibility Testing
        Cross-browser and cross-platform testing will be done.
        Docker containerization will ensure portability.
        """

        result = analyze_quality_plan(
            plan_text, self.srs_category_scores,
            self.srs_present, self.srs_missing
        )

        self.assertGreater(result["overall_coverage"], 80)
        self.assertGreater(result["achievable_quality"], 70)
        self.assertEqual(result["plan_strength"], "Strong")
        # All 7 categories should be covered
        for cat in ALL_CATEGORIES:
            self.assertTrue(
                result["category_coverage"][cat]["covered"],
                f"{cat} should be covered"
            )

    def test_partial_coverage_plan(self):
        """A plan covering some categories should get moderate scores."""
        plan_text = """
        Quality Plan

        We will perform functional testing including unit tests and
        integration tests for the core features.

        Security will be addressed through penetration testing.
        """

        result = analyze_quality_plan(
            plan_text, self.srs_category_scores,
            self.srs_present, self.srs_missing
        )

        self.assertTrue(result["category_coverage"]["Functionality"]["covered"])
        self.assertTrue(result["category_coverage"]["Security"]["covered"])
        self.assertFalse(result["category_coverage"]["Portability"]["covered"])
        self.assertLess(result["overall_coverage"], 100)

    def test_empty_plan(self):
        """An empty plan should return zero coverage."""
        result = analyze_quality_plan(
            "", self.srs_category_scores,
            self.srs_present, self.srs_missing
        )

        self.assertEqual(result["overall_coverage"], 0)
        self.assertEqual(result["achievable_quality"], 0)
        self.assertEqual(result["plan_strength"], "Weak")

    def test_no_coverage_plan(self):
        """A plan with zero relevant keywords should score poorly."""
        plan_text = """
        This document outlines the project timeline and milestones.
        Phase 1 will complete in March. Phase 2 in April.
        The team consists of 5 developers and 1 project manager.
        Weekly meetings are scheduled for Mondays.
        """

        result = analyze_quality_plan(
            plan_text, self.srs_category_scores,
            self.srs_present, self.srs_missing
        )

        self.assertLessEqual(result["overall_coverage"], 20)
        self.assertEqual(result["plan_strength"], "Weak")

    def test_suggestions_for_uncovered_categories(self):
        """Suggestions should appear for SRS categories not in the plan."""
        plan_text = "We will do functional testing and unit tests."

        result = analyze_quality_plan(
            plan_text, self.srs_category_scores,
            self.srs_present, self.srs_missing
        )

        suggestion_cats = [s["category"] for s in result["suggestions"]]
        # Security is in SRS but not in this simple plan
        self.assertIn("Security", suggestion_cats)

    def test_proactive_coverage_suggestion(self):
        """Plan covering categories NOT in SRS should get 'proactive' suggestion."""
        plan_text = """
        We will do functional testing.
        Cross-browser compatibility testing will ensure portability.
        """

        result = analyze_quality_plan(
            plan_text, self.srs_category_scores,
            self.srs_present, self.srs_missing
        )

        proactive = [s for s in result["suggestions"] if s.get("type") == "proactive"]
        # Portability is NOT in SRS but IS in the plan
        self.assertTrue(
            any(s["category"] == "Portability" for s in proactive),
            "Should detect proactive coverage of Portability"
        )

    def test_summary_is_human_readable(self):
        """Summary should be a non-empty readable string."""
        plan_text = "Unit testing and security testing will be performed."

        result = analyze_quality_plan(
            plan_text, self.srs_category_scores,
            self.srs_present, self.srs_missing
        )

        self.assertIsInstance(result["summary"], str)
        self.assertGreater(len(result["summary"]), 50)

    def test_achievable_quality_has_proactive_bonus(self):
        """Covering categories missing from SRS should boost achievable quality."""
        plan_text_no_extra = "Functional testing and unit tests."
        plan_text_with_extra = """
        Functional testing and unit tests.
        Cross-browser and cross-platform compatibility testing.
        Code reviews and static analysis.
        """

        r1 = analyze_quality_plan(
            plan_text_no_extra, self.srs_category_scores,
            self.srs_present, self.srs_missing
        )
        r2 = analyze_quality_plan(
            plan_text_with_extra, self.srs_category_scores,
            self.srs_present, self.srs_missing
        )

        self.assertGreaterEqual(r2["achievable_quality"], r1["achievable_quality"])


class TestEvidenceFinding(unittest.TestCase):
    """Test the _find_evidence helper."""

    def test_finds_keywords(self):
        text = "We will conduct penetration testing and vulnerability scanning."
        keywords = ["penetration test", "vulnerability"]
        evidence = _find_evidence(text.lower(), text, keywords)
        self.assertGreater(len(evidence), 0)

    def test_no_false_positives(self):
        text = "The weather today is sunny and warm."
        keywords = ["penetration test", "vulnerability"]
        evidence = _find_evidence(text.lower(), text, keywords)
        self.assertEqual(len(evidence), 0)


# ──────────────────────────────────────────────────────────────────────────── #
# API route tests                                                               #
# ──────────────────────────────────────────────────────────────────────────── #

def _make_docx(paragraphs):
    """Create a minimal DOCX in memory."""
    from docx import Document as DocxDocument
    doc = DocxDocument()
    for p in paragraphs:
        doc.add_paragraph(p)
    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf


class TestQualityPlanAPI(unittest.TestCase):
    """Test the /api/quality-plan/<analysis_id> endpoints."""

    @classmethod
    def setUpClass(cls):
        from app import create_app
        cls.app = create_app()
        cls.app.config["TESTING"] = True
        cls.client = cls.app.test_client()

        # First: upload and analyze an SRS file to get an analysis_id
        srs_paragraphs = [
            "Software Requirements Specification",
            "The system shall authenticate users through a secure login mechanism.",
            "The system must encrypt all sensitive data at rest and in transit.",
            "The system should respond to user requests within 2 seconds.",
            "The system shall maintain 99.9% uptime availability.",
            "The system must provide clear error messages to users.",
            "The system should support both PDF and DOCX file uploads.",
            "The system shall log all user actions for audit purposes.",
            "The system must validate all input data before processing.",
        ]

        # Upload SRS
        buf = _make_docx(srs_paragraphs)
        resp = cls.client.post(
            "/api/upload",
            data={"file": (buf, "test_srs.docx")},
            content_type="multipart/form-data",
        )
        assert resp.status_code == 200, f"Upload failed: {resp.get_json()}"
        cls.file_id = resp.get_json()["file_id"]

        # Analyze SRS
        resp = cls.client.post("/api/analyze", json={"file_id": cls.file_id})
        assert resp.status_code == 200, f"Analyze failed: {resp.get_json()}"
        cls.analysis_id = cls.file_id

    def test_01_get_quality_plan_before_upload(self):
        """GET should return 404 if no plan uploaded yet."""
        # Use a fresh analysis_id that won't have a plan
        resp = self.client.get(f"/api/quality-plan/{self.analysis_id}_noplan")
        data = resp.get_json()
        self.assertEqual(resp.status_code, 404)
        self.assertFalse(data["has_plan"])

    def test_02_upload_quality_plan_no_file(self):
        """POST without file should return 400."""
        resp = self.client.post(f"/api/quality-plan/{self.analysis_id}")
        self.assertEqual(resp.status_code, 400)

    def test_03_upload_quality_plan_bad_analysis_id(self):
        """POST to non-existent analysis should return 404."""
        buf = _make_docx(["dummy content"])
        resp = self.client.post(
            "/api/quality-plan/nonexistent_id_12345",
            data={"file": (buf, "plan.docx")},
            content_type="multipart/form-data",
        )
        self.assertEqual(resp.status_code, 404)

    def test_04_upload_and_analyze_quality_plan(self):
        """Full quality plan upload + analysis workflow."""
        plan_paragraphs = [
            "Quality Assurance Plan",
            "1. Functional Testing",
            "Unit tests and integration tests will verify all functional requirements.",
            "Test cases will cover all acceptance criteria.",
            "2. Security Measures",
            "We will perform penetration testing and vulnerability assessment.",
            "Authentication and access control mechanisms will be verified.",
            "3. Performance Testing",
            "Load testing will verify response time requirements.",
            "Throughput benchmarks will be established.",
            "4. Usability Review",
            "User acceptance testing with real users.",
            "Accessibility compliance with WCAG guidelines.",
        ]

        buf = _make_docx(plan_paragraphs)
        resp = self.client.post(
            f"/api/quality-plan/{self.analysis_id}",
            data={"file": (buf, "quality_plan.docx")},
            content_type="multipart/form-data",
        )

        self.assertEqual(resp.status_code, 200)
        result = resp.get_json()
        self.assertTrue(result["success"])
        self.assertIn("overall_coverage", result)
        self.assertIn("achievable_quality", result)
        self.assertIn("plan_strength", result)
        self.assertIn("category_coverage", result)
        self.assertIn("suggestions", result)
        self.assertIn("summary", result)

        # Coverage should be > 0 since the plan covers several categories
        self.assertGreater(result["overall_coverage"], 0)
        self.assertGreater(result["achievable_quality"], 0)

        # Functionality and Security should be covered
        self.assertTrue(result["category_coverage"]["Functionality"]["covered"])
        self.assertTrue(result["category_coverage"]["Security"]["covered"])

    def test_05_get_quality_plan_after_upload(self):
        """GET should return the plan after it's been uploaded."""
        # First ensure a plan exists by uploading one
        plan_paragraphs = [
            "Simple QA Plan",
            "Unit tests and functional testing will be done.",
            "Penetration testing for security.",
        ]
        buf = _make_docx(plan_paragraphs)
        self.client.post(
            f"/api/quality-plan/{self.analysis_id}",
            data={"file": (buf, "qp.docx")},
            content_type="multipart/form-data",
        )

        resp = self.client.get(f"/api/quality-plan/{self.analysis_id}")
        data = resp.get_json()
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(data["has_plan"])
        self.assertIn("overall_coverage", data)
        self.assertIn("category_coverage", data)

    def test_06_upload_invalid_file_type(self):
        """Uploading a .txt file should be rejected."""
        data = {"file": (io.BytesIO(b"just plain text"), "plan.txt")}
        resp = self.client.post(
            f"/api/quality-plan/{self.analysis_id}",
            data=data,
            content_type="multipart/form-data",
        )
        self.assertEqual(resp.status_code, 400)


if __name__ == "__main__":
    unittest.main()
