"""Smoke tests for repository structure.

These are minimal placeholders so pytest collects at least one test and the
`tests` workflow exits 0. Real test suites live in vector-specific subtrees.
"""
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
