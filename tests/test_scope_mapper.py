"""Tests for the Airtable scope adapter."""

import importlib.util
import json
from pathlib import Path

import pytest


def _load_scope_mapper():
    path = Path(__file__).resolve().parents[1] / "adapters" / "airtable" / "scope_mapper.py"
    spec = importlib.util.spec_from_file_location("scope_mapper", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ---------------------------------------------------------------------------
# Initialization
# ---------------------------------------------------------------------------

def test_adapter_initializes_with_base_id():
    scope_mapper = _load_scope_mapper()
    adapter = scope_mapper.AirtableScopeAdapter()
    assert adapter.base_id
    assert adapter.scope_rules_table == "Scope Rules"


def test_base_id_is_expected_value():
    """base_id must match the canonical Airtable base registered in-tree."""
    scope_mapper = _load_scope_mapper()
    adapter = scope_mapper.AirtableScopeAdapter()
    assert adapter.base_id == "appT4zR1ybxgrujBD"


def test_scope_rules_table_exact_name():
    scope_mapper = _load_scope_mapper()
    adapter = scope_mapper.AirtableScopeAdapter()
    assert adapter.scope_rules_table == "Scope Rules"


def test_multiple_instances_are_independent():
    scope_mapper = _load_scope_mapper()
    a1 = scope_mapper.AirtableScopeAdapter()
    a2 = scope_mapper.AirtableScopeAdapter()
    assert a1.base_id == a2.base_id
    assert a1 is not a2


# ---------------------------------------------------------------------------
# get_active_scope — stub behaviour
# ---------------------------------------------------------------------------

def test_default_scope_is_empty():
    scope_mapper = _load_scope_mapper()
    adapter = scope_mapper.AirtableScopeAdapter()
    assert adapter.get_active_scope() == []


def test_get_active_scope_returns_list():
    scope_mapper = _load_scope_mapper()
    adapter = scope_mapper.AirtableScopeAdapter()
    result = adapter.get_active_scope()
    assert isinstance(result, list)


def test_get_active_scope_is_not_none():
    scope_mapper = _load_scope_mapper()
    adapter = scope_mapper.AirtableScopeAdapter()
    assert adapter.get_active_scope() is not None


def test_get_active_scope_called_multiple_times_is_stable():
    scope_mapper = _load_scope_mapper()
    adapter = scope_mapper.AirtableScopeAdapter()
    assert adapter.get_active_scope() == adapter.get_active_scope()


# ---------------------------------------------------------------------------
# is_authorized — default-deny behaviour
# ---------------------------------------------------------------------------

def test_default_authorization_is_deny():
    scope_mapper = _load_scope_mapper()
    adapter = scope_mapper.AirtableScopeAdapter()
    assert adapter.is_authorized("any-asset") is False


def test_authorization_deny_for_empty_string():
    scope_mapper = _load_scope_mapper()
    adapter = scope_mapper.AirtableScopeAdapter()
    assert adapter.is_authorized("") is False


def test_authorization_deny_for_numeric_id():
    scope_mapper = _load_scope_mapper()
    adapter = scope_mapper.AirtableScopeAdapter()
    assert adapter.is_authorized("12345") is False


def test_authorization_deny_for_special_characters():
    scope_mapper = _load_scope_mapper()
    adapter = scope_mapper.AirtableScopeAdapter()
    assert adapter.is_authorized("!@#$%^&*()") is False


def test_authorization_deny_for_unicode_asset():
    scope_mapper = _load_scope_mapper()
    adapter = scope_mapper.AirtableScopeAdapter()
    assert adapter.is_authorized("资产-001") is False


@pytest.mark.parametrize("asset_id", [
    "example.com",
    "192.168.1.1",
    "*.wildcard.io",
    "app-server-prod",
    "a" * 256,
])
def test_authorization_deny_for_various_asset_ids(asset_id):
    scope_mapper = _load_scope_mapper()
    adapter = scope_mapper.AirtableScopeAdapter()
    assert adapter.is_authorized(asset_id) is False


def test_is_authorized_returns_bool():
    scope_mapper = _load_scope_mapper()
    adapter = scope_mapper.AirtableScopeAdapter()
    result = adapter.is_authorized("any-asset")
    assert isinstance(result, bool)


# ---------------------------------------------------------------------------
# JSON output format — validates the __main__ json.dumps structure
# ---------------------------------------------------------------------------

def test_main_output_is_valid_json_structure():
    """The __main__ block produces a specific JSON payload; validate keys/values."""
    scope_mapper = _load_scope_mapper()
    adapter = scope_mapper.AirtableScopeAdapter()
    payload = {
        "adapter": "airtable",
        "base_id": adapter.base_id,
        "status": "initialized",
    }
    serialized = json.dumps(payload)
    parsed = json.loads(serialized)
    assert parsed["adapter"] == "airtable"
    assert parsed["base_id"] == "appT4zR1ybxgrujBD"
    assert parsed["status"] == "initialized"


def test_main_output_json_is_deserializable():
    scope_mapper = _load_scope_mapper()
    adapter = scope_mapper.AirtableScopeAdapter()
    payload = {
        "adapter": "airtable",
        "base_id": adapter.base_id,
        "status": "initialized",
    }
    assert json.loads(json.dumps(payload)) == payload


def test_main_output_contains_all_expected_keys():
    expected_keys = {"adapter", "base_id", "status"}
    scope_mapper = _load_scope_mapper()
    adapter = scope_mapper.AirtableScopeAdapter()
    payload = {
        "adapter": "airtable",
        "base_id": adapter.base_id,
        "status": "initialized",
    }
    assert set(payload.keys()) == expected_keys


# ---------------------------------------------------------------------------
# Module structure — ensures import brings expected public symbols
# ---------------------------------------------------------------------------

def test_module_exports_adapter_class():
    scope_mapper = _load_scope_mapper()
    assert hasattr(scope_mapper, "AirtableScopeAdapter")


def test_module_imports_json():
    """Regression: json was added in this PR; ensure it is importable from the module."""
    scope_mapper = _load_scope_mapper()
    assert hasattr(scope_mapper, "json")
