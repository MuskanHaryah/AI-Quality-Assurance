import logging
import os
import sys
from logging.handlers import RotatingFileHandler


def setup_logger(name: str, log_file: str = None, level: str = "DEBUG") -> logging.Logger:
    """
    Create and return a configured logger.

    Args:
        name:     Module name (use __name__ when calling).
        log_file: Absolute path to the log file. If None, logs to console only.
        level:    Logging level string (DEBUG, INFO, WARNING, ERROR).

    Returns:
        Configured Logger instance.
    """
    numeric_level = getattr(logging, level.upper(), logging.DEBUG)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    logger = logging.getLogger(name)
    logger.setLevel(numeric_level)

    # Avoid adding duplicate handlers if logger already exists
    if logger.handlers:
        return logger

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (rotating: max 5 MB, keep 3 backups)
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=3)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


# Shared application-level logger used across modules
def _init_app_logger() -> logging.Logger:
    """Initialise the application logger with the configured log file."""
    try:
        from config import Config
        return setup_logger("qualitymapai", log_file=Config.LOG_FILE, level=Config.LOG_LEVEL)
    except Exception:
        # Fallback: console-only logging if config is unavailable
        return setup_logger("qualitymapai")


app_logger = _init_app_logger()
