"""
database/models.py
==================
SQL CREATE TABLE statements for QualityMapAI.

Tables
------
uploads       – tracks every uploaded file
analyses      – stores one analysis result per upload
requirements  – stores individual classified requirements
"""

# ── uploads ──────────────────────────────────────────────────────────────── #
CREATE_UPLOADS_TABLE: str = """
CREATE TABLE IF NOT EXISTS uploads (
    id           TEXT PRIMARY KEY,          -- unique file ID (e.g. 20260223_143012_a1b2c3d4)
    filename     TEXT    NOT NULL,          -- sanitised original filename
    original_name TEXT   NOT NULL,          -- filename as provided by the user
    file_path    TEXT    NOT NULL,          -- absolute path on disk
    file_type    TEXT    NOT NULL,          -- 'pdf' | 'docx'
    size_bytes   INTEGER NOT NULL,          -- file size in bytes
    status       TEXT    NOT NULL           -- 'uploaded' | 'processing' | 'completed' | 'error'
                 DEFAULT 'uploaded',
    uploaded_at  TIMESTAMP NOT NULL
                 DEFAULT (datetime('now'))
);
"""

# ── analyses ─────────────────────────────────────────────────────────────── #
CREATE_ANALYSES_TABLE: str = """
CREATE TABLE IF NOT EXISTS analyses (
    id                   TEXT PRIMARY KEY,  -- same as upload id for simplicity
    upload_id            TEXT NOT NULL,
    total_requirements   INTEGER NOT NULL DEFAULT 0,
    overall_score        REAL    NOT NULL DEFAULT 0.0,
    risk_level           TEXT    NOT NULL DEFAULT 'Unknown',
    categories_present   TEXT,              -- JSON array: ["Functionality", ...]
    categories_missing   TEXT,              -- JSON array
    category_scores_json TEXT,              -- JSON blob of per-category detail
    recommendations_json TEXT,              -- JSON array of recommendation dicts
    gap_analysis_json    TEXT,              -- JSON array of gap dicts
    created_at           TIMESTAMP NOT NULL
                         DEFAULT (datetime('now')),
    FOREIGN KEY (upload_id) REFERENCES uploads(id) ON DELETE CASCADE
);
"""

# ── requirements ─────────────────────────────────────────────────────────── #
CREATE_REQUIREMENTS_TABLE: str = """
CREATE TABLE IF NOT EXISTS requirements (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_id      TEXT    NOT NULL,
    requirement_text TEXT    NOT NULL,
    category         TEXT    NOT NULL,
    confidence       REAL    NOT NULL DEFAULT 0.0,
    keyword_strength TEXT,               -- 'strong' | 'weak'
    source_index     INTEGER,            -- position in original document
    FOREIGN KEY (analysis_id) REFERENCES analyses(id) ON DELETE CASCADE
);
"""
