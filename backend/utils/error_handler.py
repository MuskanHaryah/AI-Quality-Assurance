"""
utils/error_handler.py
=======================
Centralised error utilities for QualityMapAI.

Provides
--------
- Custom exception classes (AppError, ValidationError, NotFoundError)
- error_response()   – build a standard JSON error dict
- register_handlers() – wire Flask error handlers into the app
- handle_exception()  – catch-all wrapper for route functions
"""

import traceback
from functools import wraps
from typing import Any, Dict, Optional, Tuple

from flask import Flask, jsonify

from utils.logger import app_logger


# ──────────────────────────────────────────────────────────────────────────── #
# Custom exception classes                                                      #
# ──────────────────────────────────────────────────────────────────────────── #

class AppError(Exception):
    """Base application exception."""
    def __init__(self, message: str, status_code: int = 500, details: Any = None):
        super().__init__(message)
        self.message     = message
        self.status_code = status_code
        self.details     = details


class ValidationError(AppError):
    """Raised when incoming request data fails validation (HTTP 400)."""
    def __init__(self, message: str, details: Any = None):
        super().__init__(message, status_code=400, details=details)


class NotFoundError(AppError):
    """Raised when a requested resource does not exist (HTTP 404)."""
    def __init__(self, message: str):
        super().__init__(message, status_code=404)


class ProcessingError(AppError):
    """Raised when document or ML processing fails (HTTP 422)."""
    def __init__(self, message: str, details: Any = None):
        super().__init__(message, status_code=422, details=details)


# ──────────────────────────────────────────────────────────────────────────── #
# Helpers                                                                       #
# ──────────────────────────────────────────────────────────────────────────── #

def error_response(
    message: str,
    status_code: int = 500,
    details: Any = None,
) -> Tuple[Any, int]:
    """
    Build a consistent error JSON response tuple.

    Usage in a route::

        return error_response("File not found", 404)

    Returns:
        (flask.Response, status_code)
    """
    body: Dict[str, Any] = {"success": False, "error": message}
    if details is not None:
        body["details"] = details
    return jsonify(body), status_code


def success_response(data: Dict[str, Any], status_code: int = 200) -> Tuple[Any, int]:
    """Build a consistent success JSON response tuple."""
    return jsonify({"success": True, **data}), status_code


# ──────────────────────────────────────────────────────────────────────────── #
# Route decorator                                                               #
# ──────────────────────────────────────────────────────────────────────────── #

def handle_exception(func):
    """
    Decorator that wraps a route function in a try/except block.

    Catches:
    - AppError subclasses  → returns their status_code + message
    - Any other Exception  → logs the traceback, returns 500

    Usage::

        @analyze_bp.route("/analyze", methods=["POST"])
        @handle_exception
        def analyze():
            ...
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except AppError as exc:
            app_logger.warning(f"AppError [{exc.status_code}]: {exc.message}")
            return error_response(exc.message, exc.status_code, exc.details)
        except Exception as exc:
            app_logger.error(
                f"Unhandled exception in {func.__name__}: {exc}\n"
                + traceback.format_exc()
            )
            return error_response("An unexpected server error occurred.", 500)
    return wrapper


# ──────────────────────────────────────────────────────────────────────────── #
# Flask-level error handlers                                                    #
# ──────────────────────────────────────────────────────────────────────────── #

def register_handlers(app: Flask) -> None:
    """
    Register HTTP-level error handlers on the Flask app instance.
    Call once inside create_app().
    """

    @app.errorhandler(AppError)
    def handle_app_error(exc: AppError):
        return error_response(exc.message, exc.status_code, exc.details)

    @app.errorhandler(400)
    def bad_request(e):
        return error_response("Bad request. Check your input.", 400)

    @app.errorhandler(404)
    def not_found(e):
        return error_response("Endpoint not found.", 404)

    @app.errorhandler(405)
    def method_not_allowed(e):
        return error_response("HTTP method not allowed for this endpoint.", 405)

    @app.errorhandler(413)
    def request_entity_too_large(e):
        return error_response("File too large. Maximum allowed size is 10 MB.", 413)

    @app.errorhandler(422)
    def unprocessable(e):
        return error_response("Could not process the provided data.", 422)

    @app.errorhandler(500)
    def internal_error(e):
        app_logger.error(f"HTTP 500: {e}")
        return error_response("Internal server error.", 500)

    app_logger.debug("Flask error handlers registered.")
