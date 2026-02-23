import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Config:
    # Flask config
    DEBUG = True
    TESTING = False
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-prod")

    # File upload config
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB max file size
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    DATA_FOLDER = os.path.join(BASE_DIR, "data")

    # ML model paths (absolute so they work regardless of cwd)
    MODEL_PATH = os.path.join(BASE_DIR, "models", "classifier_model.pkl")
    VECTORIZER_PATH = os.path.join(BASE_DIR, "models", "tfidf_vectorizer.pkl")
    MODEL_INFO_PATH = os.path.join(BASE_DIR, "models", "model_info.json")

    # Database
    DATABASE_PATH = os.path.join(BASE_DIR, "data", "quality_assurance.db")

    # Allowed file types
    ALLOWED_EXTENSIONS = {"pdf", "docx"}

    # Logging
    LOG_LEVEL = "DEBUG"
    LOG_FILE = os.path.join(BASE_DIR, "data", "app.log")
