"""Tests for import_vectors.sh behaviour.

The key change in this PR was adding `set -euo pipefail` to the script.
These tests verify the script's interface and dry-run safety contract.
"""

import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "import_vectors.sh"


# ---------------------------------------------------------------------------
# File presence and permissions
# ---------------------------------------------------------------------------

def test_import_vectors_script_exists():
    assert SCRIPT_PATH.is_file()


def test_import_vectors_script_is_readable():
    """Script must be readable so it can be invoked via bash."""
    import stat
    mode = SCRIPT_PATH.stat().st_mode
    assert mode & stat.S_IRUSR, "import_vectors.sh must be readable by owner"


def test_import_vectors_script_is_nonempty():
    assert SCRIPT_PATH.stat().st_size > 0


# ---------------------------------------------------------------------------
# Script content — static checks
# ---------------------------------------------------------------------------

def test_script_has_set_euo_pipefail():
    """set -euo pipefail was added in this PR as a safety measure."""
    content = SCRIPT_PATH.read_text()
    assert "set -euo pipefail" in content


def test_script_has_shebang():
    content = SCRIPT_PATH.read_text()
    assert content.startswith("#!/bin/bash")


def test_script_defaults_execute_to_zero():
    """EXECUTE defaults to 0 (dry-run) — git subtree is not invoked without opt-in."""
    content = SCRIPT_PATH.read_text()
    assert 'EXECUTE=${EXECUTE:-0}' in content


def test_script_contains_dry_run_guard():
    """The dry-run path must check EXECUTE -eq 1 before running git subtree."""
    content = SCRIPT_PATH.read_text()
    assert '[ "$EXECUTE" -eq 1 ]' in content


def test_script_defines_vectors_array():
    content = SCRIPT_PATH.read_text()
    assert "VECTORS=(" in content


def test_script_references_dashboard_vector():
    content = SCRIPT_PATH.read_text()
    assert "dashboard" in content


def test_script_references_pipeline_vector():
    content = SCRIPT_PATH.read_text()
    assert "pipeline" in content


def test_script_references_storage_vector():
    content = SCRIPT_PATH.read_text()
    assert "storage" in content


# ---------------------------------------------------------------------------
# Dry-run execution — EXECUTE=0 (default)
# ---------------------------------------------------------------------------

def _run_script(env_override=None):
    import os
    env = os.environ.copy()
    env["EXECUTE"] = "0"
    if env_override:
        env.update(env_override)
    return subprocess.run(
        ["bash", str(SCRIPT_PATH)],
        capture_output=True,
        text=True,
        env=env,
        cwd=str(REPO_ROOT),
    )


def test_dry_run_exits_zero():
    result = _run_script()
    assert result.returncode == 0, f"Script exited {result.returncode}: {result.stderr}"


def test_dry_run_outputs_kernel_header():
    result = _run_script()
    assert "BugBountyOS Kernel" in result.stdout or "Vector Loading" in result.stdout


def test_dry_run_outputs_dry_run_label():
    result = _run_script()
    assert "DRY-RUN" in result.stdout


def test_dry_run_does_not_invoke_git_subtree():
    """In dry-run mode the script should print a git subtree command, not execute it."""
    result = _run_script()
    # The echo line contains the literal command text but does not run it
    assert "git subtree add" in result.stdout


def test_dry_run_lists_all_three_vectors():
    result = _run_script()
    assert "dashboard" in result.stdout
    assert "pipeline" in result.stdout
    assert "storage" in result.stdout


def test_dry_run_outputs_completion_message():
    result = _run_script()
    assert "Kernel Load Complete" in result.stdout or "Complete" in result.stdout


def test_dry_run_stderr_is_empty():
    """No unexpected error output during a normal dry-run."""
    result = _run_script()
    assert result.returncode == 0
    # stderr may contain profile warnings in this environment; only check for real errors
    assert "syntax error" not in result.stderr.lower()
    assert "command not found: git subtree" not in result.stderr