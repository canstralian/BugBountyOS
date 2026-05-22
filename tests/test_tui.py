"""Smoke tests for the bbos package (CLI parser + data loaders).

The Textual app itself is not launched here -- it requires an interactive
terminal. Tests cover only the pure-Python surfaces so they run under the
existing CI environment without an extra dependency on textual.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC = REPO_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def test_data_loads_vectors():
    from bbos.data import load_vectors

    vectors = load_vectors()
    assert vectors, "expected at least one vector in registry"
    ids = {v.id for v in vectors}
    assert {"dashboard", "pipeline", "recon"}.issubset(ids)


def test_data_loads_contracts():
    from bbos.data import load_contracts

    contracts = load_contracts()
    assert contracts, "expected at least one contract on disk"
    recon = next((c for c in contracts if c.vector_id == "recon"), None)
    assert recon is not None
    gate_ids = {g.id for g in recon.gates}
    assert "contract_signed" in gate_ids


def test_cli_parses_tui_subcommand():
    from bbos.cli import _build_parser

    args = _build_parser().parse_args(["tui"])
    assert args.command == "tui"


def test_cli_rejects_unknown_command():
    from bbos.cli import _build_parser

    parser = _build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["bogus"])
