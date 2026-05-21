"""Invariant checks for the control-plane vector registry.

The registry at control-plane/registry/vectors.yaml is base64-encoded on
disk (see CLAUDE.md). These tests decode it and assert structural
guarantees that the kernel/control-plane relies on, without pinning
specific vector IDs, counts, or per-vector state values that may evolve.

Tests should fail when:
- the registry file becomes unreadable or non-base64
- decoded content is not valid YAML
- the top-level `vectors` list is missing
- any vector entry is missing a required field
- vector IDs collide or use an unrecognised lifecycle/trust value

Tests should NOT fail when:
- vectors are added or removed
- a vector legitimately changes its state, trust_level, or contract_version
- a new optional field is added
"""
import base64
import re
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = REPO_ROOT / "control-plane" / "registry" / "vectors.yaml"

# Required fields per vector. These are part of the control-plane contract;
# loss of any one breaks routing, policy, or audit. Adding a new required
# field here is a deliberate schema change.
REQUIRED_VECTOR_FIELDS = {
    "id",
    "role",
    "state",
    "trust_level",
    "source_repo",
    "contract_version",
}

# Recognised lifecycle states from docs/ARCHITECTURE.md.
ALLOWED_STATES = {"importing", "active", "canonical", "quarantined", "pending"}

# Recognised trust levels — kept permissive intentionally so additions
# (e.g. "trusted", "untrusted", "tainted") don't break this suite, but
# values must at least be non-empty strings drawn from the known set.
ALLOWED_TRUST_LEVELS = {"permissive", "trusted", "tainted", "restricted", "untrusted"}


def _decode_registry() -> dict:
    raw = REGISTRY_PATH.read_bytes()
    # base64 files in this repo contain embedded newlines; b64decode without
    # validate=True tolerates them. Empty/garbled content surfaces as an
    # empty YAML load below, which the downstream assertions catch.
    try:
        decoded = base64.b64decode(raw)
        return yaml.safe_load(decoded)
    except (yaml.YAMLError, Exception) as exc:  # noqa: BLE001 — surface decode errors verbatim
        raise AssertionError(
            f"registry file is not valid base64 or YAML: {exc}"
        ) from exc


def test_registry_file_exists_and_nonempty():
    assert REGISTRY_PATH.is_file(), "vectors.yaml must exist"
    assert REGISTRY_PATH.stat().st_size > 0, "vectors.yaml must not be empty"


def test_registry_is_valid_base64_yaml():
    """File must decode from base64 and parse as YAML — the on-disk contract."""
    data = _decode_registry()
    assert data is not None, "decoded registry must not be empty"
    assert isinstance(data, dict), "decoded registry must be a YAML mapping"


def test_registry_has_vectors_list():
    data = _decode_registry()
    assert "vectors" in data, "registry must have a top-level `vectors` key"
    assert isinstance(data["vectors"], list), "`vectors` must be a list"


def test_every_vector_has_required_fields():
    """Each entry must carry the full control-plane field set."""
    data = _decode_registry()
    for entry in data["vectors"]:
        assert isinstance(entry, dict), f"vector entry must be a mapping: {entry!r}"
        missing = REQUIRED_VECTOR_FIELDS - set(entry.keys())
        assert not missing, (
            f"vector {entry.get('id', '<no-id>')!r} is missing required fields: {sorted(missing)}"
        )


def test_vector_ids_are_unique():
    data = _decode_registry()
    ids = [entry["id"] for entry in data["vectors"]]
    duplicates = {vid for vid in ids if ids.count(vid) > 1}
    assert not duplicates, f"duplicate vector ids in registry: {sorted(duplicates)}"


def test_vector_ids_are_nonempty_strings():
    data = _decode_registry()
    for entry in data["vectors"]:
        vid = entry["id"]
        assert isinstance(vid, str) and vid.strip(), (
            f"vector id must be a non-empty string, got: {vid!r}"
        )


def test_vector_states_are_recognised():
    data = _decode_registry()
    for entry in data["vectors"]:
        state = entry["state"]
        assert state in ALLOWED_STATES, (
            f"vector {entry['id']!r} has unrecognised state {state!r}; "
            f"allowed: {sorted(ALLOWED_STATES)}"
        )


def test_vector_trust_levels_are_recognised():
    data = _decode_registry()
    for entry in data["vectors"]:
        trust = entry["trust_level"]
        assert trust in ALLOWED_TRUST_LEVELS, (
            f"vector {entry['id']!r} has unrecognised trust_level {trust!r}; "
            f"allowed: {sorted(ALLOWED_TRUST_LEVELS)}"
        )


def test_source_repo_follows_owner_repo_pattern():
    """`source_repo` is canonical (see CLAUDE.md); enforce `owner/repo` shape."""
    pattern = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*/[A-Za-z0-9][A-Za-z0-9_.-]*$")
    data = _decode_registry()
    for entry in data["vectors"]:
        source = entry["source_repo"]
        assert isinstance(source, str), (
            f"vector {entry['id']!r} source_repo must be a string"
        )
        assert pattern.match(source), (
            f"vector {entry['id']!r} source_repo {source!r} must match owner/repo"
        )


def test_contract_version_is_non_negative_integer():
    data = _decode_registry()
    for entry in data["vectors"]:
        version = entry["contract_version"]
        assert isinstance(version, int), (
            f"vector {entry['id']!r} contract_version must be an integer, "
            f"got {type(version).__name__}"
        )
        assert version >= 0, (
            f"vector {entry['id']!r} contract_version must be non-negative, got {version}"
        )


def test_roles_are_nonempty_strings():
    data = _decode_registry()
    for entry in data["vectors"]:
        role = entry["role"]
        assert isinstance(role, str) and role.strip(), (
            f"vector {entry['id']!r} role must be a non-empty string, got {role!r}"
        )
