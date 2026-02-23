import os
import uuid
from datetime import datetime

from utils.logger import app_logger
from utils.validators import sanitize_filename


def ensure_directories(*paths: str) -> None:
    """Create one or more directories (including parents) if they do not exist."""
    for path in paths:
        os.makedirs(path, exist_ok=True)
        app_logger.debug(f"Directory ready: {path}")


def save_uploaded_file(file, upload_folder: str) -> dict:
    """
    Save a Werkzeug FileStorage object to disk.

    The file is stored under a unique ID to avoid collisions.

    Args:
        file:          Werkzeug FileStorage object from the request.
        upload_folder: Absolute path to the uploads directory.

    Returns:
        Dict with keys: file_id, original_name, saved_name, file_path, size_bytes.
    """
    ensure_directories(upload_folder)

    original_name = sanitize_filename(file.filename)
    file_id = create_analysis_id()

    # Preserve the original extension
    ext = original_name.rsplit(".", 1)[-1] if "." in original_name else "bin"
    saved_name = f"{file_id}.{ext}"
    file_path = os.path.join(upload_folder, saved_name)

    file.save(file_path)
    size_bytes = os.path.getsize(file_path)

    app_logger.info(f"File saved → {file_path} ({size_bytes} bytes)")

    return {
        "file_id": file_id,
        "original_name": original_name,
        "saved_name": saved_name,
        "file_path": file_path,
        "size_bytes": size_bytes,
    }


def delete_temp_file(file_path: str) -> bool:
    """
    Delete a file from disk.

    Args:
        file_path: Absolute path to the file.

    Returns:
        True if deleted, False if the file did not exist.
    """
    if os.path.exists(file_path):
        os.remove(file_path)
        app_logger.info(f"Temp file deleted: {file_path}")
        return True
    app_logger.warning(f"File not found for deletion: {file_path}")
    return False


def create_analysis_id() -> str:
    """
    Generate a unique analysis / upload ID.

    Format: YYYYMMDD_HHMMSS_<8-char-uuid>
    Example: 20260223_143012_a1b2c3d4

    Returns:
        Unique string ID.
    """
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    short_uuid = uuid.uuid4().hex[:8]
    return f"{timestamp}_{short_uuid}"
