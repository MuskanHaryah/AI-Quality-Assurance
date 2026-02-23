"""
routes/report.py
================
GET /api/report/<analysis_id>  – Return a complete analysis report as JSON.

Response 200
------------
  {
    "success":             true,
    "analysis_id":         "...",
    "summary":             { overall_score, risk, total_requirements, … },
    "category_scores":     { Functionality: {…}, … },
    "requirements":        [ {id, text, category, confidence, …}, … ],
    "recommendations":     [ {category, priority, message}, … ],
    "gap_analysis":        [ {category, gap_type, shortage}, … ],
    "categories_present":  […],
    "categories_missing":  […]
  }
"""

from flask import Blueprint, jsonify

from database.queries import get_analysis, get_requirements, get_upload
from utils.logger import app_logger

report_bp = Blueprint("report", __name__)


@report_bp.route("/report/<analysis_id>", methods=["GET"])
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
            "overall_score":       analysis.get("overall_score", 0),
            "risk":                {"level": analysis.get("risk_level", "Unknown")},
            "total_requirements":  analysis.get("total_requirements", 0),
            "categories_present":  analysis.get("categories_present", []),
            "categories_missing":  analysis.get("categories_missing", []),
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
