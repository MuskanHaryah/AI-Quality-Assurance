from flask import Blueprint, jsonify

report_bp = Blueprint("report", __name__)


@report_bp.route("/report/<analysis_id>", methods=["GET"])
def get_report(analysis_id):
    # TODO: Phase 1.8 - Implement report retrieval
    return jsonify({"message": "Report endpoint - coming in Phase 1.8"}), 501
