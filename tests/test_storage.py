from vectors.storage.app import app, db
from vectors.storage.routes import auth_bp, main_bp


def test_storage_app_initialised():
    assert app.name == "vectors.storage.app"
    assert db is not None


def test_blueprints_named_correctly():
    assert auth_bp.name == "auth"
    assert main_bp.name == "main"
