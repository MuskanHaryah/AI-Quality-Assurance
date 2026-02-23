from flask import Flask, jsonify
from flask_cors import CORS

from config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Enable CORS for all routes (allows React frontend on port 3000)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Ensure required folders exist
    import os
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["DATA_FOLDER"], exist_ok=True)

    # Register blueprints
    from routes.upload import upload_bp
    from routes.analyze import analyze_bp
    from routes.predict import predict_bp
    from routes.report import report_bp

    app.register_blueprint(upload_bp, url_prefix="/api")
    app.register_blueprint(analyze_bp, url_prefix="/api")
    app.register_blueprint(predict_bp, url_prefix="/api")
    app.register_blueprint(report_bp, url_prefix="/api")

    # ------------------------------------------------------------------ #
    # Health check                                                          #
    # ------------------------------------------------------------------ #
    @app.route("/api/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok", "message": "QualityMapAI backend running"})

    # ------------------------------------------------------------------ #
    # Error handlers                                                        #
    # ------------------------------------------------------------------ #
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Endpoint not found"}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"error": "Method not allowed"}), 405

    @app.errorhandler(413)
    def file_too_large(e):
        return jsonify({"error": "File too large. Maximum size is 10 MB"}), 413

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"error": "Internal server error"}), 500

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
