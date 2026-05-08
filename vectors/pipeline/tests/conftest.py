import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import create_app  # noqa: E402


@pytest.fixture
def client():
    app = create_app(config={
        "TESTING": True,
        "ANTHROPIC_API_KEY": "",
        "MISTRAL_API_KEY": "",
    })
    with app.test_client() as c:
        yield c
