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
