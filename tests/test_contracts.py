"""Tests for the contracts and registry YAML."""

import base64
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACTS_DIR = REPO_ROOT / "contracts"
REGISTRY_PATH = REPO_ROOT / "control-plane" / "registry" / "vectors.yaml"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _decode_base64_yaml(path: Path) -> dict:
    """Files in the repo are stored as base64-encoded YAML; decode and parse."""
    raw = path.read_bytes()
    decoded = base64.b64decode(raw)
    return yaml.safe_load(decoded)


# ---------------------------------------------------------------------------
# contracts/redsage.yaml — the only contract remaining after this PR
# ---------------------------------------------------------------------------

def test_contract_yaml_parses():
    with (CONTRACTS_DIR / "redsage.yaml").open() as f:
        data = yaml.safe_load(f)
    assert data is not None


def test_redsage_contract_file_exists():
    assert (CONTRACTS_DIR / "redsage.yaml").is_file()


def test_redsage_contract_is_nonempty():
    assert (CONTRACTS_DIR / "redsage.yaml").stat().st_size > 0


def test_redsage_decoded_yaml_has_vector_id():
    data = _decode_base64_yaml(CONTRACTS_DIR / "redsage.yaml")
    assert data["vector_id"] == "red-sage"


def test_redsage_decoded_yaml_role_is_reflex():
    data = _decode_base64_yaml(CONTRACTS_DIR / "redsage.yaml")
    assert data["role"] == "reflex"


def test_redsage_decoded_yaml_has_version():
    data = _decode_base64_yaml(CONTRACTS_DIR / "redsage.yaml")
    assert "version" in data


def test_redsage_decoded_yaml_has_five_gates():
    data = _decode_base64_yaml(CONTRACTS_DIR / "redsage.yaml")
    gates = data["gates"]
    assert len(gates) == 5


def test_redsage_decoded_yaml_first_gate_is_contract_signed():
    data = _decode_base64_yaml(CONTRACTS_DIR / "redsage.yaml")
    first_gate = data["gates"][0]
    assert first_gate["id"] == "contract_signed"
    assert first_gate["status"] == "completed"


def test_redsage_decoded_yaml_has_interfaces():
    data = _decode_base64_yaml(CONTRACTS_DIR / "redsage.yaml")
    assert "interfaces" in data
    assert "input" in data["interfaces"]
    assert "output" in data["interfaces"]


# ---------------------------------------------------------------------------
# Deleted contracts must not exist (cognition, recon, sensory removed in PR)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("removed_contract", ["cognition.yaml", "recon.yaml", "sensory.yaml"])
def test_removed_contracts_do_not_exist(removed_contract):
    """These contracts were deleted in this PR and must not be present."""
    assert not (CONTRACTS_DIR / removed_contract).exists()


# ---------------------------------------------------------------------------
# control-plane/registry/vectors.yaml — modified in this PR
# ---------------------------------------------------------------------------

def test_vectors_registry_parses():
    with REGISTRY_PATH.open() as f:
        data = yaml.safe_load(f)
    assert data is not None


def test_vectors_registry_file_exists():
    assert REGISTRY_PATH.is_file()


def test_vectors_registry_is_nonempty():
    assert REGISTRY_PATH.stat().st_size > 0


def test_vectors_registry_decoded_has_vectors_key():
    data = _decode_base64_yaml(REGISTRY_PATH)
    assert "vectors" in data


def test_vectors_registry_decoded_has_four_vectors():
    """After this PR: dashboard, pipeline, storage, red-sage (cognition/recon/sensory removed)."""
    data = _decode_base64_yaml(REGISTRY_PATH)
    assert len(data["vectors"]) == 4


def test_vectors_registry_decoded_vector_ids():
    data = _decode_base64_yaml(REGISTRY_PATH)
    ids = {v["id"] for v in data["vectors"]}
    assert ids == {"dashboard", "pipeline", "storage", "red-sage"}


def test_vectors_registry_removed_vectors_absent():
    """cognition, recon, sensory were removed from the registry in this PR."""
    data = _decode_base64_yaml(REGISTRY_PATH)
    ids = {v["id"] for v in data["vectors"]}
    assert "cognition" not in ids
    assert "recon" not in ids
    assert "sensory" not in ids


def test_red_sage_state_is_pending():
    """red-sage changed from 'importing' to 'pending' in this PR."""
    data = _decode_base64_yaml(REGISTRY_PATH)
    red_sage = next(v for v in data["vectors"] if v["id"] == "red-sage")
    assert red_sage["state"] == "pending"


def test_red_sage_trust_level_is_tainted():
    """red-sage trust_level changed from 'permissive' to 'tainted' in this PR."""
    data = _decode_base64_yaml(REGISTRY_PATH)
    red_sage = next(v for v in data["vectors"] if v["id"] == "red-sage")
    assert red_sage["trust_level"] == "tainted"


def test_red_sage_contract_version_is_zero():
    """red-sage contract_version changed from 1 to 0 in this PR."""
    data = _decode_base64_yaml(REGISTRY_PATH)
    red_sage = next(v for v in data["vectors"] if v["id"] == "red-sage")
    assert red_sage["contract_version"] == 0


def test_active_vectors_have_required_fields():
    """Every vector entry must have id, role, state, trust_level, source_repo, contract_version."""
    required = {"id", "role", "state", "trust_level", "source_repo", "contract_version"}
    data = _decode_base64_yaml(REGISTRY_PATH)
    for vector in data["vectors"]:
        missing = required - set(vector.keys())
        assert not missing, f"Vector {vector.get('id')} missing fields: {missing}"


def test_dashboard_vector_is_importing():
    data = _decode_base64_yaml(REGISTRY_PATH)
    dashboard = next(v for v in data["vectors"] if v["id"] == "dashboard")
    assert dashboard["state"] == "importing"
    assert dashboard["trust_level"] == "permissive"


def test_pipeline_vector_is_importing():
    data = _decode_base64_yaml(REGISTRY_PATH)
    pipeline = next(v for v in data["vectors"] if v["id"] == "pipeline")
    assert pipeline["state"] == "importing"
    assert pipeline["trust_level"] == "permissive"


def test_storage_vector_is_importing():
    data = _decode_base64_yaml(REGISTRY_PATH)
    storage = next(v for v in data["vectors"] if v["id"] == "storage")
    assert storage["state"] == "importing"
    assert storage["trust_level"] == "permissive"
