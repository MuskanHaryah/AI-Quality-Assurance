"""
services/quality_scorer.py
===========================
Calculate ISO/IEC 9126 quality scores from classified requirements.

Functions
---------
calculate_category_scores()  – Per-category requirement counts & coverage
calculate_overall_score()    – Weighted overall quality score (0–100)
generate_recommendations()   – Actionable improvement suggestions
build_full_report()          – Combine everything into one result dict
"""

from collections import Counter
from typing import Any, Dict, List

from utils.logger import app_logger

# --------------------------------------------------------------------------- #
# ISO/IEC 9126 category weights                                                 #
# (Must sum to 1.0)                                                             #
# --------------------------------------------------------------------------- #
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

# Minimum recommended number of requirements per category
MIN_RECOMMENDED = {
    "Functionality":   5,
    "Security":        3,
    "Reliability":     3,
    "Efficiency":      2,
    "Usability":       2,
    "Maintainability": 1,
    "Portability":     1,
}

# Risk thresholds for the overall score
RISK_LEVELS = [
    (80, "Low",      "green"),
    (60, "Medium",   "orange"),
    (40, "High",     "red"),
    (0,  "Critical", "darkred"),
]


# --------------------------------------------------------------------------- #
# Public API                                                                    #
# --------------------------------------------------------------------------- #

def calculate_category_scores(classified_requirements: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Count how many requirements fall into each ISO 9126 category.

    Args:
        classified_requirements: List of dicts returned by classifier.classify_batch().
                                  Each must have a "category" key.

    Returns:
        Dict keyed by category name with:
            count         – number of requirements in this category
            percentage    – share of the total (0–100)
            meets_minimum – whether count >= MIN_RECOMMENDED
            weight        – ISO weighting factor for this category
    """
    if not classified_requirements:
        return {cat: _empty_category_entry(cat) for cat in ALL_CATEGORIES}

    total = len(classified_requirements)
    counts = Counter(r["category"] for r in classified_requirements)

    scores: Dict[str, Any] = {}
    for cat in ALL_CATEGORIES:
        count = counts.get(cat, 0)
        scores[cat] = {
            "count":          count,
            "percentage":     round(count / total * 100, 2) if total else 0,
            "meets_minimum":  count >= MIN_RECOMMENDED.get(cat, 1),
            "weight":         CATEGORY_WEIGHTS[cat],
            "min_recommended": MIN_RECOMMENDED.get(cat, 1),
        }

    # Include any unexpected/unknown categories returned by the model
    for cat, count in counts.items():
        if cat not in scores:
            scores[cat] = {
                "count":           count,
                "percentage":      round(count / total * 100, 2),
                "meets_minimum":   False,
                "weight":          0.0,
                "min_recommended": 1,
            }

    app_logger.debug(f"Category scores: { {c: s['count'] for c, s in scores.items()} }")
    return scores


def calculate_overall_score(
    category_scores: Dict[str, Any],
    classified_requirements: List[Dict[str, Any]],
) -> float:
    """
    Compute a weighted overall quality score (0–100).

    The score rewards:
    - Distribution across all 7 categories (coverage bonus)
    - Average confidence of the ML predictions
    - Meeting the minimum recommended count per category

    Args:
        category_scores:            Output of calculate_category_scores().
        classified_requirements:    Raw classified list (for confidence data).

    Returns:
        Float in range 0–100.
    """
    if not classified_requirements:
        return 0.0

    total = len(classified_requirements)

    # --- Component 1: coverage score (40 points) ---
    # Each category that has ≥ 1 requirement contributes its weight × 40
    categories_present = sum(
        1 for cat in ALL_CATEGORIES if category_scores.get(cat, {}).get("count", 0) > 0
    )
    coverage_score = (categories_present / len(ALL_CATEGORIES)) * 40

    # --- Component 2: distribution balance (30 points) ---
    # How evenly requirements are spread (penalise heavy skew)
    counts = [category_scores.get(cat, {}).get("count", 0) for cat in ALL_CATEGORIES]
    present_counts = [c for c in counts if c > 0]
    if len(present_counts) > 1:
        mean_c = sum(present_counts) / len(present_counts)
        variance = sum((c - mean_c) ** 2 for c in present_counts) / len(present_counts)
        # Max variance at any realistic dataset is normalised to penalise outliers
        norm_std = (variance ** 0.5) / (mean_c + 1)
        balance_score = max(0, 30 * (1 - min(norm_std, 1)))
    else:
        balance_score = 0

    # --- Component 3: average ML confidence (30 points) ---
    confidences = [r.get("confidence", 0) for r in classified_requirements]
    avg_confidence = sum(confidences) / len(confidences) if confidences else 0
    confidence_score = (avg_confidence / 100) * 30

    overall = round(coverage_score + balance_score + confidence_score, 2)
    app_logger.info(
        f"Overall score={overall:.2f} | "
        f"coverage={coverage_score:.1f} balance={balance_score:.1f} confidence={confidence_score:.1f}"
    )
    return min(overall, 100.0)


def get_risk_level(overall_score: float) -> Dict[str, str]:
    """Return risk label and colour for the given score."""
    for threshold, label, colour in RISK_LEVELS:
        if overall_score >= threshold:
            return {"level": label, "colour": colour}
    return {"level": "Critical", "colour": "darkred"}


def generate_recommendations(
    category_scores: Dict[str, Any],
    overall_score: float,
) -> List[Dict[str, str]]:
    """
    Produce actionable, category-level recommendations.

    Args:
        category_scores: Output of calculate_category_scores().
        overall_score:   Computed overall score.

    Returns:
        List of recommendation dicts with keys: category, priority, message.
    """
    recommendations = []
    risk = get_risk_level(overall_score)

    for cat in ALL_CATEGORIES:
        data = category_scores.get(cat, {})
        count = data.get("count", 0)
        min_rec = data.get("min_recommended", 1)

        if count == 0:
            recommendations.append({
                "category": cat,
                "priority": "high",
                "message": (
                    f"No {cat} requirements found. "
                    f"Add at least {min_rec} requirement(s) covering {cat.lower()} aspects."
                ),
            })
        elif count < min_rec:
            recommendations.append({
                "category": cat,
                "priority": "medium",
                "message": (
                    f"{cat} has only {count} requirement(s) — "
                    f"minimum recommended is {min_rec}. "
                    "Consider adding more coverage."
                ),
            })

    if overall_score < 60:
        recommendations.insert(0, {
            "category": "General",
            "priority": "critical",
            "message": (
                f"Overall quality score is {overall_score:.1f}% ({risk['level']} risk). "
                "Focus on increasing coverage across missing categories before proceeding."
            ),
        })

    # Sort: critical → high → medium
    priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    recommendations.sort(key=lambda r: priority_order.get(r["priority"], 99))

    app_logger.info(f"Generated {len(recommendations)} recommendations")
    return recommendations


def generate_gap_analysis(
    category_scores: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """
    Identify categories where requirements are missing or insufficient.

    Returns:
        List of gap dicts: {category, gap_type, count, min_required, shortage}
    """
    gaps = []
    for cat in ALL_CATEGORIES:
        data = category_scores.get(cat, {})
        count = data.get("count", 0)
        min_rec = data.get("min_recommended", 1)

        if count == 0:
            gaps.append({
                "category":     cat,
                "gap_type":     "missing",
                "count":        0,
                "min_required": min_rec,
                "shortage":     min_rec,
            })
        elif count < min_rec:
            gaps.append({
                "category":     cat,
                "gap_type":     "insufficient",
                "count":        count,
                "min_required": min_rec,
                "shortage":     min_rec - count,
            })

    return gaps


def build_full_report(classified_requirements: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    One-shot helper that builds the complete scoring report.

    Args:
        classified_requirements: Output of classifier.classify_batch().

    Returns:
        {
            total_requirements,
            category_scores,
            overall_score,
            risk,
            recommendations,
            gap_analysis,
            categories_present,
            categories_missing,
        }
    """
    total = len(classified_requirements)
    category_scores = calculate_category_scores(classified_requirements)
    overall_score = calculate_overall_score(category_scores, classified_requirements)
    risk = get_risk_level(overall_score)
    recommendations = generate_recommendations(category_scores, overall_score)
    gap_analysis = generate_gap_analysis(category_scores)

    categories_present = [
        cat for cat in ALL_CATEGORIES if category_scores.get(cat, {}).get("count", 0) > 0
    ]
    categories_missing = [cat for cat in ALL_CATEGORIES if cat not in categories_present]

    return {
        "total_requirements":   total,
        "category_scores":      category_scores,
        "overall_score":        overall_score,
        "risk":                 risk,
        "recommendations":      recommendations,
        "gap_analysis":         gap_analysis,
        "categories_present":   categories_present,
        "categories_missing":   categories_missing,
    }


# --------------------------------------------------------------------------- #
# Helpers                                                                       #
# --------------------------------------------------------------------------- #

def _empty_category_entry(cat: str) -> Dict[str, Any]:
    return {
        "count":           0,
        "percentage":      0.0,
        "meets_minimum":   False,
        "weight":          CATEGORY_WEIGHTS.get(cat, 0.0),
        "min_recommended": MIN_RECOMMENDED.get(cat, 1),
    }
