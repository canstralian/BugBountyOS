"""
tests/test_adapters.py — Unit tests for changed adapter modules.

Covers:
  - adapters/airtable/scope_mapper.py  (AirtableScopeAdapter)
  - adapters/mcp/server.py             (FastMCP tools: check_scope, list_vectors)
  - vectors/pipeline/nlp_processor.py  (NLPProcessor)
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from adapters.airtable.scope_mapper import AirtableScopeAdapter
from adapters.mcp.server import check_scope, list_vectors, mcp
from vectors.pipeline.nlp_processor import NLPProcessor

# ---------------------------------------------------------------------------
# AirtableScopeAdapter
# ---------------------------------------------------------------------------


class TestAirtableScopeAdapterInit:
    def test_base_id_is_set(self):
        adapter = AirtableScopeAdapter()
        assert adapter.base_id == "appT4zR1ybxgrujBD"

    def test_scope_rules_table_is_set(self):
        adapter = AirtableScopeAdapter()
        assert adapter.scope_rules_table == "Scope Rules"

    def test_creates_independent_instances(self):
        a1 = AirtableScopeAdapter()
        a2 = AirtableScopeAdapter()
        assert a1 is not a2
        assert a1.base_id == a2.base_id


class TestAirtableScopeAdapterGetActiveScope:
    def test_returns_empty_list_by_default(self):
        adapter = AirtableScopeAdapter()
        result = adapter.get_active_scope()
        assert result == []

    def test_return_type_is_list(self):
        adapter = AirtableScopeAdapter()
        result = adapter.get_active_scope()
        assert isinstance(result, list)

    def test_idempotent_multiple_calls(self):
        adapter = AirtableScopeAdapter()
        assert adapter.get_active_scope() == adapter.get_active_scope()


class TestAirtableScopeAdapterIsAuthorized:
    def test_returns_false_for_any_asset(self):
        adapter = AirtableScopeAdapter()
        assert adapter.is_authorized("example.com") is False

    def test_returns_false_for_empty_string(self):
        adapter = AirtableScopeAdapter()
        assert adapter.is_authorized("") is False

    def test_returns_false_for_known_asset(self):
        adapter = AirtableScopeAdapter()
        assert adapter.is_authorized("appT4zR1ybxgrujBD") is False

    def test_return_type_is_bool(self):
        adapter = AirtableScopeAdapter()
        result = adapter.is_authorized("test-asset")
        assert isinstance(result, bool)

    def test_returns_false_for_multiple_assets(self):
        adapter = AirtableScopeAdapter()
        assets = ["api.example.com", "192.168.1.1", "dashboard", "storage"]
        for asset in assets:
            assert adapter.is_authorized(asset) is False


# ---------------------------------------------------------------------------
# MCP Server — check_scope
# ---------------------------------------------------------------------------


class TestMcpCheckScope:
    def test_returns_string(self):
        result = check_scope("example.com")
        assert isinstance(result, str)

    def test_returns_permissive_mode_message(self):
        result = check_scope("any-asset")
        assert "Permissive mode" in result

    def test_message_mentions_airtable(self):
        result = check_scope("any-asset")
        assert "Airtable" in result

    def test_result_is_consistent_for_any_asset_id(self):
        r1 = check_scope("asset-1")
        r2 = check_scope("asset-2")
        assert r1 == r2

    def test_callable_with_empty_string(self):
        result = check_scope("")
        assert isinstance(result, str)

    def test_callable_with_url_asset_id(self):
        result = check_scope("https://api.example.com/v1")
        assert isinstance(result, str)


# ---------------------------------------------------------------------------
# MCP Server — list_vectors
# ---------------------------------------------------------------------------


class TestMcpListVectors:
    def test_returns_list(self):
        result = list_vectors()
        assert isinstance(result, list)

    def test_contains_expected_vectors(self):
        result = list_vectors()
        assert "dashboard" in result
        assert "pipeline" in result
        assert "storage" in result
        assert "red-sage" in result

    def test_exactly_four_vectors(self):
        result = list_vectors()
        assert len(result) == 4

    def test_all_elements_are_strings(self):
        result = list_vectors()
        for v in result:
            assert isinstance(v, str)

    def test_idempotent(self):
        assert list_vectors() == list_vectors()

    def test_no_duplicates(self):
        result = list_vectors()
        assert len(result) == len(set(result))


# ---------------------------------------------------------------------------
# MCP Server — FastMCP instance
# ---------------------------------------------------------------------------


class TestMcpServerInstance:
    def test_server_name(self):
        assert mcp.name == "BugBountyOS Kernel"

    def test_server_is_fastmcp_instance(self):
        from mcp.server.fastmcp import FastMCP

        assert isinstance(mcp, FastMCP)

    def test_tools_registered(self):
        tools = asyncio.run(mcp.list_tools())
        tool_names = {t.name for t in tools}
        assert "check_scope" in tool_names
        assert "list_vectors" in tool_names

    def test_check_scope_tool_description(self):
        tools = asyncio.run(mcp.list_tools())
        check_scope_tool = next(t for t in tools if t.name == "check_scope")
        assert (
            "authorized" in check_scope_tool.description.lower()
            or "scope" in check_scope_tool.description.lower()
        )

    def test_list_vectors_tool_description(self):
        tools = asyncio.run(mcp.list_tools())
        list_vectors_tool = next(t for t in tools if t.name == "list_vectors")
        assert (
            "vector" in list_vectors_tool.description.lower()
            or "registry" in list_vectors_tool.description.lower()
        )

    def test_exactly_two_tools_registered(self):
        tools = asyncio.run(mcp.list_tools())
        assert len(tools) == 2


# ---------------------------------------------------------------------------
# NLPProcessor
# ---------------------------------------------------------------------------


class TestNLPProcessor:
    def test_instantiates_without_error(self):
        processor = NLPProcessor()
        assert processor is not None

    def test_is_nlpprocessor_instance(self):
        processor = NLPProcessor()
        assert isinstance(processor, NLPProcessor)

    def test_multiple_instances_are_independent(self):
        p1 = NLPProcessor()
        p2 = NLPProcessor()
        assert p1 is not p2

    def test_init_does_not_raise(self):
        try:
            NLPProcessor()
        except Exception as exc:
            pytest.fail(f"NLPProcessor.__init__ raised unexpectedly: {exc}")
