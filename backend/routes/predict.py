from flask import Blueprint, jsonify

predict_bp = Blueprint("predict", __name__)


@predict_bp.route("/predict", methods=["POST"])
def predict():
    # TODO: Phase 1.8 - Implement direct text prediction
    return jsonify({"message": "Predict endpoint - coming in Phase 1.8"}), 501
