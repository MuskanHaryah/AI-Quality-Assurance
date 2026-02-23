"""
routes/upload.py
================
POST /api/upload  – Accept a PDF or DOCX file, save it to disk,
                    persist metadata to the database.

Request
-------
  multipart/form-data
  Body field: "file"  (PDF or DOCX, max 10 MB)

Response 200
------------
  {
    "success":       true,
    "file_id":       "20260223_152312_cf11b406",
    "filename":      "requirements.pdf",
    "file_type":     "pdf",
    "size_bytes":    204800,
    "size_mb":       0.20,
    "status":        "uploaded",
    "message":       "File uploaded successfully"
  }
"""

from flask import Blueprint, jsonify, request, current_app

from database.queries import save_upload
from utils.file_handler import save_uploaded_file
from utils.logger import app_logger
from utils.validators import validate_file_size, validate_file_type

upload_bp = Blueprint("upload", __name__)


@upload_bp.route("/upload", methods=["POST"])
def upload():
    # ── 1. Check a file was included ──────────────────────────────────── #
    if "file" not in request.files:
        return jsonify({"success": False, "error": "No file provided. Send field name 'file'."}), 400

    file = request.files["file"]

    if not file.filename:
        return jsonify({"success": False, "error": "File has no name."}), 400

    # ── 2. Validate file type ─────────────────────────────────────────── #
    if not validate_file_type(file.filename):
        return jsonify({
            "success": False,
            "error":   "Unsupported file type. Only PDF and DOCX are accepted.",
        }), 400

    # ── 3. Validate file size ─────────────────────────────────────────── #
    if not validate_file_size(file):
        return jsonify({
            "success": False,
            "error":   "File exceeds the 10 MB size limit.",
        }), 400

    # ── 4. Save to disk ───────────────────────────────────────────────── #
    try:
        upload_folder = current_app.config["UPLOAD_FOLDER"]
        saved = save_uploaded_file(file, upload_folder)
    except Exception as exc:
        app_logger.error(f"File save error: {exc}")
        return jsonify({"success": False, "error": "Could not save file to disk."}), 500

    # ── 5. Detect file type from extension ────────────────────────────── #
    ext = saved["original_name"].rsplit(".", 1)[-1].lower() if "." in saved["original_name"] else "unknown"

    # ── 6. Persist to database ────────────────────────────────────────── #
    try:
        save_upload({
            "id":            saved["file_id"],
            "filename":      saved["saved_name"],
            "original_name": saved["original_name"],
            "file_path":     saved["file_path"],
            "file_type":     ext,
            "size_bytes":    saved["size_bytes"],
            "status":        "uploaded",
        })
    except Exception as exc:
        app_logger.error(f"Database save error: {exc}")
        return jsonify({"success": False, "error": "Could not save file metadata."}), 500

    # ── 7. Return success response ────────────────────────────────────── #
    app_logger.info(f"Upload successful: {saved['file_id']} ({saved['original_name']})")
    return jsonify({
        "success":    True,
        "file_id":    saved["file_id"],
        "filename":   saved["original_name"],
        "file_type":  ext,
        "size_bytes": saved["size_bytes"],
        "size_mb":    round(saved["size_bytes"] / (1024 * 1024), 2),
        "status":     "uploaded",
        "message":    "File uploaded successfully. Use /api/analyze to process it.",
    }), 200
