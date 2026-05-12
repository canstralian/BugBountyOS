"""Tests for adapters/mcp/server.py.

Tests the check_scope and list_vectors tool functions and the REGISTRY_PATH
constant without exercising the MCP transport layer.
"""
from pathlib import Path

import yaml

from adapters.mcp.server import REGISTRY_PATH, check_scope, list_vectors


# ---------------------------------------------------------------------------
# REGISTRY_PATH constant
# ---------------------------------------------------------------------------


def test_registry_path_is_path_instance():
    assert isinstance(REGISTRY_PATH, Path)


def test_registry_path_file_exists():
    assert REGISTRY_PATH.exists(), f"Registry file not found: {REGISTRY_PATH}"


def test_registry_path_is_file_not_directory():
    assert REGISTRY_PATH.is_file()


def test_registry_path_ends_with_vectors_yaml():
    assert REGISTRY_PATH.name == "vectors.yaml"


# ---------------------------------------------------------------------------
# check_scope
# ---------------------------------------------------------------------------


def test_check_scope_returns_string():
    result = check_scope("any-asset")
    assert isinstance(result, str)


def test_check_scope_response_contains_permissive_mode():
    result = check_scope("any-asset")
    assert "Permissive" in result


def test_check_scope_with_empty_asset_id_returns_string():
    result = check_scope("")
    assert isinstance(result, str)


def test_check_scope_response_is_same_for_any_input():
    """check_scope is a stub that returns the same message regardless of asset_id."""
    result_a = check_scope("asset-1")
    result_b = check_scope("asset-2")
    result_c = check_scope("")
    assert result_a == result_b == result_c


def test_check_scope_with_special_characters():
    result = check_scope("!@#$%^&*()")
    assert isinstance(result, str)
    assert len(result) > 0


# ---------------------------------------------------------------------------
# list_vectors
# ---------------------------------------------------------------------------


def test_list_vectors_returns_list():
    result = list_vectors()
    assert isinstance(result, list)


def test_list_vectors_contains_all_expected_ids():
    result = list_vectors()
    expected = {"dashboard", "pipeline", "storage", "red-sage"}
    assert expected <= set(result)


def test_list_vectors_order_matches_registry():
    result = list_vectors()
    assert result == ["dashboard", "pipeline", "storage", "red-sage"]


def test_list_vectors_count_matches_registry():
    raw = yaml.safe_load(REGISTRY_PATH.read_text())
    assert len(list_vectors()) == len(raw["vectors"])


def test_list_vectors_all_items_are_strings():
    for item in list_vectors():
        assert isinstance(item, str), f"Non-string vector id: {item!r}"


def test_list_vectors_contains_no_duplicates():
    result = list_vectors()
    assert len(result) == len(set(result))


def test_list_vectors_does_not_contain_empty_strings():
    for item in list_vectors():
        assert item.strip() != "", "Vector registry contained a blank id"