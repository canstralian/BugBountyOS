"""Smoke tests for repository structure.

These are minimal placeholders so pytest collects at least one test and the
`tests` workflow exits 0. Real test suites live in vector-specific subtrees.
"""
import base64
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_readme_present_and_nonempty():
    readme = REPO_ROOT / "README.md"
    assert readme.is_file(), "README.md should exist at repo root"
    assert readme.stat().st_size > 0, "README.md should not be empty"


def test_license_is_mit():
    license_path = REPO_ROOT / "LICENSE"
    assert license_path.is_file()
    assert "MIT" in license_path.read_text(encoding="utf-8")


def test_workflow_directories_exist():
    for required in ("adapters", "contracts", "docs", "kernel", "vectors"):
        assert (REPO_ROOT / required).is_dir(), f"{required}/ should exist"


def test_adrian_watchdog_wired():
    """Adrian watchdog vector must be registered with a contract and adapter."""
    contract = REPO_ROOT / "contracts" / "adrian.yaml"
    assert contract.is_file(), "contracts/adrian.yaml must exist"
    contract_plain = base64.b64decode(contract.read_bytes()).decode("utf-8")
    assert "vector_id: adrian" in contract_plain
    assert "role: watchdog" in contract_plain
    assert "coverage: universal" in contract_plain

    registry = REPO_ROOT / "control-plane" / "registry" / "vectors.yaml"
    registry_plain = base64.b64decode(registry.read_bytes()).decode("utf-8")
    assert "id: adrian" in registry_plain
    assert "secureagentics/Adrian" in registry_plain

    adapter = REPO_ROOT / "adapters" / "adrian" / "watchdog_client.py"
    assert adapter.is_file(), "adapters/adrian/watchdog_client.py must exist"

    import_script = (REPO_ROOT / "import_vectors.sh").read_text(encoding="utf-8")
    assert "adrian:https://github.com/secureagentics/Adrian" in import_script
