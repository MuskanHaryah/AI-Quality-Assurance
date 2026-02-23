import os

from flask import Flask, jsonify
from flask_cors import CORS

from config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Enable CORS for all routes (allows React frontend on port 3000)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Ensure required folders exist
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["DATA_FOLDER"], exist_ok=True)

    # Initialise the SQLite database (creates tables if they don't exist)
    from database.db import init_db
    init_db()

    # Register blueprints
    from routes.upload import upload_bp
    from routes.analyze import analyze_bp
    from routes.predict import predict_bp
    from routes.report import report_bp

    app.register_blueprint(upload_bp, url_prefix="/api")
    app.register_blueprint(analyze_bp, url_prefix="/api")
    app.register_blueprint(predict_bp, url_prefix="/api")
    app.register_blueprint(report_bp, url_prefix="/api")

    # Wire centralised HTTP-level error handlers
    from utils.error_handler import register_handlers
    register_handlers(app)

    # ------------------------------------------------------------------ #
    # Health check                                                          #
    # ------------------------------------------------------------------ #
    @app.route("/api/health", methods=["GET"])
    def health():
        from services.classifier import classifier
        model_info = classifier.get_model_info()
        return jsonify({
            "status":  "ok",
            "message": "QualityMapAI backend running",
            "model":   model_info["model_name"],
            "accuracy": model_info["accuracy"],
        })

    # ------------------------------------------------------------------ #
    # Dashboard: recent analyses list                                       #
    # ------------------------------------------------------------------ #
    @app.route("/api/analyses", methods=["GET"])
    def list_analyses():
        from database.queries import get_recent_analyses
        rows = get_recent_analyses(limit=20)
        # Only send the summary columns (not full JSON blobs)
        summaries = [
            {
                "analysis_id":       r["id"],
                "filename":          r.get("original_name") or r.get("filename"),
                "file_type":         r.get("file_type"),
                "overall_score":     r.get("overall_score", 0),
                "risk_level":        r.get("risk_level", "Unknown"),
                "total_requirements": r.get("total_requirements", 0),
                "created_at":        r.get("created_at"),
            }
            for r in rows
        ]
        return jsonify({"success": True, "analyses": summaries, "count": len(summaries)})

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
