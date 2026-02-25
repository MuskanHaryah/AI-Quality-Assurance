"""
services/quality_plan_analyzer.py
==================================
Analyze a Quality Plan document against an existing SRS analysis.

How it works
------------
1. Extract text from the uploaded Quality Plan (PDF/DOCX).
2. For each ISO/IEC 9126 category that the SRS analysis identified,
   search the Quality Plan text for evidence that the plan addresses it.
3. Calculate:
   - Per-category coverage (covered / not covered + evidence snippets)
   - Overall coverage percentage
   - Achievable quality score (if the plan is fully executed)
   - Improvement suggestions for uncovered categories

This is keyword/phrase-based matching — honest and appropriate for a
semester project. No fake deep-learning magic.
"""

import re
from typing import Any, Dict, List

from utils.logger import app_logger


# --------------------------------------------------------------------------- #
# Category keyword dictionaries                                                 #
# Each category has phrases that indicate a quality plan addresses it          #
# --------------------------------------------------------------------------- #

CATEGORY_EVIDENCE_KEYWORDS: Dict[str, List[str]] = {
    "Functionality": [
        "functional test", "feature test", "unit test", "integration test",
        "functional requirement", "feature validation", "acceptance test",
        "test case", "test scenario", "functional verification",
        "use case test", "requirement verification", "system test",
        "functional coverage", "feature coverage", "regression test",
    ],
    "Security": [
        "security test", "penetration test", "vulnerability", "authentication",
        "authorization", "encryption", "access control", "security audit",
        "security review", "threat model", "security scan", "owasp",
        "sql injection", "xss", "csrf", "security compliance", "firewall",
        "intrusion detection", "data protection", "privacy", "secure coding",
    ],
    "Reliability": [
        "reliability test", "stress test", "load test", "failover",
        "recovery test", "fault tolerance", "availability", "uptime",
        "mean time between failure", "mtbf", "backup", "disaster recovery",
        "error handling", "exception handling", "retry", "redundancy",
        "high availability", "reliability metric", "failure rate",
    ],
    "Efficiency": [
        "performance test", "load test", "response time", "throughput",
        "latency", "benchmark", "performance metric", "resource usage",
        "memory usage", "cpu usage", "optimization", "scalability",
        "capacity planning", "performance baseline", "stress test",
        "performance requirement", "sla", "service level",
    ],
    "Usability": [
        "usability test", "user experience", "ux", "ui test",
        "user acceptance", "accessibility", "user interface",
        "user feedback", "user survey", "heuristic evaluation",
        "navigation test", "readability", "user training",
        "user documentation", "help documentation", "ease of use",
        "wcag", "508 compliance", "a11y",
    ],
    "Maintainability": [
        "code review", "code quality", "static analysis", "code coverage",
        "documentation", "coding standard", "refactoring", "technical debt",
        "modularity", "maintainability index", "sonarqube", "lint",
        "code complexity", "cyclomatic complexity", "design review",
        "architecture review", "api documentation",
    ],
    "Portability": [
        "portability test", "cross-platform", "cross-browser",
        "compatibility test", "migration", "platform support",
        "browser compatibility", "operating system", "docker",
        "containerization", "deployment", "environment", "configuration",
        "installation test", "platform independent", "mobile compatible",
    ],
}

# How much each category contributes to achievable quality (same weights as scorer)
CATEGORY_WEIGHTS: Dict[str, float] = {
    "Functionality":   0.30,
    "Security":        0.20,
    "Reliability":     0.15,
    "Efficiency":      0.15,
    "Usability":       0.10,
    "Maintainability": 0.05,
    "Portability":     0.05,
}

ALL_CATEGORIES = list(CATEGORY_WEIGHTS.keys())


# --------------------------------------------------------------------------- #
# Public API                                                                    #
# --------------------------------------------------------------------------- #

def analyze_quality_plan(
    plan_text: str,
    srs_category_scores: Dict[str, Any],
    srs_categories_present: List[str],
    srs_categories_missing: List[str],
) -> Dict[str, Any]:
    """
    Analyze a quality plan document against an SRS analysis.

    Args:
        plan_text:              Cleaned text extracted from the quality plan document.
        srs_category_scores:    Category scores from the SRS analysis.
        srs_categories_present: Categories found in the SRS.
        srs_categories_missing: Categories missing from the SRS.

    Returns:
        {
            "category_coverage":  { cat: {covered, evidence, srs_count, importance}, ... },
            "overall_coverage":   float (0-100),
            "achievable_quality": float (0-100),
            "plan_strength":      "Strong" | "Moderate" | "Weak",
            "suggestions":        [ {category, priority, message}, ... ],
            "summary":            str,
        }
    """
    if not plan_text or not plan_text.strip():
        return _empty_result("Quality plan document is empty or unreadable.")

    plan_text_lower = plan_text.lower()

    # ── 1. Check each category for coverage evidence ─────────────────── #
    category_coverage: Dict[str, Any] = {}
    covered_count = 0
    covered_weight = 0.0

    for cat in ALL_CATEGORIES:
        keywords = CATEGORY_EVIDENCE_KEYWORDS.get(cat, [])
        evidence = _find_evidence(plan_text_lower, plan_text, keywords)
        srs_count = srs_category_scores.get(cat, {}).get("count", 0)
        is_in_srs = cat in srs_categories_present
        is_covered = len(evidence) > 0

        if is_covered:
            covered_count += 1
            covered_weight += CATEGORY_WEIGHTS.get(cat, 0)

        category_coverage[cat] = {
            "covered":           is_covered,
            "evidence_snippets": evidence[:5],  # max 5 snippets per category
            "evidence_count":    len(evidence),
            "in_srs":            is_in_srs,
            "srs_requirement_count": srs_count,
            "weight":            CATEGORY_WEIGHTS.get(cat, 0),
            "importance":        _importance_label(CATEGORY_WEIGHTS.get(cat, 0)),
        }

    # ── 2. Calculate overall coverage ────────────────────────────────── #
    # Coverage = weighted % of SRS-present categories that the plan covers
    srs_present_set = set(srs_categories_present)
    if srs_present_set:
        covered_srs_weight = sum(
            CATEGORY_WEIGHTS.get(cat, 0)
            for cat in srs_present_set
            if category_coverage.get(cat, {}).get("covered", False)
        )
        total_srs_weight = sum(CATEGORY_WEIGHTS.get(cat, 0) for cat in srs_present_set)
        overall_coverage = round((covered_srs_weight / total_srs_weight) * 100, 2) if total_srs_weight > 0 else 0.0
    else:
        overall_coverage = 0.0

    # ── 3. Calculate achievable quality ──────────────────────────────── #
    # If the plan is followed, quality = weighted sum of covered categories
    # Bonus points for covering categories NOT in the SRS (proactive)
    base_quality = covered_weight * 100  # max 100 if all covered
    # Bonus: if plan covers extra categories missing from SRS, that's proactive
    proactive_bonus = sum(
        CATEGORY_WEIGHTS.get(cat, 0) * 20  # up to 20 pts extra per missing-but-planned cat
        for cat in srs_categories_missing
        if category_coverage.get(cat, {}).get("covered", False)
    )
    achievable_quality = min(round(base_quality + proactive_bonus, 2), 100.0)

    # ── 4. Determine plan strength ───────────────────────────────────── #
    if overall_coverage >= 80:
        plan_strength = "Strong"
    elif overall_coverage >= 50:
        plan_strength = "Moderate"
    else:
        plan_strength = "Weak"

    # ── 5. Generate improvement suggestions ──────────────────────────── #
    suggestions = _generate_suggestions(
        category_coverage, srs_categories_present, srs_categories_missing, overall_coverage
    )

    # ── 6. Generate summary ──────────────────────────────────────────── #
    summary = _generate_summary(
        covered_count, len(ALL_CATEGORIES),
        srs_categories_present, overall_coverage, achievable_quality, plan_strength
    )

    app_logger.info(
        f"Quality plan analyzed | coverage={overall_coverage:.1f}% | "
        f"achievable={achievable_quality:.1f}% | strength={plan_strength} | "
        f"covered={covered_count}/{len(ALL_CATEGORIES)}"
    )

    return {
        "category_coverage":  category_coverage,
        "overall_coverage":   overall_coverage,
        "achievable_quality": achievable_quality,
        "plan_strength":      plan_strength,
        "suggestions":        suggestions,
        "summary":            summary,
    }


# --------------------------------------------------------------------------- #
# Evidence finding                                                              #
# --------------------------------------------------------------------------- #

def _find_evidence(text_lower: str, original_text: str, keywords: List[str]) -> List[str]:
    """
    Search the plan text for keyword matches and return surrounding context snippets.

    Returns a list of short evidence strings like:
        "...performance test will be conducted on every release..."
    """
    evidence: List[str] = []
    seen_positions: set = set()

    for keyword in keywords:
        # Find all occurrences
        for match in re.finditer(re.escape(keyword), text_lower):
            start = match.start()
            # Avoid duplicate snippets from overlapping regions
            bucket = start // 80
            if bucket in seen_positions:
                continue
            seen_positions.add(bucket)

            # Extract surrounding context (±60 chars)
            snippet_start = max(0, start - 60)
            snippet_end = min(len(original_text), match.end() + 60)
            snippet = original_text[snippet_start:snippet_end].strip()
            # Clean up partial words at edges
            snippet = re.sub(r"^\S*\s", "", snippet)
            snippet = re.sub(r"\s\S*$", "", snippet)
            if snippet:
                evidence.append(f"...{snippet}...")

    return evidence


# --------------------------------------------------------------------------- #
# Suggestion generation                                                         #
# --------------------------------------------------------------------------- #

def _generate_suggestions(
    category_coverage: Dict[str, Any],
    srs_present: List[str],
    srs_missing: List[str],
    overall_coverage: float,
) -> List[Dict[str, str]]:
    """Generate actionable improvement suggestions."""
    suggestions = []

    # Critical: SRS categories that the plan doesn't cover
    for cat in srs_present:
        data = category_coverage.get(cat, {})
        if not data.get("covered", False):
            suggestions.append({
                "category": cat,
                "priority": "high",
                "type":     "uncovered",
                "message": (
                    f"Your SRS has {data.get('srs_requirement_count', 0)} {cat} requirement(s), "
                    f"but your Quality Plan does not address {cat} testing/validation. "
                    f"Add {cat.lower()} testing activities to your plan."
                ),
            })

    # Medium: Categories missing from both SRS and plan
    for cat in srs_missing:
        data = category_coverage.get(cat, {})
        if not data.get("covered", False):
            suggestions.append({
                "category": cat,
                "priority": "medium",
                "type":     "both_missing",
                "message": (
                    f"{cat} is missing from both your SRS and Quality Plan. "
                    f"Consider adding {cat.lower()} requirements to your SRS "
                    f"and corresponding test activities to your plan."
                ),
            })

    # Info: Categories the plan covers proactively (not in SRS)
    for cat in srs_missing:
        data = category_coverage.get(cat, {})
        if data.get("covered", False):
            suggestions.append({
                "category": cat,
                "priority": "info",
                "type":     "proactive",
                "message": (
                    f"Good: Your Quality Plan covers {cat} even though the SRS doesn't "
                    f"mention it explicitly. Consider adding {cat.lower()} requirements "
                    f"to your SRS to formalize this."
                ),
            })

    # General suggestion if coverage is low
    if overall_coverage < 50:
        suggestions.insert(0, {
            "category": "General",
            "priority": "critical",
            "type":     "low_coverage",
            "message": (
                f"Quality plan coverage is only {overall_coverage:.0f}%. "
                f"The plan does not adequately address the quality factors identified "
                f"in your SRS. Major revision recommended."
            ),
        })

    # Sort: critical → high → medium → info
    priority_order = {"critical": 0, "high": 1, "medium": 2, "info": 3}
    suggestions.sort(key=lambda s: priority_order.get(s["priority"], 99))

    return suggestions


# --------------------------------------------------------------------------- #
# Summary generation                                                            #
# --------------------------------------------------------------------------- #

def _generate_summary(
    covered: int, total: int,
    srs_present: List[str],
    coverage: float, achievable: float, strength: str,
) -> str:
    """Generate a human-readable summary paragraph."""
    lines = []

    lines.append(
        f"Your Quality Plan covers {covered} out of {total} ISO/IEC 9126 quality categories."
    )

    if srs_present:
        lines.append(
            f"Your SRS identified requirements in {len(srs_present)} categories. "
            f"The plan covers {coverage:.0f}% of these categories (weighted by importance)."
        )

    if strength == "Strong":
        lines.append(
            f"If this plan is fully executed, the achievable quality score is {achievable:.0f}%. "
            "This is a strong quality plan that addresses most identified quality factors."
        )
    elif strength == "Moderate":
        lines.append(
            f"If this plan is fully executed, the achievable quality score is {achievable:.0f}%. "
            "The plan has room for improvement — some quality factors are not addressed."
        )
    else:
        lines.append(
            f"If this plan is fully executed, the achievable quality score would only be {achievable:.0f}%. "
            "Significant gaps exist. Review the suggestions below to strengthen your plan."
        )

    return " ".join(lines)


# --------------------------------------------------------------------------- #
# Helpers                                                                       #
# --------------------------------------------------------------------------- #

def _importance_label(weight: float) -> str:
    if weight >= 0.20:
        return "Critical"
    elif weight >= 0.10:
        return "Important"
    else:
        return "Supplementary"


def _empty_result(reason: str) -> Dict[str, Any]:
    return {
        "category_coverage":  {cat: {"covered": False, "evidence_snippets": [], "evidence_count": 0,
                                      "in_srs": False, "srs_requirement_count": 0,
                                      "weight": CATEGORY_WEIGHTS.get(cat, 0),
                                      "importance": _importance_label(CATEGORY_WEIGHTS.get(cat, 0))}
                                for cat in ALL_CATEGORIES},
        "overall_coverage":   0.0,
        "achievable_quality": 0.0,
        "plan_strength":      "Weak",
        "suggestions":        [{"category": "General", "priority": "critical", "type": "error",
                                "message": reason}],
        "summary":            reason,
    }
