"""Smoke tests for the Airtable scope adapter."""

import importlib.util
from pathlib import Path

import pytest


def _load_scope_mapper():
    path = Path(__file__).resolve().parents[1] / "adapters" / "airtable" / "scope_mapper.py"
    spec = importlib.util.spec_from_file_location("scope_mapper", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_adapter_initializes_with_base_id():
    scope_mapper = _load_scope_mapper()
    adapter = scope_mapper.AirtableScopeAdapter()
    assert adapter.base_id
    assert adapter.scope_rules_table == "Scope Rules"


def test_default_scope_is_empty():
    scope_mapper = _load_scope_mapper()
    adapter = scope_mapper.AirtableScopeAdapter()
    assert adapter.get_active_scope() == []


@pytest.mark.parametrize(
    "asset_id",
    [
        "any-asset",
        "",
        "12345",
        "!@#$%^&*()",
        "example.com",
        "192.168.1.1",
        "*.wildcard.io",
        "资产-001",
        "a" * 256,
    ],
)
def test_default_authorization_denies(asset_id):
    """Stub adapter must default-deny for any asset id shape."""
    scope_mapper = _load_scope_mapper()
    adapter = scope_mapper.AirtableScopeAdapter()
    result = adapter.is_authorized(asset_id)
    assert result is False
    assert isinstance(result, bool)
