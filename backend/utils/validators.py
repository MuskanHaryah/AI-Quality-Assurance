import os
import re
import unicodedata


def _get_allowed_extensions() -> set:
    try:
        from config import Config
        return Config.ALLOWED_EXTENSIONS
    except Exception:
        return {"pdf", "docx"}


def _get_max_file_size() -> int:
    try:
        from config import Config
        return Config.MAX_CONTENT_LENGTH
    except Exception:
        return 10 * 1024 * 1024


ALLOWED_EXTENSIONS = _get_allowed_extensions()
MAX_FILE_SIZE_BYTES = _get_max_file_size()
MAX_FILE_SIZE_MB = MAX_FILE_SIZE_BYTES / (1024 * 1024)


def validate_file_type(filename: str) -> bool:
    """
    Return True if the filename has a supported extension (pdf or docx).

    Args:
        filename: Original filename from the upload.

    Returns:
        True if allowed, False otherwise.
    """
    if not filename or "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS


def validate_file_size(file) -> bool:
    """
    Check that the file size does not exceed MAX_FILE_SIZE_BYTES.

    The file pointer is reset to position 0 after checking.

    Args:
        file: Werkzeug FileStorage object.

    Returns:
        True if within limit, False otherwise.
    """
    file.seek(0, 2)  # Seek to end
    size = file.tell()
    file.seek(0)     # Reset to start
    return size <= MAX_FILE_SIZE_BYTES


def sanitize_filename(filename: str) -> str:
    """
    Remove or replace characters that are unsafe in filenames.

    - Normalise unicode to ASCII
    - Keep only alphanumerics, dots, hyphens, underscores
    - Collapse consecutive dots/spaces
    - Truncate to 255 chars

    Args:
        filename: Raw filename string.

    Returns:
        Sanitized filename safe to write to disk.
    """
    # Normalize unicode characters
    filename = unicodedata.normalize("NFKD", filename)
    filename = filename.encode("ascii", "ignore").decode("ascii")

    # Keep only safe characters
    filename = re.sub(r"[^\w.\-]", "_", filename)

    # Collapse multiple consecutive dots/underscores/hyphens
    filename = re.sub(r"\.{2,}", ".", filename)
    filename = re.sub(r"_{2,}", "_", filename)

    # Strip leading/trailing dots and underscores
    filename = filename.strip("._")

    # Ensure the extension is preserved after sanitization
    if not filename:
        filename = "uploaded_file"

    return filename[:255]


def get_extension(filename: str) -> str:
    """Return the lowercase file extension without the leading dot."""
    if "." not in filename:
        return ""
    return filename.rsplit(".", 1)[1].lower()
