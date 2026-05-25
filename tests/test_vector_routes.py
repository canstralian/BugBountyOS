"""
tests/test_vector_routes.py — Tests for changed vector route modules.

Covers:
  - vectors/pipeline/routes.py  (health endpoint: quote style changed to double)
  - vectors/storage/routes.py   (Blueprints: quote style changed to double)
  - vectors/pipeline/app.py     (Flask app instantiation)
  - vectors/storage/app.py      (Flask app + SQLAlchemy instantiation)
"""

import json
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

REPO_ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

flask = pytest.importorskip("flask", reason="Flask not installed; skipping route tests")


# ---------------------------------------------------------------------------
# vectors/storage/routes.py — Blueprint definitions
# ---------------------------------------------------------------------------


class TestStorageBlueprints:
    """Tests for vectors/storage/routes.py (changed: single -> double quotes on Blueprint names)."""

    @pytest.fixture(autouse=True)
    def _import_storage_routes(self):
        """Import storage routes with correct sys.path."""
        vectors_storage = str(REPO_ROOT / "vectors" / "storage")
        if vectors_storage not in sys.path:
            sys.path.insert(0, vectors_storage)
        # Clear stale module cache to get a fresh import
        for mod in ("routes", "app"):
            sys.modules.pop(mod, None)
        import app as storage_app  # noqa: F401
        import routes as storage_routes

        self.routes = storage_routes

    def test_auth_blueprint_exists(self):
        assert hasattr(self.routes, "auth_bp")

    def test_main_blueprint_exists(self):
        assert hasattr(self.routes, "main_bp")

    def test_auth_blueprint_name_is_auth(self):
        assert self.routes.auth_bp.name == "auth"

    def test_main_blueprint_name_is_main(self):
        assert self.routes.main_bp.name == "main"

    def test_auth_bp_is_blueprint_instance(self):
        from flask import Blueprint

        assert isinstance(self.routes.auth_bp, Blueprint)

    def test_main_bp_is_blueprint_instance(self):
        from flask import Blueprint

        assert isinstance(self.routes.main_bp, Blueprint)

    def test_blueprints_are_distinct_objects(self):
        assert self.routes.auth_bp is not self.routes.main_bp


# ---------------------------------------------------------------------------
# vectors/pipeline/app.py — Flask app instantiation
# ---------------------------------------------------------------------------


class TestPipelineApp:
    """Tests for vectors/pipeline/app.py (added blank line/EOF newline in PR)."""

    @pytest.fixture(autouse=True)
    def _import_pipeline_app(self):
        vectors_pipeline = str(REPO_ROOT / "vectors" / "pipeline")
        if vectors_pipeline not in sys.path:
            sys.path.insert(0, vectors_pipeline)
        if "app" in sys.modules:
            del sys.modules["app"]
        import app as pipeline_app

        self.app_module = pipeline_app

    def test_app_attribute_exists(self):
        assert hasattr(self.app_module, "app")

    def test_app_is_flask_instance(self):
        from flask import Flask

        assert isinstance(self.app_module.app, Flask)

    def test_app_name_is_set(self):
        assert self.app_module.app.name is not None


# ---------------------------------------------------------------------------
# vectors/pipeline/routes.py — Health endpoint
# ---------------------------------------------------------------------------


class TestPipelineRoutes:
    """Tests for vectors/pipeline/routes.py (changed: single -> double quotes, added blanks)."""

    @pytest.fixture(autouse=True)
    def _setup(self):
        vectors_pipeline = str(REPO_ROOT / "vectors" / "pipeline")
        if vectors_pipeline not in sys.path:
            sys.path.insert(0, vectors_pipeline)
        for mod in ("app", "routes"):
            if mod in sys.modules:
                del sys.modules[mod]
        import app as pipeline_app
        import routes  # noqa: F401

        self.client = pipeline_app.app.test_client()
        self.app_ctx = pipeline_app.app.app_context()
        self.app_ctx.push()
        yield
        self.app_ctx.pop()

    def test_health_endpoint_returns_200(self):
        response = self.client.get("/api/health")
        assert response.status_code == 200

    def test_health_endpoint_returns_json(self):
        response = self.client.get("/api/health")
        assert response.content_type.startswith("application/json")

    def test_health_endpoint_status_ok(self):
        response = self.client.get("/api/health")
        data = json.loads(response.data)
        assert data["status"] == "ok"

    def test_health_endpoint_uses_double_quote_key(self):
        """Regression: after PR, response key is 'status' (double-quote style in source)."""
        response = self.client.get("/api/health")
        data = json.loads(response.data)
        assert "status" in data

    def test_health_endpoint_route_is_api_health(self):
        """Route path should be /api/health (double-quoted in source after PR)."""
        rules = [rule.rule for rule in self.client.application.url_map.iter_rules()]
        assert "/api/health" in rules

    def test_health_endpoint_not_found_for_wrong_path(self):
        response = self.client.get("/health")
        assert response.status_code == 404


# ---------------------------------------------------------------------------
# vectors/storage/app.py — Flask + SQLAlchemy instantiation
# ---------------------------------------------------------------------------


class TestStorageApp:
    """Tests for vectors/storage/app.py (added blank line in PR)."""

    @pytest.fixture(autouse=True)
    def _import_storage_app(self):
        vectors_storage = str(REPO_ROOT / "vectors" / "storage")
        if vectors_storage not in sys.path:
            sys.path.insert(0, vectors_storage)
        if "app" in sys.modules:
            del sys.modules["app"]
        pytest.importorskip("flask_sqlalchemy", reason="flask_sqlalchemy not installed")
        import app as storage_app

        self.app_module = storage_app

    def test_app_attribute_exists(self):
        assert hasattr(self.app_module, "app")

    def test_db_attribute_exists(self):
        assert hasattr(self.app_module, "db")

    def test_app_is_flask_instance(self):
        from flask import Flask

        assert isinstance(self.app_module.app, Flask)

    def test_db_is_sqlalchemy_instance(self):
        from flask_sqlalchemy import SQLAlchemy

        assert isinstance(self.app_module.db, SQLAlchemy)
