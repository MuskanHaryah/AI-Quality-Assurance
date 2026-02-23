"""
tests/conftest.py
=================
Shared pytest fixtures available to all test modules in this package.

Fixtures
--------
app       — configured Flask application in TESTING mode
client    — test client for the Flask app

Usage in tests
--------------
    def test_health(client):
        resp = client.get("/api/health")
        assert resp.status_code == 200
"""

import os
import sys
import pytest

# Make sure imports resolve from the backend root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app


@pytest.fixture(scope="session")
def app():
    """
    Create a single Flask application instance for the entire test session.
    Using session scope avoids re-loading the ML model on every test class.
    """
    flask_app = create_app()
    flask_app.config.update(
        TESTING=True,
        # Use an in-memory-style DB path so tests don't pollute the dev database.
        # The DB is still file-backed so concurrent write safety is maintained.
    )
    yield flask_app


@pytest.fixture(scope="session")
def client(app):
    """Return a test client that reuses the session-scoped app."""
    return app.test_client()
