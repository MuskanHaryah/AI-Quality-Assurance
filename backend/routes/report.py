"""
routes/report.py
================
GET /api/report/<analysis_id>  – Return an SRS analysis summary as JSON.

The report shows which ISO/IEC 9126 categories are present/missing,
the detected domain, and domain-aware recommendations.
It does NOT include a quality score — quality estimation is done
via the Quality Plan comparison feature.
"""

from flask import Blueprint, jsonify

from database.queries import get_analysis, get_requirements, get_upload
from utils.error_handler import handle_exception
from utils.logger import app_logger

report_bp = Blueprint("report", __name__)


@report_bp.route("/report/<analysis_id>", methods=["GET"])
@handle_exception
def get_report(analysis_id):
    if not analysis_id or not analysis_id.strip():
        return jsonify({"success": False, "error": "analysis_id is required."}), 400

    # ── Fetch analysis from DB ─────────────────────────────────────────── #
    analysis = get_analysis(analysis_id)
    if not analysis:
        return jsonify({"success": False, "error": f"No analysis found for id: {analysis_id}"}), 404

    # ── Fetch requirements from DB ────────────────────────────────────── #
    requirements = get_requirements(analysis_id)

    # ── Fetch upload metadata ─────────────────────────────────────────── #
    upload = get_upload(analysis["upload_id"])

    # ── Build normalised requirement list ─────────────────────────────── #
    req_list = [
        {
            "id":         r["id"],
            "text":       r["requirement_text"],
            "category":   r["category"],
            "confidence": round(r["confidence"], 2),
            "keyword_strength": r.get("keyword_strength"),
        }
        for r in requirements
    ]

    app_logger.info(f"Report served: analysis_id={analysis_id}")

    return jsonify({
        "success":            True,
        "analysis_id":        analysis_id,
        "summary": {
            "total_requirements":  analysis.get("total_requirements", 0),
            "categories_present":  analysis.get("categories_present", []),
            "categories_missing":  analysis.get("categories_missing", []),
            "domain":              analysis.get("domain_json", {}),
            "created_at":          analysis.get("created_at"),
            "filename":            upload["original_name"] if upload else None,
            "file_type":           upload["file_type"] if upload else None,
        },
        "category_scores":     analysis.get("category_scores_json", {}),
        "requirements":        req_list,
        "recommendations":     analysis.get("recommendations_json", []),
        "gap_analysis":        analysis.get("gap_analysis_json", []),
        "categories_present":  analysis.get("categories_present", []),
        "categories_missing":  analysis.get("categories_missing", []),
    }), 200
