"""
routes/analyze.py
=================
POST /api/analyze  – Run the complete analysis pipeline on an uploaded file.

Pipeline
--------
  1. Validate request (file_id required)
  2. Load file path from database
  3. Extract text (PDF / DOCX)
  4. Extract requirement candidates from text
  5. Classify each requirement with the ML model
  6. Calculate quality scores
  7. Save analysis + requirements to database
  8. Return full structured JSON

Request (JSON)
--------------
  { "file_id": "20260223_152312_cf11b406" }

Response 200
------------
  {
    "success":            true,
    "analysis_id":        "...",
    "total_requirements": 12,
    "overall_score":      74.3,
    "risk":               { "level": "Medium", "colour": "orange" },
    "category_scores":    { ... },
    "requirements":       [ { text, category, confidence }, ... ],
    "recommendations":    [ ... ],
    "gap_analysis":       [ ... ],
    "categories_present": [...],
    "categories_missing": [...],
    "processing_time_s":  2.41
  }
"""

import time

from flask import Blueprint, jsonify, request

from database.queries import (
    get_upload,
    save_full_analysis,
    update_upload_status,
)
from services.classifier import classifier
from services.document_processor import process_document
from services.quality_scorer import build_full_report
from services.requirement_extractor import extract_requirements
from utils.error_handler import handle_exception
from utils.logger import app_logger

analyze_bp = Blueprint("analyze", __name__)


@analyze_bp.route("/analyze", methods=["POST"])
@handle_exception
def analyze():
    start_time = time.time()

    # ── 1. Validate request ───────────────────────────────────────────────── #
    data = request.get_json(silent=True)
    if not data or "file_id" not in data:
        return jsonify({"success": False, "error": "JSON body with 'file_id' is required."}), 400

    file_id = data["file_id"].strip()
    if not file_id:
        return jsonify({"success": False, "error": "'file_id' cannot be empty."}), 400

    # ── 2. Load file metadata from database ───────────────────────────────── #
    upload = get_upload(file_id)
    if not upload:
        return jsonify({"success": False, "error": f"No file found for file_id: {file_id}"}), 404

    file_path = upload["file_path"]
    app_logger.info(f"Starting analysis for file_id={file_id} path={file_path}")
    update_upload_status(file_id, "processing")

    # ── 3. Extract text from document ─────────────────────────────────────── #
    doc_result = process_document(file_path)
    if not doc_result["success"]:
        update_upload_status(file_id, "error")
        return jsonify({
            "success": False,
            "error":   f"Text extraction failed: {doc_result['error']}",
        }), 422

    raw_text = doc_result["text"]
    app_logger.info(
        f"Text extracted: {doc_result['word_count']} words, {doc_result['page_count']} pages"
    )

    # ── 4. Extract requirement candidates ─────────────────────────────────── #
    extraction = extract_requirements(raw_text)
    if extraction["total_found"] == 0:
        update_upload_status(file_id, "error")
        return jsonify({
            "success": False,
            "error":   (
                "No requirement statements found in this document. "
                "This does not appear to be an SRS (Software Requirements Specification). "
                "Please upload a document that contains requirement sentences "
                "with keywords like 'shall', 'must', 'should', 'requires', etc."
            ),
        }), 422

    # Warn if very few requirements found (likely not a proper SRS)
    if extraction["total_found"] < 3:
        update_upload_status(file_id, "error")
        return jsonify({
            "success": False,
            "error":   (
                f"Only {extraction['total_found']} requirement(s) found. "
                "This document does not contain enough requirement statements "
                "to produce a meaningful analysis. A proper SRS typically has "
                "at least 5-10 requirement statements. Please upload an SRS document."
            ),
        }), 422

    candidates = extraction["requirements"]       # list of {text, source_index, …}
    req_texts  = [r["text"] for r in candidates]

    # ── 5. Classify with ML model ─────────────────────────────────────────── #
    classified = classifier.classify_batch(req_texts)

    # Merge extractor metadata (keyword_strength, source_index) into classifier output
    for i, cls_result in enumerate(classified):
        ext_data = candidates[i] if i < len(candidates) else {}
        cls_result["keyword_strength"] = ext_data.get("keyword_strength")
        cls_result["source_index"]     = ext_data.get("source_index")

    # ── 6. Calculate quality scores ───────────────────────────────────────── #
    report = build_full_report(classified, raw_text=raw_text)

    # ── 7. Persist to database (single atomic transaction) ───────────────── #
    try:
        save_full_analysis(
            analysis={
                "id":                  file_id,
                "upload_id":           file_id,
                "total_requirements":  report["total_requirements"],
                "overall_score":       0.0,            # score comes from Quality Plan, not SRS
                "risk_level":          "N/A",
                "categories_present":  report["categories_present"],
                "categories_missing":  report["categories_missing"],
                "category_scores":     report["category_scores"],
                "recommendations":     report["recommendations"],
                "gap_analysis":        report["gap_analysis"],
                "domain":              report["domain"],
            },
            requirements=classified,
            upload_status="completed",
        )
    except Exception as exc:
        app_logger.error(f"Database persist error: {exc}")
        update_upload_status(file_id, "error")
        return jsonify({"success": False, "error": "Failed to save analysis results."}), 500

    elapsed = round(time.time() - start_time, 2)
    app_logger.info(
        f"Analysis complete: {report['total_requirements']} reqs, "
        f"domain={report['domain']['domain']}, time={elapsed}s"
    )

    # ── 8. Build and return response ──────────────────────────────────────── #
    requirements_list = [
        {
            "text":             r["text"],
            "category":         r["category"],
            "confidence":       round(r["confidence"], 2),
            "keyword_strength": r.get("keyword_strength"),
        }
        for r in classified
    ]

    return jsonify({
        "success":            True,
        "analysis_id":        file_id,
        "total_requirements": report["total_requirements"],
        "domain":             report["domain"],
        "category_scores":    report["category_scores"],
        "requirements":       requirements_list,
        "recommendations":    report["recommendations"],
        "gap_analysis":       report["gap_analysis"],
        "categories_present": report["categories_present"],
        "categories_missing": report["categories_missing"],
        "document_info": {
            "word_count":  doc_result["word_count"],
            "page_count":  doc_result["page_count"],
            "file_type":   doc_result["file_type"],
        },
        "extraction_stats":   extraction["extraction_stats"],
        "processing_time_s":  elapsed,
    }), 200
