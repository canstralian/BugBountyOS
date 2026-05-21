"""Smoke tests for the contracts and registry YAML."""

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_contract_yaml_parses():
    with (REPO_ROOT / "contracts" / "redsage.yaml").open() as f:
        data = yaml.safe_load(f)
    assert isinstance(data, dict), f"YAML file {f.name} should parse into a dictionary. Check if it is still base64-encoded."
    assert "vector_id" in data


def test_vectors_registry_parses():
    with (REPO_ROOT / "control-plane" / "registry" / "vectors.yaml").open() as f:
        data = yaml.safe_load(f)
    assert isinstance(data, dict), "Registry YAML should parse into a dictionary"
    assert "vectors" in data
