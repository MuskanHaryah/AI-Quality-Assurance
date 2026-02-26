"""
routes/quality_plan.py
======================
POST /api/quality-plan/<analysis_id>  – Upload & analyze a quality plan against an SRS analysis.
GET  /api/quality-plan/<analysis_id>  – Retrieve the quality plan analysis results.

Workflow
--------
1. User uploads SRS → gets analysis with classified requirements (existing flow).
2. User uploads Quality Plan (PDF/DOCX) here → system compares it against the SRS analysis.
3. Returns: which quality categories the plan covers, achievable quality, suggestions.
"""

import time

from flask import Blueprint, jsonify, request, current_app

from database.queries import (
    get_analysis,
    get_quality_plan_by_analysis,
    save_quality_plan,
)
from services.document_processor import process_document
from services.quality_plan_analyzer import analyze_quality_plan
from utils.file_handler import save_uploaded_file
from utils.error_handler import handle_exception
from utils.logger import app_logger
from utils.validators import validate_file_size, validate_file_type

quality_plan_bp = Blueprint("quality_plan", __name__)


# --------------------------------------------------------------------------- #
# Helper: Detect if document looks like an SRS instead of a Quality Plan
# --------------------------------------------------------------------------- #
def _detect_srs_document(text: str) -> dict:
    """
    Check if the document appears to be an SRS (Software Requirements Specification)
    rather than a Quality Plan.
    
    Returns:
        {
            "is_likely_srs": bool,
            "warning": str or None,
            "srs_indicators_found": int,
            "qp_indicators_found": int
        }
    """
    text_lower = text.lower()
    
    # SRS indicators - requirement-style keywords
    srs_keywords = [
        " shall ", " must ", " should ", " will ",
        "the system shall", "the software shall", "the application shall",
        "requirement", "srs", "software requirements specification",
        "functional requirement", "non-functional requirement",
        "use case", "user story", "acceptance criteria",
    ]
    
    # Quality Plan indicators
    qp_keywords = [
        "quality plan", "test plan", "test strategy", "test case",
        "quality assurance", "qa plan", "testing approach",
        "test coverage", "defect management", "quality metric",
        "review process", "inspection", "audit", "quality objective",
        "quality standard", "iso 9126", "quality attribute",
    ]
    
    srs_count = sum(1 for kw in srs_keywords if kw in text_lower)
    qp_count = sum(1 for kw in qp_keywords if kw in text_lower)
    
    # If SRS indicators significantly outnumber QP indicators, it's likely an SRS
    is_likely_srs = srs_count > 5 and srs_count > qp_count * 2
    
    warning = None
    if is_likely_srs:
        warning = (
            "Warning: This document appears to be an SRS (Software Requirements Specification) "
            f"rather than a Quality Plan. Found {srs_count} requirement-style indicators "
            f"vs {qp_count} quality plan indicators. Please upload an actual Quality Plan document "
            "that describes testing strategies, quality metrics, and review processes."
        )
    
    return {
        "is_likely_srs": is_likely_srs,
        "warning": warning,
        "srs_indicators_found": srs_count,
        "qp_indicators_found": qp_count,
    }


@quality_plan_bp.route("/quality-plan/<analysis_id>", methods=["POST"])
@handle_exception
def upload_and_analyze_quality_plan(analysis_id):
    """Upload a quality plan PDF/DOCX and analyze it against the given SRS analysis."""
    start_time = time.time()

    # ── 1. Validate the SRS analysis exists ──────────────────────────── #
    analysis = get_analysis(analysis_id)
    if not analysis:
        return jsonify({
            "success": False,
            "error": f"No SRS analysis found for id: {analysis_id}. Analyze an SRS first.",
        }), 404

    # ── 2. Validate file upload ──────────────────────────────────────── #
    if "file" not in request.files:
        return jsonify({"success": False, "error": "No file provided. Send field name 'file'."}), 400

    file = request.files["file"]
    if not file.filename:
        return jsonify({"success": False, "error": "File has no name."}), 400

    if not validate_file_type(file.filename):
        return jsonify({
            "success": False,
            "error": "Unsupported file type. Only PDF and DOCX are accepted.",
        }), 400

    if not validate_file_size(file):
        return jsonify({
            "success": False,
            "error": "File exceeds the 10 MB size limit.",
        }), 400

    # ── 3. Save file to disk ─────────────────────────────────────────── #
    try:
        upload_folder = current_app.config["UPLOAD_FOLDER"]
        saved = save_uploaded_file(file, upload_folder)
    except Exception as exc:
        app_logger.error(f"Quality plan file save error: {exc}")
        return jsonify({"success": False, "error": "Could not save file to disk."}), 500

    file_path = saved["file_path"]
    ext = saved["original_name"].rsplit(".", 1)[-1].lower() if "." in saved["original_name"] else "unknown"

    # ── 4. Extract text from quality plan ────────────────────────────── #
    doc_result = process_document(file_path)
    if not doc_result["success"]:
        return jsonify({
            "success": False,
            "error": f"Could not read quality plan: {doc_result['error']}",
        }), 422

    plan_text = doc_result["text"]
    app_logger.info(
        f"Quality plan text extracted: {doc_result['word_count']} words, "
        f"{doc_result['page_count']} pages"
    )

    if doc_result["word_count"] < 10:
        return jsonify({
            "success": False,
            "error": "Quality plan document seems empty or too short to analyze.",
        }), 422

    # ── 4.5 Detect if document looks like an SRS instead of Quality Plan ─ #
    srs_warning = _detect_srs_document(plan_text)

    # ── 5. Get SRS analysis data for comparison ──────────────────────── #
    srs_category_scores = analysis.get("category_scores_json", {})
    srs_categories_present = analysis.get("categories_present", [])
    srs_categories_missing = analysis.get("categories_missing", [])
    srs_domain = analysis.get("domain_json", {})

    # Ensure they're lists/dicts (may come as JSON strings from DB)
    if isinstance(srs_categories_present, str):
        import json
        srs_categories_present = json.loads(srs_categories_present)
    if isinstance(srs_categories_missing, str):
        import json
        srs_categories_missing = json.loads(srs_categories_missing)
    if isinstance(srs_category_scores, str):
        import json
        srs_category_scores = json.loads(srs_category_scores)
    if isinstance(srs_domain, str):
        import json
        srs_domain = json.loads(srs_domain)

    # ── 6. Analyze the quality plan ──────────────────────────────────── #
    plan_result = analyze_quality_plan(
        plan_text=plan_text,
        srs_category_scores=srs_category_scores,
        srs_categories_present=srs_categories_present,
        srs_categories_missing=srs_categories_missing,
        srs_domain=srs_domain,
    )

    # ── 7. Save to database ──────────────────────────────────────────── #
    plan_id = f"qp_{analysis_id}"
    try:
        save_quality_plan({
            "id":                 plan_id,
            "analysis_id":        analysis_id,
            "filename":           saved["saved_name"],
            "original_name":      saved["original_name"],
            "file_path":          file_path,
            "file_type":          ext,
            "size_bytes":         saved.get("size_bytes", 0),
            "overall_coverage":   plan_result["overall_coverage"],
            "achievable_quality": plan_result["achievable_quality"],
            "category_coverage":  plan_result["category_coverage"],
            "suggestions":        plan_result["suggestions"],
            "status":             "analyzed",
        })
    except Exception as exc:
        app_logger.error(f"Quality plan DB save error: {exc}")
        return jsonify({"success": False, "error": "Failed to save quality plan analysis."}), 500

    elapsed = round(time.time() - start_time, 2)
    app_logger.info(
        f"Quality plan analysis complete: coverage={plan_result['overall_coverage']:.1f}%, "
        f"achievable={plan_result['achievable_quality']:.1f}%, time={elapsed}s"
    )

    return jsonify({
        "success":            True,
        "plan_id":            plan_id,
        "analysis_id":        analysis_id,
        "overall_coverage":   plan_result["overall_coverage"],
        "achievable_quality": plan_result["achievable_quality"],
        "plan_strength":      plan_result["plan_strength"],
        "category_coverage":  plan_result["category_coverage"],
        "suggestions":        plan_result["suggestions"],
        "summary":            plan_result["summary"],
        "domain_match":       plan_result.get("domain_match", {}),
        "srs_warning":        srs_warning if srs_warning.get("is_likely_srs") else None,
        "processing_time_s":  elapsed,
    }), 200


@quality_plan_bp.route("/quality-plan/<analysis_id>", methods=["GET"])
@handle_exception
def get_quality_plan_report(analysis_id):
    """Retrieve the quality plan analysis for a given SRS analysis."""
    plan = get_quality_plan_by_analysis(analysis_id)
    if not plan:
        return jsonify({
            "success": False,
            "error": "No quality plan analysis found for this SRS analysis.",
            "has_plan": False,
        }), 404

    return jsonify({
        "success":            True,
        "has_plan":           True,
        "plan_id":            plan["id"],
        "analysis_id":        analysis_id,
        "original_name":      plan.get("original_name"),
        "overall_coverage":   plan.get("overall_coverage", 0),
        "achievable_quality": plan.get("achievable_quality", 0),
        "category_coverage":  plan.get("category_coverage_json", {}),
        "suggestions":        plan.get("suggestions_json", []),
        "status":             plan.get("status"),
        "created_at":         plan.get("created_at"),
    }), 200
