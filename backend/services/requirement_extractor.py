"""
services/requirement_extractor.py
===================================
Extract individual requirement statements from plain text.

Strategy
--------
1. Split the text into candidate sentences / bullet items.
2. Score each candidate against requirement signal words.
3. Filter out candidates that are too short, too long, or non-textual.
4. Return a structured list ready for the classifier.
"""

import re
from typing import Dict, Any, List

from utils.logger import app_logger


# --------------------------------------------------------------------------- #
# Configuration                                                                 #
# --------------------------------------------------------------------------- #

# Words that strongly indicate a requirement statement
STRONG_KEYWORDS = [
    "shall", "must", "should", "will", "shall not", "must not",
    "should not", "is required", "are required", "needs to", "need to",
]

# Weaker signals — sentence may still be a requirement
WEAK_KEYWORDS = [
    "require", "provides", "supports", "enables", "allows",
    "ensures", "guarantees", "handles", "processes", "validates",
    "verifies", "maintains", "manages", "implements", "performs",
]

# Minimum / maximum meaningful requirement lengths (characters)
MIN_LENGTH = 20
MAX_LENGTH = 500


# --------------------------------------------------------------------------- #
# Public API                                                                    #
# --------------------------------------------------------------------------- #

def extract_requirements(text: str) -> Dict[str, Any]:
    """
    Parse plain text and return a list of requirement candidates.

    Args:
        text: Cleaned plain-text string from document_processor.

    Returns:
        {
            "requirements":     [ {text, source_line, has_keyword, …}, … ],
            "total_found":      int,
            "total_candidates": int,   # sentences checked
            "extraction_stats": { strong_keyword_matches, weak_keyword_matches, filtered_out }
        }
    """
    if not text or not text.strip():
        return _empty_result()

    candidates = _split_into_candidates(text)
    app_logger.debug(f"Candidates after split: {len(candidates)}")

    requirements = []
    stats = {"strong_keyword_matches": 0, "weak_keyword_matches": 0, "filtered_out": 0}

    for idx, candidate in enumerate(candidates):
        result = _evaluate_candidate(candidate, idx)

        if result is None:
            stats["filtered_out"] += 1
            continue

        if result["keyword_strength"] == "strong":
            stats["strong_keyword_matches"] += 1
        elif result["keyword_strength"] == "weak":
            stats["weak_keyword_matches"] += 1

        requirements.append(result)

    app_logger.info(
        f"Requirement extraction complete | "
        f"found={len(requirements)} / {len(candidates)} candidates | "
        f"strong={stats['strong_keyword_matches']} weak={stats['weak_keyword_matches']} "
        f"filtered={stats['filtered_out']}"
    )

    return {
        "requirements": requirements,
        "total_found": len(requirements),
        "total_candidates": len(candidates),
        "extraction_stats": stats,
    }


def get_requirement_texts(extraction_result: Dict[str, Any]) -> List[str]:
    """
    Convenience helper — return just the text strings from extract_requirements().

    Args:
        extraction_result: Dict returned by extract_requirements().

    Returns:
        List of plain-text requirement strings.
    """
    return [r["text"] for r in extraction_result.get("requirements", [])]


# --------------------------------------------------------------------------- #
# Splitting                                                                     #
# --------------------------------------------------------------------------- #

def _split_into_candidates(text: str) -> List[str]:
    """
    Split a document into candidate requirement sentences.

    Handles:
    - Numbered lists:  "1. The system shall …"
    - Bullet points:   "- The system …"  /  "• …"
    - Regular sentences terminated by . ! ?
    - Line-based requirements (one per line)

    Returns:
        Deduplicated list of stripped non-empty strings.
    """
    # First, try splitting on common list-item patterns + sentence boundaries
    # Replace bullet/numbering prefixes with a normalised delimiter
    text = re.sub(r"(?m)^\s*[\-\•\*]\s+", "\n", text)            # bullets
    text = re.sub(r"(?m)^\s*\d+[\.\)]\s+", "\n", text)           # numbered lists
    text = re.sub(r"(?m)^\s*[a-zA-Z][\.\)]\s+", "\n", text)      # lettered lists (a. b.)

    # Split on sentence-ending punctuation OR newlines
    raw_parts = re.split(r"(?<=[.!?])\s+|\n", text)

    candidates = []
    seen = set()
    for part in raw_parts:
        part = part.strip()
        # Normalise internal whitespace
        part = re.sub(r"\s+", " ", part)
        if part and part not in seen:
            candidates.append(part)
            seen.add(part)

    return candidates


# --------------------------------------------------------------------------- #
# Evaluation                                                                    #
# --------------------------------------------------------------------------- #

def _evaluate_candidate(text: str, index: int) -> Dict[str, Any] | None:
    """
    Decide whether a candidate string is a valid requirement.

    Args:
        text:  Candidate sentence string.
        index: Original position in the candidates list.

    Returns:
        Structured dict if valid, None if filtered out.
    """
    # --- length filter ---
    if len(text) < MIN_LENGTH or len(text) > MAX_LENGTH:
        return None

    # --- reject mostly-numeric or mostly-special-char strings ---
    alpha_ratio = sum(c.isalpha() for c in text) / len(text)
    if alpha_ratio < 0.4:
        return None

    text_lower = text.lower()

    # --- strong keyword check ---
    matched_strong = [kw for kw in STRONG_KEYWORDS if kw in text_lower]
    if matched_strong:
        return {
            "text": text,
            "source_index": index,
            "has_keyword": True,
            "keyword_strength": "strong",
            "matched_keywords": matched_strong,
        }

    # --- weak keyword check ---
    matched_weak = [kw for kw in WEAK_KEYWORDS if kw in text_lower]
    if matched_weak:
        return {
            "text": text,
            "source_index": index,
            "has_keyword": True,
            "keyword_strength": "weak",
            "matched_keywords": matched_weak,
        }

    # No keyword — discard
    return None


# --------------------------------------------------------------------------- #
# Helpers                                                                       #
# --------------------------------------------------------------------------- #

def _empty_result() -> Dict[str, Any]:
    return {
        "requirements": [],
        "total_found": 0,
        "total_candidates": 0,
        "extraction_stats": {
            "strong_keyword_matches": 0,
            "weak_keyword_matches": 0,
            "filtered_out": 0,
        },
    }
