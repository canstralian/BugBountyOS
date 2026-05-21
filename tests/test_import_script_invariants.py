"""Invariant checks for import_vectors.sh.

These tests are intentionally focused on durable safety properties of the
import script: shell hardening, default-deny dry-run behavior, and
containment of side effects. They do not assert vector counts, vector
names, or remote URLs — those are expected to evolve as the registry
matures.

Tests should fail when:
- the safety flag `set -euo pipefail` is removed
- the dry-run default flips to executing real git operations
- `git subtree` is invoked without the EXECUTE guard
- the script silently swallows errors
"""
import os
import re
import stat
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "import_vectors.sh"


def _read_script() -> str:
    return SCRIPT_PATH.read_text(encoding="utf-8")


def _run_script(env_override: dict | None = None) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env.setdefault("EXECUTE", "0")
    if env_override:
        env.update(env_override)
    return subprocess.run(
        ["bash", str(SCRIPT_PATH)],
        capture_output=True,
        text=True,
        env=env,
        cwd=str(REPO_ROOT),
        timeout=30,
    )


def test_script_exists_and_readable():
    assert SCRIPT_PATH.is_file(), "import_vectors.sh must exist at repo root"
    mode = SCRIPT_PATH.stat().st_mode
    assert mode & stat.S_IRUSR, "import_vectors.sh must be readable"


def test_script_has_bash_shebang():
    content = _read_script()
    assert content.startswith("#!"), "script must declare an interpreter"
    first_line = content.splitlines()[0]
    assert "bash" in first_line, "script must be a bash script"


def test_script_uses_strict_mode():
    """`set -euo pipefail` is the contract for shell hardening.

    If this is removed, the script silently continues past failures and
    references to unset variables — a regression we want CI to catch.
    """
    content = _read_script()
    assert re.search(r"set\s+-e[a-z]*u[a-z]*o\s+pipefail", content) or re.search(
        r"set\s+-euo\s+pipefail", content
    ), "import_vectors.sh must enable strict mode via `set -euo pipefail`"


def test_execute_defaults_to_dry_run():
    """EXECUTE must default to 0 so the script is safe to run without args."""
    content = _read_script()
    assert re.search(r'EXECUTE=\$\{EXECUTE:-0\}', content), (
        "EXECUTE must default to 0 — running the script with no env must be a dry-run"
    )


def test_git_subtree_is_guarded_by_execute_flag():
    """Every `git subtree` invocation must sit behind the EXECUTE guard.

    We don't pin the exact guard expression, but no `git subtree` line may
    appear at the top level of a control-flow block without `EXECUTE` in
    the same `if`/conditional context.
    """
    content = _read_script()
    # Locate git subtree invocations that are real commands (not echoed/quoted).
    # A real invocation is a line whose first non-whitespace token is `git`.
    real_invocations = [
        line
        for line in content.splitlines()
        if re.match(r"^\s*git\s+subtree\b", line)
    ]
    assert real_invocations, "script should reference git subtree at least once"
    # Walk the script and confirm each real `git subtree` line is inside an
    # `if` block that tests EXECUTE.
    lines = content.splitlines()
    for idx, line in enumerate(lines):
        if not re.match(r"^\s*git\s+subtree\b", line):
            continue
        # Search backwards for the nearest enclosing `if` on the same or
        # lower indentation; that `if` must reference EXECUTE.
        enclosing_if = None
        depth = 0
        for j in range(idx - 1, -1, -1):
            if re.match(r"^\s*fi\b", lines[j]):
                depth += 1
                continue
            if re.match(r"^\s*if\b", lines[j]):
                if depth == 0:
                    enclosing_if = lines[j]
                    break
                depth -= 1
        assert enclosing_if is not None, (
            f"git subtree on line {idx + 1} is not inside an `if` block"
        )
        assert "EXECUTE" in enclosing_if, (
            f"git subtree on line {idx + 1} is not guarded by an EXECUTE check; "
            f"enclosing if was: {enclosing_if.strip()!r}"
        )


def test_dry_run_exits_zero():
    """With EXECUTE=0, the script must complete successfully on a clean run."""
    result = _run_script({"EXECUTE": "0"})
    assert result.returncode == 0, (
        f"dry-run exited {result.returncode}; stderr={result.stderr!r}"
    )


def test_dry_run_emits_dry_run_marker():
    """Output must clearly indicate dry-run mode to the operator."""
    result = _run_script({"EXECUTE": "0"})
    assert "DRY-RUN" in result.stdout or "dry-run" in result.stdout.lower(), (
        "dry-run output must contain a DRY-RUN marker so operators can tell "
        "real runs from rehearsals"
    )


def test_dry_run_does_not_mutate_working_tree():
    """A dry-run must not create or delete files in vectors/ or anywhere else."""
    before = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
        check=True,
    ).stdout
    _run_script({"EXECUTE": "0"})
    after = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
        check=True,
    ).stdout
    assert before == after, (
        "dry-run modified the working tree — it must be a no-op on disk"
    )


def test_dry_run_does_not_create_unset_variable_failure():
    """With `set -u`, any reference to an unset variable would crash.

    Run the dry-run with a minimal environment to confirm the script doesn't
    rely on unguarded environment variables that could break in CI.
    """
    result = subprocess.run(
        ["bash", str(SCRIPT_PATH)],
        capture_output=True,
        text=True,
        env={"PATH": os.environ.get("PATH", ""), "EXECUTE": "0"},
        cwd=str(REPO_ROOT),
        timeout=30,
    )
    assert result.returncode == 0, (
        f"dry-run failed under a minimal env (returncode={result.returncode}); "
        f"this usually means an unset variable is being referenced. stderr={result.stderr!r}"
    )
