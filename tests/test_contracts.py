from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent


def test_redsage_contract_valid_yaml_with_required_fields():
    data = yaml.safe_load((ROOT / "contracts" / "redsage.yaml").read_text())
    assert data["vector_id"] == "red-sage"
    assert data["role"] == "reflex"
    assert isinstance(data["gates"], list) and len(data["gates"]) >= 1
    for gate in data["gates"]:
        assert "id" in gate
        assert "status" in gate


def test_vector_registry_valid():
    data = yaml.safe_load((ROOT / "control-plane" / "registry" / "vectors.yaml").read_text())
    ids = {v["id"] for v in data["vectors"]}
    assert {"dashboard", "pipeline", "storage", "red-sage"}.issubset(ids)
    for vector in data["vectors"]:
        assert vector["trust_level"] in {"permissive", "tainted", "restricted"}
