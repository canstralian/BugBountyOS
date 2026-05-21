"""Tests for import_vectors.sh behaviour and dry-run safety contract."""

import os
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "import_vectors.sh"


def test_script_exists():
    assert SCRIPT_PATH.is_file()


def test_script_has_shebang():
    assert SCRIPT_PATH.read_text().startswith("#!/bin/bash")


def test_script_uses_set_euo_pipefail():
    assert "set -euo pipefail" in SCRIPT_PATH.read_text()


def test_script_defaults_execute_to_zero():
    assert "EXECUTE=${EXECUTE:-0}" in SCRIPT_PATH.read_text()


def test_dry_run_guard_dereferences_execute_variable():
    # Regression: previously `[ "EXECUTE" -eq 1 ]` (literal) made the EXECUTE=1 path unreachable.
    assert '[ "$EXECUTE" -eq 1 ]' in SCRIPT_PATH.read_text()


def _run_script(execute="0"):
    env = os.environ.copy()
    env["EXECUTE"] = execute
    return subprocess.run(
        ["bash", str(SCRIPT_PATH)],
        capture_output=True,
        text=True,
        env=env,
        cwd=str(REPO_ROOT),
    )


def test_dry_run_exits_zero():
    result = _run_script()
    assert result.returncode == 0, result.stderr


def test_dry_run_emits_dry_run_label():
    assert "DRY-RUN" in _run_script().stdout


def test_dry_run_lists_all_three_vectors():
    stdout = _run_script().stdout
    assert "dashboard" in stdout
    assert "pipeline" in stdout
    assert "storage" in stdout


def test_dry_run_extracts_full_url_not_name_prefix():
    """Regression: `${entry#:*}` extracted the full entry instead of the URL."""
    stdout = _run_script().stdout
    assert "https://github.com/canstralian/BugBountyBot" in stdout
    assert "dashboard:https://github.com" not in stdout


def test_dry_run_completes_cleanly():
    assert "Kernel Load Complete" in _run_script().stdout
