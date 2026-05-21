"""Invariant checks for per-vector contract YAMLs.

Each file in contracts/ is base64-encoded on disk (see CLAUDE.md) and
describes a vector's role, version, interfaces, and the Five Gates from
docs/CONTRACTS.md. These tests assert structural and schema-level
guarantees that every contract must satisfy, without pinning specific
contract names or per-contract field values.

Tests should fail when:
- a contract file becomes unreadable or non-base64
- decoded content is not valid YAML
- a required top-level key is missing
- the Five Gates structural requirement is broken
- a gate is missing its id or status

Tests should NOT fail when:
- contracts are added or removed
- a contract legitimately updates its version, gate status, or interfaces
"""
import base64
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACTS_DIR = REPO_ROOT / "contracts"

# Required top-level keys for every contract. These come from
# docs/CONTRACTS.md and the kernel/control-plane integration surface.
REQUIRED_CONTRACT_KEYS = {"vector_id", "role", "version", "gates", "interfaces"}

# The Five Gates (docs/CONTRACTS.md). Every contract must declare exactly
# this many gates — this is a true schema requirement, not a snapshot.
EXPECTED_GATE_COUNT = 5

# Recognised gate statuses. Add to this set when the lifecycle vocabulary
# legitimately grows.
ALLOWED_GATE_STATUSES = {"pending", "in_progress", "completed", "failed", "skipped"}


def _contract_files() -> list[Path]:
    return sorted(p for p in CONTRACTS_DIR.glob("*.yaml") if p.is_file())


def _decode_contract(path: Path) -> dict:
    raw = path.read_bytes()
    # Normalize whitespace for strict base64 validation
    clean_raw = raw.strip()
    clean_raw = b"".join(clean_raw.split())
    try:
        decoded = base64.b64decode(clean_raw, validate=True)
    except (ValueError, Exception) as exc:  # noqa: BLE001
        raise AssertionError(
            f"contract {path.name} is not valid base64: {exc}"
        ) from exc
    return yaml.safe_load(decoded)


def test_contracts_directory_has_at_least_one_contract():
    """We don't pin a specific count, but the directory must not be empty."""
    files = _contract_files()
    assert files, "contracts/ must contain at least one *.yaml contract"


@pytest.mark.parametrize("contract_path", _contract_files(), ids=lambda p: p.name)
def test_contract_is_valid_base64_yaml(contract_path):
    data = _decode_contract(contract_path)
    assert data is not None, f"{contract_path.name} decoded to empty content"
    assert isinstance(data, dict), (
        f"{contract_path.name} must be a YAML mapping, got {type(data).__name__}"
    )


@pytest.mark.parametrize("contract_path", _contract_files(), ids=lambda p: p.name)
def test_contract_has_required_top_level_keys(contract_path):
    data = _decode_contract(contract_path)
    missing = REQUIRED_CONTRACT_KEYS - set(data.keys())
    assert not missing, (
        f"{contract_path.name} is missing required keys: {sorted(missing)}"
    )


@pytest.mark.parametrize("contract_path", _contract_files(), ids=lambda p: p.name)
def test_contract_vector_id_is_nonempty_string(contract_path):
    data = _decode_contract(contract_path)
    vid = data["vector_id"]
    assert isinstance(vid, str) and vid.strip(), (
        f"{contract_path.name} vector_id must be a non-empty string, got {vid!r}"
    )


@pytest.mark.parametrize("contract_path", _contract_files(), ids=lambda p: p.name)
def test_contract_declares_five_gates(contract_path):
    """docs/CONTRACTS.md mandates exactly five gates per vector."""
    data = _decode_contract(contract_path)
    gates = data["gates"]
    assert isinstance(gates, list), f"{contract_path.name} gates must be a list"
    assert len(gates) == EXPECTED_GATE_COUNT, (
        f"{contract_path.name} declares {len(gates)} gates; "
        f"the Five Gates spec requires exactly {EXPECTED_GATE_COUNT}"
    )


@pytest.mark.parametrize("contract_path", _contract_files(), ids=lambda p: p.name)
def test_every_gate_has_id_and_status(contract_path):
    data = _decode_contract(contract_path)
    for idx, gate in enumerate(data["gates"]):
        assert isinstance(gate, dict), (
            f"{contract_path.name} gate[{idx}] must be a mapping, got {gate!r}"
        )
        assert "id" in gate and isinstance(gate["id"], str) and gate["id"].strip(), (
            f"{contract_path.name} gate[{idx}] missing or empty `id`"
        )
        assert "status" in gate, (
            f"{contract_path.name} gate[{idx}] ({gate.get('id')!r}) missing `status`"
        )
        assert gate["status"] in ALLOWED_GATE_STATUSES, (
            f"{contract_path.name} gate {gate['id']!r} has unrecognised status "
            f"{gate['status']!r}; allowed: {sorted(ALLOWED_GATE_STATUSES)}"
        )


@pytest.mark.parametrize("contract_path", _contract_files(), ids=lambda p: p.name)
def test_gate_ids_are_unique_within_a_contract(contract_path):
    data = _decode_contract(contract_path)
    ids = [gate["id"] for gate in data["gates"]]
    duplicates = {gid for gid in ids if ids.count(gid) > 1}
    assert not duplicates, (
        f"{contract_path.name} has duplicate gate ids: {sorted(duplicates)}"
    )


@pytest.mark.parametrize("contract_path", _contract_files(), ids=lambda p: p.name)
def test_contract_interfaces_declare_input_and_output(contract_path):
    """Interfaces are the kernel's typed routing boundary; both ends required."""
    data = _decode_contract(contract_path)
    interfaces = data["interfaces"]
    assert isinstance(interfaces, dict), (
        f"{contract_path.name} interfaces must be a mapping"
    )
    for required in ("input", "output"):
        assert required in interfaces, (
            f"{contract_path.name} interfaces is missing `{required}`"
        )
