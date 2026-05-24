from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent


def _load(path):
    with open(ROOT / path) as f:
        return yaml.safe_load(f)


def test_vectors_registry_shape():
    data = _load("control-plane/registry/vectors.yaml")
    vectors = data["vectors"]
    ids = [v["id"] for v in vectors]
    assert ids == ["dashboard", "pipeline", "storage", "red-sage"]
    for v in vectors:
        assert set(v) >= {"id", "role", "state", "trust_level", "source_repo", "contract_version"}


def test_redsage_contract_has_required_gates():
    data = _load("contracts/redsage.yaml")
    assert data["vector_id"] == "red-sage"
    gate_ids = {g["id"] for g in data["gates"]}
    assert {"contract_signed", "tests_pass", "spec_kit_score", "integration_pass", "owner_approval"} <= gate_ids


# --- vectors.yaml extended tests ---

def test_vector_ids_are_unique():
    data = _load("control-plane/registry/vectors.yaml")
    ids = [v["id"] for v in data["vectors"]]
    assert len(ids) == len(set(ids))


def test_vectors_registry_count():
    data = _load("control-plane/registry/vectors.yaml")
    assert len(data["vectors"]) == 4


def test_dashboard_vector_fields():
    data = _load("control-plane/registry/vectors.yaml")
    dashboard = next(v for v in data["vectors"] if v["id"] == "dashboard")
    assert dashboard["role"] == "visual-cortex"
    assert dashboard["state"] == "importing"
    assert dashboard["trust_level"] == "permissive"
    assert dashboard["source_repo"] == "canstralian/BugBountyBot"
    assert dashboard["contract_version"] == 1


def test_pipeline_vector_fields():
    data = _load("control-plane/registry/vectors.yaml")
    pipeline = next(v for v in data["vectors"] if v["id"] == "pipeline")
    assert pipeline["role"] == "metabolism"
    assert pipeline["state"] == "importing"
    assert pipeline["trust_level"] == "permissive"
    assert pipeline["source_repo"] == "canstralian/BugBountyPipeline"
    assert pipeline["contract_version"] == 1


def test_storage_vector_fields():
    data = _load("control-plane/registry/vectors.yaml")
    storage = next(v for v in data["vectors"] if v["id"] == "storage")
    assert storage["role"] == "memory"
    assert storage["state"] == "importing"
    assert storage["trust_level"] == "permissive"
    assert storage["source_repo"] == "canstralian/BugBountyManager"
    assert storage["contract_version"] == 1


def test_redsage_vector_is_tainted_and_pending():
    data = _load("control-plane/registry/vectors.yaml")
    red_sage = next(v for v in data["vectors"] if v["id"] == "red-sage")
    assert red_sage["state"] == "pending"
    assert red_sage["trust_level"] == "tainted"
    assert red_sage["contract_version"] == 0
    assert red_sage["source_repo"] == "canstralian/RedSageBot"


def test_all_contract_versions_are_integers():
    data = _load("control-plane/registry/vectors.yaml")
    for v in data["vectors"]:
        assert isinstance(v["contract_version"], int)


def test_importing_vectors_are_permissive():
    # All vectors in 'importing' state must have permissive trust level.
    data = _load("control-plane/registry/vectors.yaml")
    for v in data["vectors"]:
        if v["state"] == "importing":
            assert v["trust_level"] == "permissive", (
                f"Vector {v['id']} is importing but has trust_level={v['trust_level']!r}"
            )


# --- contracts/redsage.yaml extended tests ---

def test_redsage_contract_top_level_fields():
    data = _load("contracts/redsage.yaml")
    assert data["role"] == "reflex"
    assert data["version"] == "1.0.0"
    assert "description" in data


def test_redsage_contract_signed_gate_is_completed():
    data = _load("contracts/redsage.yaml")
    signed = next(g for g in data["gates"] if g["id"] == "contract_signed")
    assert signed["status"] == "completed"


def test_redsage_pending_gates():
    data = _load("contracts/redsage.yaml")
    pending_ids = {g["id"] for g in data["gates"] if g["status"] == "pending"}
    assert "tests_pass" in pending_ids
    assert "spec_kit_score" in pending_ids
    assert "integration_pass" in pending_ids
    assert "owner_approval" in pending_ids


def test_redsage_gate_count():
    data = _load("contracts/redsage.yaml")
    assert len(data["gates"]) == 5


def test_redsage_interfaces_present():
    data = _load("contracts/redsage.yaml")
    assert "interfaces" in data
    assert "input" in data["interfaces"]
    assert "output" in data["interfaces"]


def test_redsage_input_interface():
    data = _load("contracts/redsage.yaml")
    inputs = data["interfaces"]["input"]
    assert len(inputs) >= 1
    assert inputs[0]["type"] == "event"
    assert inputs[0]["source"] == "pipeline"


def test_redsage_output_interface():
    data = _load("contracts/redsage.yaml")
    outputs = data["interfaces"]["output"]
    assert len(outputs) >= 1
    assert outputs[0]["type"] == "action_plan"
    assert outputs[0]["target"] == "execution_engine"


def test_redsage_gate_ids_are_unique():
    data = _load("contracts/redsage.yaml")
    gate_ids = [g["id"] for g in data["gates"]]
    assert len(gate_ids) == len(set(gate_ids))


def test_all_gates_have_required_fields():
    data = _load("contracts/redsage.yaml")
    for gate in data["gates"]:
        assert "id" in gate
        assert "name" in gate
        assert "status" in gate
