"""
services/quality_scorer.py
===========================
Summarise the ISO/IEC 9126 category distribution of classified requirements,
detect the software domain, and generate domain-aware recommendations.

**Important design decision** (Feb 2026):
The SRS analysis does *not* produce a quality score. It only tells the user
which quality categories are present or missing in the SRS and gives
domain-specific suggestions.  Quality estimation is done separately when
the user uploads a Quality Plan (see quality_plan_analyzer.py).

Functions
---------
calculate_category_scores()    – Per-category requirement counts & coverage
detect_domain()                – Identify the system domain from requirement text
generate_recommendations()     – Domain-aware improvement suggestions
generate_gap_analysis()        – Categories missing or insufficient
build_full_report()            – One-shot helper combining everything
"""

from collections import Counter
from typing import Any, Dict, List, Optional

from utils.logger import app_logger

# --------------------------------------------------------------------------- #
# ISO/IEC 9126 category weights  (used internally & by quality plan analyzer)   #
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

# --------------------------------------------------------------------------- #
# Domain detection                                                              #
# --------------------------------------------------------------------------- #

DOMAIN_KEYWORDS: Dict[str, List[str]] = {
    "Banking / Finance": [
        "bank", "financial", "transaction", "payment",
        "ledger", "credit", "debit", "loan", "interest", "atm",
        "deposit", "withdrawal", "currency", "fund",
        "invoice", "billing", "fintech", "money transfer",
        "mortgage", "forex", "stock", "trading", "wealth",
    ],
    "Healthcare": [
        "patient", "medical", "health", "clinical", "diagnosis",
        "hospital", "doctor", "prescription", "emr", "ehr", "hipaa",
        "pharmacy", "lab result", "treatment", "nursing", "vital sign",
    ],
    "E-commerce": [
        "shop", "cart", "product", "catalog", "order", "checkout",
        "shipping", "inventory", "marketplace", "wishlist", "discount",
        "coupon", "merchant", "storefront", "retail", "add to cart",
    ],
    "Education / LMS": [
        "student", "course", "grade", "enroll", "curriculum",
        "classroom", "teacher", "learning", "lms", "assessment",
        "assignment", "lecture", "exam", "semester", "school",
        "faculty", "syllabus", "attendance", "lesson", "quiz",
    ],
    "Library Management": [
        "book", "borrow", "return book", "library", "patron",
        "catalog", "isbn", "circulation", "fine", "overdue",
        "reservation", "shelf", "member", "lending", "librarian",
        "due date", "checkout", "renewal", "collection",
    ],
    "Government / Public Sector": [
        "citizen", "regulation", "compliance", "public sector",
        "federal", "government", "municipality", "permit", "license",
        "voting", "tax", "census",
    ],
    "IoT / Embedded": [
        "sensor", "device", "firmware", "embedded", "gateway",
        "telemetry", "mqtt", "actuator", "iot", "microcontroller",
    ],
    "Telecom / Networking": [
        "network", "bandwidth", "latency", "protocol", "telecom",
        "subscriber", "5g", "lte", "voip", "router",
    ],
    "Hotel / Hospitality": [
        "hotel", "reservation", "booking", "guest", "room",
        "check-in", "check-out", "housekeeping", "reception",
        "amenity", "hospitality", "concierge", "occupancy",
    ],
    "Restaurant / Food Service": [
        "menu", "order", "table", "restaurant", "kitchen",
        "waiter", "bill", "cuisine", "reservation", "dine",
        "takeaway", "delivery", "chef", "dish",
    ],
    "HR / Payroll": [
        "employee", "payroll", "salary", "leave", "attendance",
        "recruitment", "onboarding", "performance review", "hr",
        "benefits", "timesheet", "appraisal", "workforce",
    ],
    "Inventory / Warehouse": [
        "warehouse", "stock", "sku", "goods", "shipment",
        "supply chain", "dispatch", "receiving", "storage",
        "reorder", "inbound", "outbound", "logistics",
    ],
}

# Which ISO 9126 categories are *especially* critical for each domain
DOMAIN_CRITICAL_CATEGORIES: Dict[str, Dict[str, str]] = {
    "Banking / Finance": {
        "Security":    "critical",
        "Reliability": "critical",
        "Functionality": "high",
        "Efficiency":  "high",
    },
    "Healthcare": {
        "Security":    "critical",
        "Reliability": "critical",
        "Usability":   "high",
        "Functionality": "high",
    },
    "E-commerce": {
        "Security":    "high",
        "Usability":   "high",
        "Efficiency":  "high",
        "Portability": "high",
    },
    "Education / LMS": {
        "Usability":   "critical",
        "Functionality": "high",
        "Portability": "high",
    },
    "Library Management": {
        "Usability":   "critical",
        "Reliability": "high",
        "Maintainability": "high",
    },
    "Government / Public Sector": {
        "Security":    "critical",
        "Reliability": "critical",
        "Usability":   "high",
    },
    "IoT / Embedded": {
        "Reliability": "critical",
        "Efficiency":  "critical",
        "Security":    "high",
    },
    "Telecom / Networking": {
        "Efficiency":  "critical",
        "Reliability": "critical",
        "Security":    "high",
    },
    "Hotel / Hospitality": {
        "Usability":   "critical",
        "Reliability": "high",
        "Functionality": "high",
    },
    "Restaurant / Food Service": {
        "Usability":   "critical",
        "Efficiency":  "high",
        "Reliability": "high",
    },
    "HR / Payroll": {
        "Security":    "critical",
        "Reliability": "high",
        "Functionality": "high",
    },
    "Inventory / Warehouse": {
        "Reliability": "critical",
        "Efficiency":  "high",
        "Functionality": "high",
    },
}


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


def detect_domain(
    classified_requirements: List[Dict[str, Any]],
    raw_text: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Detect the software domain from requirement text and (optionally) the
    full document text.

    Returns:
        {
            "domain":      "Banking / Finance"  (or "General" if unclear),
            "confidence":  0.0 – 1.0,
            "critical_categories": { "Security": "critical", ... },
        }
    """
    # Combine all requirement text + raw text into one searchable blob
    text_parts = [r.get("text", "") for r in classified_requirements]
    if raw_text:
        text_parts.append(raw_text)
    blob = " ".join(text_parts).lower()

    scores: Dict[str, int] = {}
    for domain, keywords in DOMAIN_KEYWORDS.items():
        hits = sum(1 for kw in keywords if kw in blob)
        if hits > 0:
            scores[domain] = hits

    if not scores:
        return {
            "domain": "General",
            "confidence": 0.0,
            "critical_categories": {},
        }

    best_domain = max(scores, key=scores.get)
    best_hits = scores[best_domain]
    max_possible = len(DOMAIN_KEYWORDS.get(best_domain, []))
    confidence = round(min(best_hits / max(max_possible * 0.4, 1), 1.0), 2)

    return {
        "domain":              best_domain,
        "confidence":          confidence,
        "critical_categories": DOMAIN_CRITICAL_CATEGORIES.get(best_domain, {}),
    }


def generate_recommendations(
    category_scores: Dict[str, Any],
    domain_info: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, str]]:
    """
    Produce actionable, domain-aware, category-level recommendations.

    The SRS analysis does NOT assign a quality score — it just highlights
    what is present, what is missing, and what matters most given the
    detected domain.

    Args:
        category_scores: Output of calculate_category_scores().
        domain_info:     Output of detect_domain() (optional).

    Returns:
        List of recommendation dicts with keys: category, priority, message.
    """
    recommendations: List[Dict[str, str]] = []
    domain = (domain_info or {}).get("domain", "General")
    critical_cats = (domain_info or {}).get("critical_categories", {})

    for cat in ALL_CATEGORIES:
        data = category_scores.get(cat, {})
        count = data.get("count", 0)
        min_rec = data.get("min_recommended", 1)
        domain_importance = critical_cats.get(cat)          # "critical" | "high" | None

        if count == 0:
            # Determine priority based on domain
            if domain_importance == "critical":
                priority = "critical"
                suffix = (
                    f" This is *critical* for a {domain} system — "
                    f"missing {cat.lower()} requirements is a serious risk."
                )
            elif domain_importance == "high":
                priority = "high"
                suffix = (
                    f" For a {domain} system, {cat.lower()} is highly important."
                )
            else:
                priority = "high"
                suffix = ""

            recommendations.append({
                "category": cat,
                "priority": priority,
                "message": (
                    f"No {cat} requirements found in the SRS. "
                    f"Consider adding at least {min_rec} requirement(s) "
                    f"covering {cat.lower()} aspects.{suffix}"
                ),
            })
        elif count < min_rec:
            priority = "high" if domain_importance in ("critical", "high") else "medium"
            recommendations.append({
                "category": cat,
                "priority": priority,
                "message": (
                    f"{cat} has only {count} requirement(s) — "
                    f"recommended minimum is {min_rec}. "
                    "Consider adding more coverage."
                    + (
                        f" Especially important for a {domain} system."
                        if domain_importance
                        else ""
                    )
                ),
            })

    # Sort: critical → high → medium → low
    priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    recommendations.sort(key=lambda r: priority_order.get(r["priority"], 99))

    app_logger.info(f"Generated {len(recommendations)} recommendations (domain={domain})")
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


def build_full_report(
    classified_requirements: List[Dict[str, Any]],
    raw_text: Optional[str] = None,
) -> Dict[str, Any]:
    """
    One-shot helper that builds the complete SRS summary report.

    The report tells the user **what is present and what is missing** in the
    SRS, detects the software domain, and generates domain-aware
    recommendations.  It does NOT produce a quality score — that comes from
    the Quality Plan comparison step.

    Args:
        classified_requirements: Output of classifier.classify_batch().
        raw_text:                Full document text (optional, improves domain detection).

    Returns:
        {
            total_requirements,
            category_scores,
            domain,                  ← NEW
            recommendations,
            gap_analysis,
            categories_present,
            categories_missing,
        }
    """
    total = len(classified_requirements)
    category_scores = calculate_category_scores(classified_requirements)
    domain_info = detect_domain(classified_requirements, raw_text)
    recommendations = generate_recommendations(category_scores, domain_info)
    gap_analysis = generate_gap_analysis(category_scores)

    categories_present = [
        cat for cat in ALL_CATEGORIES if category_scores.get(cat, {}).get("count", 0) > 0
    ]
    categories_missing = [cat for cat in ALL_CATEGORIES if cat not in categories_present]

    app_logger.info(
        f"SRS summary built: {total} reqs, domain={domain_info['domain']}, "
        f"present={len(categories_present)}/{len(ALL_CATEGORIES)}"
    )

    return {
        "total_requirements":   total,
        "category_scores":      category_scores,
        "domain":               domain_info,
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
