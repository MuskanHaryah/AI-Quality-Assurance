"""
database/queries.py
===================
All database read/write operations for QualityMapAI.

All functions accept optional conn parameter for testability;
when omitted they open their own connection via db_connection().
"""

import json
from typing import Any, Dict, List, Optional

from database.db import db_connection, get_connection
from utils.logger import app_logger


# ──────────────────────────────────────────────────────────────────────────── #
# UPLOADS                                                                       #
# ──────────────────────────────────────────────────────────────────────────── #

def save_upload(upload: Dict[str, Any]) -> bool:
    """
    Insert a new upload record.

    Args:
        upload: Dict with keys matching the uploads table columns.
                Required: id, filename, original_name, file_path, file_type, size_bytes

    Returns:
        True on success.
    """
    sql = """
        INSERT INTO uploads (id, filename, original_name, file_path, file_type, size_bytes, status)
        VALUES (:id, :filename, :original_name, :file_path, :file_type, :size_bytes, :status)
    """
    with db_connection() as conn:
        conn.execute(sql, {
            "id":            upload["id"],
            "filename":      upload["filename"],
            "original_name": upload.get("original_name", upload["filename"]),
            "file_path":     upload["file_path"],
            "file_type":     upload.get("file_type", "unknown"),
            "size_bytes":    upload.get("size_bytes", 0),
            "status":        upload.get("status", "uploaded"),
        })
    app_logger.info(f"Upload saved: id={upload['id']}")
    return True


def get_upload(upload_id: str) -> Optional[Dict[str, Any]]:
    """Fetch a single upload by its ID. Returns None if not found."""
    sql = "SELECT * FROM uploads WHERE id = ?"
    with db_connection() as conn:
        row = conn.execute(sql, (upload_id,)).fetchone()
    return dict(row) if row else None


def update_upload_status(upload_id: str, status: str) -> bool:
    """Update the status field of an upload record."""
    sql = "UPDATE uploads SET status = ? WHERE id = ?"
    with db_connection() as conn:
        conn.execute(sql, (status, upload_id))
    return True


def get_recent_uploads(limit: int = 10) -> List[Dict[str, Any]]:
    """Return the most recent uploads ordered by uploaded_at DESC."""
    sql = "SELECT * FROM uploads ORDER BY uploaded_at DESC LIMIT ?"
    with db_connection() as conn:
        rows = conn.execute(sql, (limit,)).fetchall()
    return [dict(r) for r in rows]


# ──────────────────────────────────────────────────────────────────────────── #
# ANALYSES                                                                      #
# ──────────────────────────────────────────────────────────────────────────── #

def save_analysis(analysis: Dict[str, Any]) -> bool:
    """
    Insert a new analysis record.

    All complex fields (category_scores, recommendations, gap_analysis,
    categories_present, categories_missing) are serialised to JSON strings.

    Args:
        analysis: Dict with keys matching the analyses table. Required: id, upload_id.

    Returns:
        True on success.
    """
    sql = """
        INSERT INTO analyses (
            id, upload_id, total_requirements, overall_score, risk_level,
            categories_present, categories_missing,
            category_scores_json, recommendations_json, gap_analysis_json
        )
        VALUES (
            :id, :upload_id, :total_requirements, :overall_score, :risk_level,
            :categories_present, :categories_missing,
            :category_scores_json, :recommendations_json, :gap_analysis_json
        )
    """
    with db_connection() as conn:
        conn.execute(sql, {
            "id":                    analysis["id"],
            "upload_id":             analysis["upload_id"],
            "total_requirements":    analysis.get("total_requirements", 0),
            "overall_score":         analysis.get("overall_score", 0.0),
            "risk_level":            analysis.get("risk_level", "Unknown"),
            "categories_present":    json.dumps(analysis.get("categories_present", [])),
            "categories_missing":    json.dumps(analysis.get("categories_missing", [])),
            "category_scores_json":  json.dumps(analysis.get("category_scores", {})),
            "recommendations_json":  json.dumps(analysis.get("recommendations", [])),
            "gap_analysis_json":     json.dumps(analysis.get("gap_analysis", [])),
        })
    app_logger.info(
        f"Analysis saved: id={analysis['id']} score={analysis.get('overall_score', 0):.2f}"
    )
    return True


def get_analysis(analysis_id: str) -> Optional[Dict[str, Any]]:
    """
    Fetch a single analysis by ID and deserialise JSON columns.
    Returns None if not found.
    """
    sql = "SELECT * FROM analyses WHERE id = ?"
    with db_connection() as conn:
        row = conn.execute(sql, (analysis_id,)).fetchone()

    if not row:
        return None

    data = dict(row)
    # Deserialise JSON columns
    for col in ("categories_present", "categories_missing",
                "category_scores_json", "recommendations_json", "gap_analysis_json"):
        if data.get(col):
            try:
                data[col] = json.loads(data[col])
            except (json.JSONDecodeError, TypeError):
                pass

    return data


def get_recent_analyses(limit: int = 10) -> List[Dict[str, Any]]:
    """Return recent analyses joined with the filename from uploads."""
    sql = """
        SELECT a.*, u.filename, u.original_name, u.file_type, u.uploaded_at
        FROM analyses a
        JOIN uploads u ON a.upload_id = u.id
        ORDER BY a.created_at DESC
        LIMIT ?
    """
    with db_connection() as conn:
        rows = conn.execute(sql, (limit,)).fetchall()
    return [dict(r) for r in rows]


# ──────────────────────────────────────────────────────────────────────────── #
# REQUIREMENTS                                                                  #
# ──────────────────────────────────────────────────────────────────────────── #

def save_requirements(analysis_id: str, requirements: List[Dict[str, Any]]) -> bool:
    """
    Batch-insert a list of classified requirements.

    Args:
        analysis_id:   ID of the parent analysis record.
        requirements:  List of dicts from classifier.classify_batch() merged with
                       extractor data.  Required keys: text, category, confidence.

    Returns:
        True on success.
    """
    sql = """
        INSERT INTO requirements (analysis_id, requirement_text, category, confidence,
                                  keyword_strength, source_index)
        VALUES (:analysis_id, :requirement_text, :category, :confidence,
                :keyword_strength, :source_index)
    """
    rows = [
        {
            "analysis_id":      analysis_id,
            "requirement_text": r.get("text", ""),
            "category":         r.get("category", "Unknown"),
            "confidence":       r.get("confidence", 0.0),
            "keyword_strength": r.get("keyword_strength", None),
            "source_index":     r.get("source_index", r.get("index", None)),
        }
        for r in requirements
    ]

    with db_connection() as conn:
        conn.executemany(sql, rows)

    app_logger.info(f"Saved {len(rows)} requirements for analysis_id={analysis_id}")
    return True


def get_requirements(analysis_id: str) -> List[Dict[str, Any]]:
    """Return all requirements for a given analysis."""
    sql = """
        SELECT id, requirement_text, category, confidence, keyword_strength, source_index
        FROM requirements
        WHERE analysis_id = ?
        ORDER BY id ASC
    """
    with db_connection() as conn:
        rows = conn.execute(sql, (analysis_id,)).fetchall()
    return [dict(r) for r in rows]


def get_requirements_count(analysis_id: str) -> int:
    """Return the number of requirements stored for an analysis."""
    sql = "SELECT COUNT(*) FROM requirements WHERE analysis_id = ?"
    with db_connection() as conn:
        count = conn.execute(sql, (analysis_id,)).fetchone()[0]
    return count


# ──────────────────────────────────────────────────────────────────────────── #
# TRANSACTIONAL HELPERS                                                         #
# ──────────────────────────────────────────────────────────────────────────── #

def delete_analysis(analysis_id: str) -> bool:
    """
    Delete an existing analysis and its requirements (CASCADE).
    Used before re-analysis to avoid PK violations.
    """
    with db_connection() as conn:
        conn.execute("DELETE FROM requirements WHERE analysis_id = ?", (analysis_id,))
        conn.execute("DELETE FROM analyses WHERE id = ?", (analysis_id,))
    app_logger.info(f"Deleted previous analysis: {analysis_id}")
    return True


def save_full_analysis(
    analysis: Dict[str, Any],
    requirements: List[Dict[str, Any]],
    upload_status: str = "completed",
) -> bool:
    """
    Atomically save analysis + requirements + update upload status
    in a single database transaction.  If any step fails the entire
    operation is rolled back.

    Args:
        analysis:       Dict with keys matching the analyses table.
        requirements:   List of classified requirement dicts.
        upload_status:  Status to set on the parent upload record.

    Returns:
        True on success.
    """
    analysis_id = analysis["id"]
    upload_id = analysis["upload_id"]

    analysis_sql = """
        INSERT INTO analyses (
            id, upload_id, total_requirements, overall_score, risk_level,
            categories_present, categories_missing,
            category_scores_json, recommendations_json, gap_analysis_json
        )
        VALUES (
            :id, :upload_id, :total_requirements, :overall_score, :risk_level,
            :categories_present, :categories_missing,
            :category_scores_json, :recommendations_json, :gap_analysis_json
        )
    """
    req_sql = """
        INSERT INTO requirements (analysis_id, requirement_text, category, confidence,
                                  keyword_strength, source_index)
        VALUES (:analysis_id, :requirement_text, :category, :confidence,
                :keyword_strength, :source_index)
    """
    status_sql = "UPDATE uploads SET status = ? WHERE id = ?"

    req_rows = [
        {
            "analysis_id":      analysis_id,
            "requirement_text": r.get("text", ""),
            "category":         r.get("category", "Unknown"),
            "confidence":       r.get("confidence", 0.0),
            "keyword_strength": r.get("keyword_strength", None),
            "source_index":     r.get("source_index", r.get("index", None)),
        }
        for r in requirements
    ]

    with db_connection() as conn:
        # Remove previous analysis if re-analyzing
        conn.execute("DELETE FROM requirements WHERE analysis_id = ?", (analysis_id,))
        conn.execute("DELETE FROM analyses WHERE id = ?", (analysis_id,))

        conn.execute(analysis_sql, {
            "id":                    analysis_id,
            "upload_id":             upload_id,
            "total_requirements":    analysis.get("total_requirements", 0),
            "overall_score":         analysis.get("overall_score", 0.0),
            "risk_level":            analysis.get("risk_level", "Unknown"),
            "categories_present":    json.dumps(analysis.get("categories_present", [])),
            "categories_missing":    json.dumps(analysis.get("categories_missing", [])),
            "category_scores_json":  json.dumps(analysis.get("category_scores", {})),
            "recommendations_json":  json.dumps(analysis.get("recommendations", [])),
            "gap_analysis_json":     json.dumps(analysis.get("gap_analysis", [])),
        })
        conn.executemany(req_sql, req_rows)
        conn.execute(status_sql, (upload_status, upload_id))

    app_logger.info(
        f"Full analysis saved atomically: id={analysis_id} "
        f"reqs={len(req_rows)} score={analysis.get('overall_score', 0):.2f}"
    )
    return True


# ──────────────────────────────────────────────────────────────────────────── #
# QUALITY PLANS                                                                 #
# ──────────────────────────────────────────────────────────────────────────── #

def save_quality_plan(plan: Dict[str, Any]) -> bool:
    """Insert or update a quality plan record with analysis results."""
    sql = """
        INSERT OR REPLACE INTO quality_plans (
            id, analysis_id, filename, original_name, file_path, file_type,
            size_bytes, overall_coverage, achievable_quality,
            category_coverage_json, suggestions_json, status
        )
        VALUES (
            :id, :analysis_id, :filename, :original_name, :file_path, :file_type,
            :size_bytes, :overall_coverage, :achievable_quality,
            :category_coverage_json, :suggestions_json, :status
        )
    """
    with db_connection() as conn:
        conn.execute(sql, {
            "id":                     plan["id"],
            "analysis_id":            plan["analysis_id"],
            "filename":               plan["filename"],
            "original_name":          plan.get("original_name", plan["filename"]),
            "file_path":              plan["file_path"],
            "file_type":              plan.get("file_type", "unknown"),
            "size_bytes":             plan.get("size_bytes", 0),
            "overall_coverage":       plan.get("overall_coverage", 0.0),
            "achievable_quality":     plan.get("achievable_quality", 0.0),
            "category_coverage_json": json.dumps(plan.get("category_coverage", {})),
            "suggestions_json":       json.dumps(plan.get("suggestions", [])),
            "status":                 plan.get("status", "analyzed"),
        })
    app_logger.info(f"Quality plan saved: id={plan['id']} analysis_id={plan['analysis_id']}")
    return True


def get_quality_plan(plan_id: str) -> Optional[Dict[str, Any]]:
    """Fetch a quality plan by its ID, deserialising JSON columns."""
    sql = "SELECT * FROM quality_plans WHERE id = ?"
    with db_connection() as conn:
        row = conn.execute(sql, (plan_id,)).fetchone()
    if not row:
        return None
    data = dict(row)
    for col in ("category_coverage_json", "suggestions_json"):
        if data.get(col):
            try:
                data[col] = json.loads(data[col])
            except (json.JSONDecodeError, TypeError):
                pass
    return data


def get_quality_plan_by_analysis(analysis_id: str) -> Optional[Dict[str, Any]]:
    """Fetch the most recent quality plan for a given SRS analysis."""
    sql = "SELECT * FROM quality_plans WHERE analysis_id = ? ORDER BY created_at DESC LIMIT 1"
    with db_connection() as conn:
        row = conn.execute(sql, (analysis_id,)).fetchone()
    if not row:
        return None
    data = dict(row)
    for col in ("category_coverage_json", "suggestions_json"):
        if data.get(col):
            try:
                data[col] = json.loads(data[col])
            except (json.JSONDecodeError, TypeError):
                pass
    return data
