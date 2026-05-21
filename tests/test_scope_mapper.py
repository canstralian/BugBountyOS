"""Smoke tests for the Airtable scope adapter."""

import importlib.util
from pathlib import Path


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


def test_default_authorization_is_deny():
    scope_mapper = _load_scope_mapper()
    adapter = scope_mapper.AirtableScopeAdapter()
    assert adapter.is_authorized("any-asset") is False
