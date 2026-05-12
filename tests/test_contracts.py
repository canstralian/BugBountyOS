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


# ---------------------------------------------------------------------------
# Additional vectors registry tests
# ---------------------------------------------------------------------------


def test_vectors_registry_has_exactly_four_entries():
    data = _load("control-plane/registry/vectors.yaml")
    assert len(data["vectors"]) == 4


def test_vectors_registry_trust_levels_are_valid():
    valid_levels = {"permissive", "tainted", "trusted", "quarantined"}
    data = _load("control-plane/registry/vectors.yaml")
    for v in data["vectors"]:
        assert v["trust_level"] in valid_levels, (
            f"Vector {v['id']!r} has unexpected trust_level {v['trust_level']!r}"
        )


def test_vectors_registry_states_are_valid():
    valid_states = {"importing", "active", "canonical", "quarantined", "pending"}
    data = _load("control-plane/registry/vectors.yaml")
    for v in data["vectors"]:
        assert v["state"] in valid_states, (
            f"Vector {v['id']!r} has unexpected state {v['state']!r}"
        )


def test_vectors_red_sage_is_tainted_and_pending():
    data = _load("control-plane/registry/vectors.yaml")
    red_sage = next(v for v in data["vectors"] if v["id"] == "red-sage")
    assert red_sage["trust_level"] == "tainted"
    assert red_sage["state"] == "pending"


def test_vectors_red_sage_contract_version_is_zero():
    data = _load("control-plane/registry/vectors.yaml")
    red_sage = next(v for v in data["vectors"] if v["id"] == "red-sage")
    assert red_sage["contract_version"] == 0


def test_vectors_permissive_vectors_are_importing():
    data = _load("control-plane/registry/vectors.yaml")
    for v in data["vectors"]:
        if v["trust_level"] == "permissive":
            assert v["state"] == "importing", (
                f"Permissive vector {v['id']!r} should be in 'importing' state"
            )


def test_vectors_source_repos_are_non_empty_strings():
    data = _load("control-plane/registry/vectors.yaml")
    for v in data["vectors"]:
        assert isinstance(v["source_repo"], str)
        assert v["source_repo"].strip() != ""


def test_vectors_ids_are_unique():
    data = _load("control-plane/registry/vectors.yaml")
    ids = [v["id"] for v in data["vectors"]]
    assert len(ids) == len(set(ids)), "Duplicate vector IDs found in registry"


# ---------------------------------------------------------------------------
# Additional redsage contract tests
# ---------------------------------------------------------------------------


def test_redsage_contract_signed_gate_is_completed():
    data = _load("contracts/redsage.yaml")
    gate = next(g for g in data["gates"] if g["id"] == "contract_signed")
    assert gate["status"] == "completed"


def test_redsage_remaining_gates_are_pending():
    data = _load("contracts/redsage.yaml")
    pending_gate_ids = {"tests_pass", "spec_kit_score", "integration_pass", "owner_approval"}
    for gate in data["gates"]:
        if gate["id"] in pending_gate_ids:
            assert gate["status"] == "pending", (
                f"Gate {gate['id']!r} expected 'pending', got {gate['status']!r}"
            )


def test_redsage_contract_has_interfaces():
    data = _load("contracts/redsage.yaml")
    assert "interfaces" in data
    assert "input" in data["interfaces"]
    assert "output" in data["interfaces"]


def test_redsage_contract_input_interface_has_event_type():
    data = _load("contracts/redsage.yaml")
    inputs = data["interfaces"]["input"]
    assert len(inputs) >= 1
    assert inputs[0]["type"] == "event"
    assert inputs[0]["source"] == "pipeline"


def test_redsage_contract_output_interface_has_action_plan_type():
    data = _load("contracts/redsage.yaml")
    outputs = data["interfaces"]["output"]
    assert len(outputs) >= 1
    assert outputs[0]["type"] == "action_plan"
    assert outputs[0]["target"] == "execution_engine"


def test_redsage_contract_version_is_semver_string():
    data = _load("contracts/redsage.yaml")
    version = data["version"]
    assert isinstance(version, str)
    parts = version.split(".")
    assert len(parts) == 3, f"Version {version!r} is not in major.minor.patch format"
    for part in parts:
        assert part.isdigit(), f"Version component {part!r} is not an integer"


def test_redsage_contract_role_is_reflex():
    data = _load("contracts/redsage.yaml")
    assert data["role"] == "reflex"


def test_redsage_contract_description_is_non_empty():
    data = _load("contracts/redsage.yaml")
    assert isinstance(data.get("description"), str)
    assert len(data["description"].strip()) > 0


def test_redsage_contract_gates_all_have_id_name_status():
    data = _load("contracts/redsage.yaml")
    for gate in data["gates"]:
        assert "id" in gate, f"Gate missing 'id': {gate}"
        assert "name" in gate, f"Gate missing 'name': {gate}"
        assert "status" in gate, f"Gate missing 'status': {gate}"


def test_redsage_contract_gate_statuses_are_valid():
    valid_statuses = {"pending", "completed", "failed", "skipped"}
    data = _load("contracts/redsage.yaml")
    for gate in data["gates"]:
        assert gate["status"] in valid_statuses, (
            f"Gate {gate['id']!r} has unexpected status {gate['status']!r}"
        )
