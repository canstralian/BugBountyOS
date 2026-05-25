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


# ---------------------------------------------------------------------------
# bbos.__version__
# ---------------------------------------------------------------------------


def test_version_string():
    import bbos

    assert bbos.__version__ == "0.1.0"


def test_version_is_string():
    import bbos

    assert isinstance(bbos.__version__, str)


# ---------------------------------------------------------------------------
# _decode_yaml_bytes — unit tests with synthetic payloads
# ---------------------------------------------------------------------------


class TestDecodeYamlBytes:
    @pytest.fixture(autouse=True)
    def _import(self):
        from bbos.data import _decode_yaml_bytes

        self._decode = _decode_yaml_bytes

    def test_plain_yaml_dict(self):
        raw = b"key: value\nother: 42\n"
        result = self._decode(raw)
        assert result == {"key": "value", "other": 42}

    def test_base64_encoded_yaml(self):
        import base64

        payload = b"vectors:\n  - id: v1\n"
        encoded = base64.b64encode(payload)
        result = self._decode(encoded)
        assert result == {"vectors": [{"id": "v1"}]}

    def test_base64_with_line_wrapping(self):
        import base64
        import textwrap

        payload = b"role: tester\nstate: active\n"
        encoded = base64.b64encode(payload).decode("ascii")
        # Simulate PEM-style line wrapping (every 76 chars)
        wrapped = "\n".join(textwrap.wrap(encoded, 76)).encode("ascii")
        result = self._decode(wrapped)
        assert result == {"role": "tester", "state": "active"}

    def test_invalid_base64_falls_back_to_plain_yaml(self):
        # Contains characters not valid in base64; should fall back to YAML parse
        raw = b"not_b64: true\n!!notb64!!\n"
        result = self._decode(raw)
        # Falls back: result is the parsed YAML dict (ignoring the invalid line)
        assert isinstance(result, dict)

    def test_empty_bytes_returns_empty_dict(self):
        result = self._decode(b"")
        assert result == {}

    def test_yaml_list_at_root_returns_empty_dict(self):
        # YAML that parses to a list, not a dict -> should return {}
        raw = b"- item1\n- item2\n"
        result = self._decode(raw)
        assert result == {}

    def test_yaml_scalar_at_root_returns_empty_dict(self):
        raw = b"just a string\n"
        result = self._decode(raw)
        assert result == {}

    def test_null_yaml_returns_empty_dict(self):
        result = self._decode(b"null\n")
        assert result == {}

    def test_base64_that_decodes_to_non_dict_yaml_falls_back(self):
        import base64

        # Base64 of a YAML list — should fall back because parsed result isn't a dict
        payload = b"- a\n- b\n"
        encoded = base64.b64encode(payload)
        # Falls back to plain YAML of the base64 string itself,
        # which is a scalar -> returns {}
        result = self._decode(encoded)
        assert result == {}

    def test_whitespace_only_bytes_returns_empty_dict(self):
        result = self._decode(b"   \n\t  \n")
        assert result == {}

    def test_nested_dict_plain_yaml(self):
        raw = b"interfaces:\n  input:\n    - type: domain\n      description: target domain\n"
        result = self._decode(raw)
        assert result["interfaces"]["input"][0]["type"] == "domain"


# ---------------------------------------------------------------------------
# load_vectors — parametric tests using tmp_path
# ---------------------------------------------------------------------------


class TestLoadVectors:
    @pytest.fixture(autouse=True)
    def _import(self):
        from bbos.data import load_vectors

        self._load = load_vectors

    def test_nonexistent_path_returns_empty_list(self, tmp_path):
        result = self._load(tmp_path / "does_not_exist.yaml")
        assert result == []

    def test_empty_vectors_key_returns_empty_list(self, tmp_path):
        f = tmp_path / "vectors.yaml"
        f.write_text("vectors: []\n", encoding="utf-8")
        result = self._load(f)
        assert result == []

    def test_null_vectors_key_returns_empty_list(self, tmp_path):
        f = tmp_path / "vectors.yaml"
        f.write_text("vectors: null\n", encoding="utf-8")
        result = self._load(f)
        assert result == []

    def test_missing_vectors_key_returns_empty_list(self, tmp_path):
        f = tmp_path / "vectors.yaml"
        f.write_text("other: data\n", encoding="utf-8")
        result = self._load(f)
        assert result == []

    def test_single_vector_plain_yaml(self, tmp_path):
        f = tmp_path / "vectors.yaml"
        f.write_text(
            "vectors:\n"
            "  - id: testvec\n"
            "    role: scanner\n"
            "    state: active\n"
            "    trust_level: high\n"
            "    source_repo: github.com/org/repo\n"
            "    contract_version: 3\n",
            encoding="utf-8",
        )
        result = self._load(f)
        assert len(result) == 1
        v = result[0]
        assert v.id == "testvec"
        assert v.role == "scanner"
        assert v.state == "active"
        assert v.trust_level == "high"
        assert v.source_repo == "github.com/org/repo"
        assert v.contract_version == 3

    def test_multiple_vectors(self, tmp_path):
        f = tmp_path / "vectors.yaml"
        f.write_text(
            "vectors:\n"
            "  - id: vec1\n"
            "    role: r1\n"
            "    state: s1\n"
            "    trust_level: t1\n"
            "    source_repo: repo1\n"
            "    contract_version: 1\n"
            "  - id: vec2\n"
            "    role: r2\n"
            "    state: s2\n"
            "    trust_level: t2\n"
            "    source_repo: repo2\n"
            "    contract_version: 2\n",
            encoding="utf-8",
        )
        result = self._load(f)
        assert len(result) == 2
        assert {v.id for v in result} == {"vec1", "vec2"}

    def test_missing_fields_use_empty_string_defaults(self, tmp_path):
        f = tmp_path / "vectors.yaml"
        f.write_text("vectors:\n  - id: minimal\n", encoding="utf-8")
        result = self._load(f)
        assert len(result) == 1
        v = result[0]
        assert v.id == "minimal"
        assert v.role == ""
        assert v.state == ""
        assert v.trust_level == ""
        assert v.source_repo == ""
        assert v.contract_version == 0

    def test_null_fields_coerced_to_empty_string(self, tmp_path):
        f = tmp_path / "vectors.yaml"
        f.write_text(
            "vectors:\n  - id: ~\n    role: ~\n    state: ~\n"
            "    trust_level: ~\n    source_repo: ~\n    contract_version: ~\n",
            encoding="utf-8",
        )
        result = self._load(f)
        assert len(result) == 1
        v = result[0]
        assert v.id == ""
        assert v.role == ""
        assert v.contract_version == 0

    def test_contract_version_zero_default(self, tmp_path):
        f = tmp_path / "vectors.yaml"
        f.write_text("vectors:\n  - id: v1\n", encoding="utf-8")
        result = self._load(f)
        assert result[0].contract_version == 0

    def test_base64_encoded_registry(self, tmp_path):
        import base64

        payload = (
            b"vectors:\n"
            b"  - id: b64vec\n"
            b"    role: encoded\n"
            b"    state: active\n"
            b"    trust_level: medium\n"
            b"    source_repo: repo\n"
            b"    contract_version: 1\n"
        )
        encoded = base64.b64encode(payload)
        f = tmp_path / "vectors.yaml"
        f.write_bytes(encoded)
        result = self._load(f)
        assert len(result) == 1
        assert result[0].id == "b64vec"

    def test_vectors_are_frozen_dataclasses(self, tmp_path):
        from bbos.data import Vector

        f = tmp_path / "vectors.yaml"
        f.write_text(
            "vectors:\n  - id: v1\n    role: r\n    state: s\n"
            "    trust_level: t\n    source_repo: sr\n    contract_version: 0\n",
            encoding="utf-8",
        )
        result = self._load(f)
        v = result[0]
        with pytest.raises((AttributeError, TypeError)):
            v.id = "mutated"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# load_contracts — parametric tests using tmp_path
# ---------------------------------------------------------------------------


class TestLoadContracts:
    @pytest.fixture(autouse=True)
    def _import(self):
        from bbos.data import load_contracts

        self._load = load_contracts

    def test_nonexistent_dir_returns_empty_list(self, tmp_path):
        result = self._load(tmp_path / "no_such_dir")
        assert result == []

    def test_empty_dir_returns_empty_list(self, tmp_path):
        d = tmp_path / "contracts"
        d.mkdir()
        result = self._load(d)
        assert result == []

    def test_non_yaml_files_ignored(self, tmp_path):
        d = tmp_path / "contracts"
        d.mkdir()
        (d / "readme.txt").write_text("irrelevant", encoding="utf-8")
        result = self._load(d)
        assert result == []

    def test_minimal_contract(self, tmp_path):
        d = tmp_path / "contracts"
        d.mkdir()
        (d / "alpha.yaml").write_text(
            "vector_id: alpha\nrole: scanner\ndescription: does scanning\nversion: '1'\n",
            encoding="utf-8",
        )
        result = self._load(d)
        assert len(result) == 1
        c = result[0]
        assert c.vector_id == "alpha"
        assert c.role == "scanner"
        assert c.description == "does scanning"
        assert c.version == "1"
        assert c.gates == ()
        assert c.inputs == ()
        assert c.outputs == ()

    def test_vector_id_falls_back_to_path_stem(self, tmp_path):
        d = tmp_path / "contracts"
        d.mkdir()
        (d / "mycontract.yaml").write_text("role: worker\n", encoding="utf-8")
        result = self._load(d)
        assert result[0].vector_id == "mycontract"

    def test_gates_parsed(self, tmp_path):
        d = tmp_path / "contracts"
        d.mkdir()
        (d / "beta.yaml").write_text(
            "vector_id: beta\n"
            "gates:\n"
            "  - id: contract_signed\n"
            "    name: Contract Signed\n"
            "    status: completed\n"
            "  - id: scope_approved\n"
            "    name: Scope Approved\n"
            "    status: pending\n",
            encoding="utf-8",
        )
        result = self._load(d)
        c = result[0]
        assert len(c.gates) == 2
        gate_ids = {g.id for g in c.gates}
        assert gate_ids == {"contract_signed", "scope_approved"}
        signed = next(g for g in c.gates if g.id == "contract_signed")
        assert signed.status == "completed"
        assert signed.name == "Contract Signed"

    def test_inputs_parsed(self, tmp_path):
        d = tmp_path / "contracts"
        d.mkdir()
        (d / "gamma.yaml").write_text(
            "vector_id: gamma\n"
            "interfaces:\n"
            "  input:\n"
            "    - type: domain\n"
            "      description: a domain name\n",
            encoding="utf-8",
        )
        result = self._load(d)
        c = result[0]
        assert len(c.inputs) == 1
        assert c.inputs[0].type == "domain"
        assert c.inputs[0].description == "a domain name"

    def test_outputs_parsed(self, tmp_path):
        d = tmp_path / "contracts"
        d.mkdir()
        (d / "delta.yaml").write_text(
            "vector_id: delta\n"
            "interfaces:\n"
            "  output:\n"
            "    - type: report\n"
            "      description: final report\n",
            encoding="utf-8",
        )
        result = self._load(d)
        c = result[0]
        assert len(c.outputs) == 1
        assert c.outputs[0].type == "report"

    def test_type_key_typo_tolerance(self, tmp_path):
        """load_contracts should tolerate the 't^e' typo instead of 'type'."""
        d = tmp_path / "contracts"
        d.mkdir()
        (d / "recon.yaml").write_text(
            "vector_id: recon\n"
            "interfaces:\n"
            "  input:\n"
            "    - t^e: domain\n"
            "      description: typo-key domain\n",
            encoding="utf-8",
        )
        result = self._load(d)
        c = result[0]
        assert len(c.inputs) == 1
        assert c.inputs[0].type == "domain"

    def test_null_gates_field_treated_as_empty(self, tmp_path):
        d = tmp_path / "contracts"
        d.mkdir()
        (d / "epsilon.yaml").write_text(
            "vector_id: epsilon\ngates: null\n", encoding="utf-8"
        )
        result = self._load(d)
        assert result[0].gates == ()

    def test_null_interfaces_field_treated_as_empty(self, tmp_path):
        d = tmp_path / "contracts"
        d.mkdir()
        (d / "zeta.yaml").write_text(
            "vector_id: zeta\ninterfaces: null\n", encoding="utf-8"
        )
        result = self._load(d)
        c = result[0]
        assert c.inputs == ()
        assert c.outputs == ()

    def test_contracts_sorted_by_filename(self, tmp_path):
        d = tmp_path / "contracts"
        d.mkdir()
        for name in ("zzz", "aaa", "mmm"):
            (d / f"{name}.yaml").write_text(
                f"vector_id: {name}\n", encoding="utf-8"
            )
        result = self._load(d)
        ids = [c.vector_id for c in result]
        assert ids == ["aaa", "mmm", "zzz"]

    def test_base64_encoded_contract(self, tmp_path):
        import base64

        payload = (
            b"vector_id: encoded_vec\n"
            b"role: encoded_role\n"
            b"version: '2'\n"
            b"gates:\n"
            b"  - id: gate1\n"
            b"    name: Gate One\n"
            b"    status: completed\n"
        )
        encoded = base64.b64encode(payload)
        d = tmp_path / "contracts"
        d.mkdir()
        (d / "enc.yaml").write_bytes(encoded)
        result = self._load(d)
        assert len(result) == 1
        c = result[0]
        assert c.vector_id == "encoded_vec"
        assert c.role == "encoded_role"
        assert len(c.gates) == 1
        assert c.gates[0].id == "gate1"
        assert c.gates[0].status == "completed"

    def test_gate_missing_fields_default_to_empty_string(self, tmp_path):
        d = tmp_path / "contracts"
        d.mkdir()
        (d / "partial.yaml").write_text(
            "vector_id: partial\ngates:\n  - {}\n", encoding="utf-8"
        )
        result = self._load(d)
        g = result[0].gates[0]
        assert g.id == ""
        assert g.name == ""
        assert g.status == ""

    def test_contracts_are_frozen_dataclasses(self, tmp_path):
        d = tmp_path / "contracts"
        d.mkdir()
        (d / "immut.yaml").write_text("vector_id: immut\n", encoding="utf-8")
        result = self._load(d)
        c = result[0]
        with pytest.raises((AttributeError, TypeError)):
            c.vector_id = "changed"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# cli.main — dispatch and error-exit behaviour
# ---------------------------------------------------------------------------


class TestCliMain:
    @pytest.fixture(autouse=True)
    def _import(self):
        from bbos.cli import main, tui_main

        self._main = main
        self._tui_main = tui_main

    def test_main_dispatches_tui_subcommand(self, monkeypatch):
        monkeypatch.setattr(
            "bbos.cli.tui_main", lambda: 0
        )
        from bbos import cli

        monkeypatch.setattr(cli, "tui_main", lambda: 0)
        result = cli.main(["tui"])
        assert result == 0

    def test_main_no_args_exits_nonzero(self):
        with pytest.raises(SystemExit) as exc_info:
            self._main([])
        assert exc_info.value.code != 0

    def test_main_unknown_subcommand_exits(self):
        with pytest.raises(SystemExit):
            self._main(["unknown"])

    def test_tui_main_missing_textual_returns_1(self, monkeypatch):
        import sys
        import io

        # Simulate textual not being importable by setting its sys.modules entry to None
        monkeypatch.setitem(sys.modules, "textual", None)
        monkeypatch.setitem(sys.modules, "bbos.tui.app", None)

        stderr_capture = io.StringIO()
        monkeypatch.setattr(sys, "stderr", stderr_capture)

        from bbos import cli

        result = cli.tui_main()
        assert result == 1
        assert "textual" in stderr_capture.getvalue().lower()

    def test_tui_main_missing_textual_writes_stderr(self, monkeypatch):
        import sys
        import io

        monkeypatch.setitem(sys.modules, "textual", None)
        monkeypatch.setitem(sys.modules, "bbos.tui.app", None)

        stderr_capture = io.StringIO()
        monkeypatch.setattr(sys, "stderr", stderr_capture)

        from bbos import cli

        cli.tui_main()
        output = stderr_capture.getvalue()
        assert "pip install" in output

    def test_build_parser_prog_name(self):
        from bbos.cli import _build_parser

        parser = _build_parser()
        assert parser.prog == "bbos"

    def test_build_parser_tui_command_exists(self):
        from bbos.cli import _build_parser

        # Should not raise
        args = _build_parser().parse_args(["tui"])
        assert args.command == "tui"

    def test_main_with_none_argv_uses_sys_argv(self, monkeypatch):
        """main(None) should call parse_args with sys.argv[1:]; test it exits when no args."""
        import sys

        monkeypatch.setattr(sys, "argv", ["bbos"])
        with pytest.raises(SystemExit):
            self._main(None)


# ---------------------------------------------------------------------------
# Dataclass immutability and structure
# ---------------------------------------------------------------------------


class TestDataclasses:
    def test_vector_is_hashable(self):
        from bbos.data import Vector

        v = Vector(
            id="v1", role="r", state="s", trust_level="t",
            source_repo="sr", contract_version=1,
        )
        assert hash(v) is not None
        assert {v}  # can be put in a set

    def test_gate_is_hashable(self):
        from bbos.data import Gate

        g = Gate(id="g1", name="Gate 1", status="pending")
        assert hash(g) is not None

    def test_interface_is_hashable(self):
        from bbos.data import Interface

        i = Interface(type="domain", description="a domain")
        assert hash(i) is not None

    def test_contract_is_hashable(self):
        from bbos.data import Contract, Gate, Interface

        c = Contract(
            vector_id="cv",
            role="r",
            description="d",
            version="1",
            gates=(Gate(id="g", name="G", status="ok"),),
            inputs=(Interface(type="t", description="d"),),
            outputs=(),
        )
        assert hash(c) is not None

    def test_vector_equality(self):
        from bbos.data import Vector

        v1 = Vector(id="x", role="r", state="s", trust_level="t", source_repo="sr", contract_version=0)
        v2 = Vector(id="x", role="r", state="s", trust_level="t", source_repo="sr", contract_version=0)
        assert v1 == v2

    def test_gate_defaults_empty_strings(self):
        from bbos.data import Gate

        g = Gate(id="", name="", status="")
        assert g.id == ""
        assert g.name == ""
        assert g.status == ""

    def test_contract_default_tuples_are_empty(self):
        from bbos.data import Contract

        c = Contract(vector_id="v", role="r", description="d", version="1")
        assert c.gates == ()
        assert c.inputs == ()
        assert c.outputs == ()


# ---------------------------------------------------------------------------
# Regression / boundary tests
# ---------------------------------------------------------------------------


def test_decode_yaml_bytes_handles_windows_line_endings():
    from bbos.data import _decode_yaml_bytes

    raw = b"key: val\r\nother: 2\r\n"
    result = _decode_yaml_bytes(raw)
    assert result == {"key": "val", "other": 2}


def test_load_vectors_contract_version_string_coerced_to_int(tmp_path):
    from bbos.data import load_vectors

    f = tmp_path / "vectors.yaml"
    f.write_text(
        "vectors:\n  - id: v1\n    contract_version: '5'\n",
        encoding="utf-8",
    )
    result = load_vectors(f)
    assert result[0].contract_version == 5


def test_load_contracts_multiple_inputs_and_outputs(tmp_path):
    from bbos.data import load_contracts

    d = tmp_path / "contracts"
    d.mkdir()
    (d / "multi.yaml").write_text(
        "vector_id: multi\n"
        "interfaces:\n"
        "  input:\n"
        "    - type: domain\n      description: domain input\n"
        "    - type: ip\n        description: ip input\n"
        "  output:\n"
        "    - type: report\n      description: final report\n"
        "    - type: ioc\n        description: ioc list\n",
        encoding="utf-8",
    )
    result = load_contracts(d)
    c = result[0]
    assert len(c.inputs) == 2
    assert len(c.outputs) == 2
    input_types = {i.type for i in c.inputs}
    assert "domain" in input_types
    output_types = {o.type for o in c.outputs}
    assert "report" in output_types


def test_load_contracts_gate_name_fallback_in_findings_display(tmp_path):
    """Findings view uses g.name or g.id - ensure both fields are accessible."""
    from bbos.data import load_contracts

    d = tmp_path / "contracts"
    d.mkdir()
    (d / "named.yaml").write_text(
        "vector_id: named\n"
        "gates:\n"
        "  - id: gate_with_name\n    name: Named Gate\n    status: completed\n"
        "  - id: gate_no_name\n    name: ''\n    status: pending\n",
        encoding="utf-8",
    )
    result = load_contracts(d)
    g1, g2 = result[0].gates
    # Mimic the FindingsView fallback: g.name or g.id
    assert (g1.name or g1.id) == "Named Gate"
    assert (g2.name or g2.id) == "gate_no_name"
