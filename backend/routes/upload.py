from flask import Blueprint, jsonify

upload_bp = Blueprint("upload", __name__)


@upload_bp.route("/upload", methods=["POST"])
def upload():
    # TODO: Phase 1.8 - Implement full upload logic
    return jsonify({"message": "Upload endpoint - coming in Phase 1.8"}), 501
