"""
database/db.py
==============
SQLite connection management for QualityMapAI.

Provides:
- get_connection() – thread-safe SQLite connection with WAL mode
- init_db()        – create all tables if they don't already exist
- close_connection() – close a connection safely
"""

import os
import sqlite3
from contextlib import contextmanager
from typing import Generator

from utils.logger import app_logger

# Resolved at import time from config; avoids circular-import by reading env directly
_DB_PATH: str | None = None


def _get_db_path() -> str:
    """Resolve the database path from config (lazy import to avoid circular deps)."""
    global _DB_PATH
    if _DB_PATH is None:
        from config import Config
        _DB_PATH = Config.DATABASE_PATH
        os.makedirs(os.path.dirname(_DB_PATH), exist_ok=True)
    return _DB_PATH


def get_connection() -> sqlite3.Connection:
    """
    Open and return a SQLite connection.

    Settings applied:
    - WAL journal mode  → better concurrent read performance
    - row_factory       → rows accessible as dicts
    - foreign_keys ON   → enforce FK constraints
    - timeout 10 s      → queue write requests instead of failing immediately
    """
    db_path = _get_db_path()
    conn = sqlite3.connect(db_path, timeout=10, check_same_thread=False)
    conn.row_factory = sqlite3.Row          # Dict-like access: row["column"]
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


@contextmanager
def db_connection() -> Generator[sqlite3.Connection, None, None]:
    """
    Context manager for safe database access.

    Usage::

        with db_connection() as conn:
            conn.execute(...)

    Commits on success, rolls back on any exception.
    """
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception as exc:
        conn.rollback()
        app_logger.error(f"Database error – rolled back: {exc}")
        raise
    finally:
        conn.close()


def init_db() -> None:
    """
    Create all database tables and indices if they do not already exist.
    Safe to call on every application startup.
    """
    from database.models import (
        CREATE_UPLOADS_TABLE,
        CREATE_ANALYSES_TABLE,
        CREATE_REQUIREMENTS_TABLE,
        CREATE_INDICES,
    )

    with db_connection() as conn:
        conn.execute(CREATE_UPLOADS_TABLE)
        conn.execute(CREATE_ANALYSES_TABLE)
        conn.execute(CREATE_REQUIREMENTS_TABLE)
        for idx_sql in CREATE_INDICES:
            conn.execute(idx_sql)

    app_logger.info(f"Database initialised at: {_get_db_path()}")
