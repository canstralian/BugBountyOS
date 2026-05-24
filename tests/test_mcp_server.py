"""Tests for adapters/mcp/server.py."""
from pathlib import Path
from unittest.mock import patch

import yaml

from adapters.mcp.server import REGISTRY_PATH, check_scope, list_vectors


# --- REGISTRY_PATH ---

def test_registry_path_points_to_vectors_yaml():
    assert REGISTRY_PATH.name == "vectors.yaml"
    assert REGISTRY_PATH.parts[-2] == "registry"
    assert REGISTRY_PATH.parts[-3] == "control-plane"


def test_registry_path_exists():
    assert REGISTRY_PATH.exists(), f"Expected registry file at {REGISTRY_PATH}"


# --- check_scope ---

def test_check_scope_returns_string():
    result = check_scope("any-asset-id")
    assert isinstance(result, str)


def test_check_scope_is_permissive_mode():
    result = check_scope("some-asset")
    assert "Permissive" in result


def test_check_scope_is_non_empty():
    result = check_scope("asset-123")
    assert len(result) > 0


def test_check_scope_arbitrary_asset_id():
    # Behavior must be consistent regardless of the asset_id value.
    assert check_scope("") == check_scope("nonexistent-asset-xyz")


def test_check_scope_returns_same_for_any_input():
    r1 = check_scope("aaa")
    r2 = check_scope("bbb")
    assert r1 == r2


# --- list_vectors ---

def test_list_vectors_returns_list():
    result = list_vectors()
    assert isinstance(result, list)


def test_list_vectors_returns_expected_ids():
    result = list_vectors()
    assert result == ["dashboard", "pipeline", "storage", "red-sage"]


def test_list_vectors_all_strings():
    result = list_vectors()
    for item in result:
        assert isinstance(item, str)


def test_list_vectors_count():
    result = list_vectors()
    assert len(result) == 4


def test_list_vectors_contains_dashboard():
    assert "dashboard" in list_vectors()


def test_list_vectors_contains_pipeline():
    assert "pipeline" in list_vectors()


def test_list_vectors_contains_storage():
    assert "storage" in list_vectors()


def test_list_vectors_contains_red_sage():
    assert "red-sage" in list_vectors()


def test_list_vectors_reads_from_registry_yaml():
    # Verify list_vectors is driven by the YAML file content.
    fake_data = {"vectors": [{"id": "alpha"}, {"id": "beta"}]}
    with patch.object(Path, "read_text", return_value=yaml.dump(fake_data)):
        result = list_vectors()
    assert result == ["alpha", "beta"]


def test_list_vectors_empty_registry():
    fake_data = {"vectors": []}
    with patch.object(Path, "read_text", return_value=yaml.dump(fake_data)):
        result = list_vectors()
    assert result == []