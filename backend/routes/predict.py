"""
routes/predict.py
=================
POST /api/predict  – Classify a single plain-text requirement on the fly.
                     No file upload needed; useful for quick checks.

Request (JSON)
--------------
  { "text": "The system shall encrypt all passwords." }
  OR a list:
  { "texts": ["req 1", "req 2"] }

Response 200
------------
  {
    "success":  true,
    "results":  [ { text, category, confidence, probabilities }, … ]
  }
"""

from flask import Blueprint, jsonify, request

from services.classifier import classifier
from utils.error_handler import handle_exception
from utils.logger import app_logger

predict_bp = Blueprint("predict", __name__)


@predict_bp.route("/predict", methods=["POST"])
@handle_exception
def predict():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"success": False, "error": "Request body must be JSON."}), 400

    # Accept either a single text or a list of texts
    if "texts" in data:
        texts = data["texts"]
        if not isinstance(texts, list) or not texts:
            return jsonify({"success": False, "error": "'texts' must be a non-empty list."}), 400
    elif "text" in data:
        texts = [data["text"]]
    else:
        return jsonify({"success": False, "error": "Provide 'text' (string) or 'texts' (list)."}), 400

    # Validate individual items
    for item in texts:
        if not isinstance(item, str) or not item.strip():
            return jsonify({"success": False, "error": "Each text entry must be a non-empty string."}), 400

    try:
        results = classifier.classify_batch(texts)
        app_logger.info(f"/predict: classified {len(results)} requirement(s)")
        return jsonify({"success": True, "results": results, "count": len(results)}), 200
    except Exception as exc:
        app_logger.error(f"/predict error: {exc}")
        return jsonify({"success": False, "error": "Classification failed."}), 500
