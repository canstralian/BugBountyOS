"""
tests/test_config_structure.py — Structure validation for new config files.

Covers:
  - pyproject.toml           (new file: ruff + mypy configuration)
  - .pre-commit-config.yaml  (new file: pre-commit hooks)
  - .github/workflows/ci.yml (changed: removed ruff lint step from CI)
  - .github/workflows/lint.yml (changed: added ruff format + mypy steps)
"""

import os
import sys
import tomllib
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

REPO_ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# pyproject.toml
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def pyproject() -> dict:
    path = REPO_ROOT / "pyproject.toml"
    with open(path, "rb") as f:
        return tomllib.load(f)


class TestPyprojectExists:
    def test_file_present(self):
        assert (REPO_ROOT / "pyproject.toml").is_file()

    def test_file_nonempty(self):
        assert (REPO_ROOT / "pyproject.toml").stat().st_size > 0

    def test_file_is_valid_toml(self, pyproject):
        assert isinstance(pyproject, dict)


class TestPyprojectRuffSection:
    def test_has_tool_ruff(self, pyproject):
        assert "tool" in pyproject
        assert "ruff" in pyproject["tool"]

    def test_line_length_is_100(self, pyproject):
        assert pyproject["tool"]["ruff"]["line-length"] == 100

    def test_target_version_is_py312(self, pyproject):
        assert pyproject["tool"]["ruff"]["target-version"] == "py312"

    def test_exclude_list_contains_git(self, pyproject):
        excludes = pyproject["tool"]["ruff"]["exclude"]
        assert ".git" in excludes

    def test_exclude_list_contains_venv(self, pyproject):
        excludes = pyproject["tool"]["ruff"]["exclude"]
        assert ".venv" in excludes

    def test_exclude_list_contains_dist(self, pyproject):
        excludes = pyproject["tool"]["ruff"]["exclude"]
        assert "dist" in excludes

    def test_exclude_list_contains_build(self, pyproject):
        excludes = pyproject["tool"]["ruff"]["exclude"]
        assert "build" in excludes


class TestPyprojectRuffLintSection:
    def test_has_ruff_lint(self, pyproject):
        assert "lint" in pyproject["tool"]["ruff"]

    def test_select_contains_e(self, pyproject):
        assert "E" in pyproject["tool"]["ruff"]["lint"]["select"]

    def test_select_contains_f(self, pyproject):
        assert "F" in pyproject["tool"]["ruff"]["lint"]["select"]

    def test_select_contains_b(self, pyproject):
        assert "B" in pyproject["tool"]["ruff"]["lint"]["select"]

    def test_select_contains_sim(self, pyproject):
        assert "SIM" in pyproject["tool"]["ruff"]["lint"]["select"]

    def test_ignore_contains_e501(self, pyproject):
        assert "E501" in pyproject["tool"]["ruff"]["lint"]["ignore"]

    def test_ignore_only_contains_e501(self, pyproject):
        """pyproject.toml ignore list contains exactly E501 (not B008 or others)."""
        ignore = pyproject["tool"]["ruff"]["lint"]["ignore"]
        assert ignore == ["E501"]


class TestPyprojectRuffFormatSection:
    def test_has_ruff_format(self, pyproject):
        assert "format" in pyproject["tool"]["ruff"]

    def test_quote_style_is_double(self, pyproject):
        assert pyproject["tool"]["ruff"]["format"]["quote-style"] == "double"

    def test_indent_style_is_space(self, pyproject):
        assert pyproject["tool"]["ruff"]["format"]["indent-style"] == "space"


class TestPyprojectMypySection:
    def test_has_tool_mypy(self, pyproject):
        assert "mypy" in pyproject["tool"]

    def test_python_version_is_312(self, pyproject):
        assert pyproject["tool"]["mypy"]["python_version"] == "3.12"

    def test_warn_unused_configs_enabled(self, pyproject):
        assert pyproject["tool"]["mypy"]["warn_unused_configs"] is True

    def test_disallow_untyped_defs_disabled(self, pyproject):
        assert pyproject["tool"]["mypy"]["disallow_untyped_defs"] is False

    def test_check_untyped_defs_enabled(self, pyproject):
        assert pyproject["tool"]["mypy"]["check_untyped_defs"] is True

    def test_ignore_missing_imports_enabled(self, pyproject):
        assert pyproject["tool"]["mypy"]["ignore_missing_imports"] is True

    def test_mypy_exclude_contains_git(self, pyproject):
        excludes = pyproject["tool"]["mypy"]["exclude"]
        assert any(".git" in e for e in excludes)

    def test_mypy_exclude_contains_venv(self, pyproject):
        excludes = pyproject["tool"]["mypy"]["exclude"]
        assert any(".venv" in e for e in excludes)


# ---------------------------------------------------------------------------
# .pre-commit-config.yaml
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def pre_commit_config() -> dict:
    path = REPO_ROOT / ".pre-commit-config.yaml"
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


class TestPreCommitConfigExists:
    def test_file_present(self):
        assert (REPO_ROOT / ".pre-commit-config.yaml").is_file()

    def test_file_nonempty(self):
        assert (REPO_ROOT / ".pre-commit-config.yaml").stat().st_size > 0

    def test_is_valid_yaml(self, pre_commit_config):
        assert isinstance(pre_commit_config, dict)


class TestPreCommitRuffRepo:
    def test_has_repos_key(self, pre_commit_config):
        assert "repos" in pre_commit_config

    def test_repos_is_list(self, pre_commit_config):
        assert isinstance(pre_commit_config["repos"], list)

    def test_ruff_repo_present(self, pre_commit_config):
        repos = pre_commit_config["repos"]
        repo_urls = [r["repo"] for r in repos]
        assert any("ruff" in url for url in repo_urls)

    def test_ruff_repo_revision(self, pre_commit_config):
        repos = pre_commit_config["repos"]
        ruff_repo = next(r for r in repos if "ruff" in r["repo"])
        assert ruff_repo["rev"] == "v0.15.1"

    def test_ruff_check_hook_present(self, pre_commit_config):
        repos = pre_commit_config["repos"]
        ruff_repo = next(r for r in repos if "ruff" in r["repo"])
        hook_ids = [h["id"] for h in ruff_repo["hooks"]]
        assert "ruff-check" in hook_ids

    def test_ruff_format_hook_present(self, pre_commit_config):
        repos = pre_commit_config["repos"]
        ruff_repo = next(r for r in repos if "ruff" in r["repo"])
        hook_ids = [h["id"] for h in ruff_repo["hooks"]]
        assert "ruff-format" in hook_ids

    def test_ruff_check_has_fix_arg(self, pre_commit_config):
        repos = pre_commit_config["repos"]
        ruff_repo = next(r for r in repos if "ruff" in r["repo"])
        ruff_check = next(h for h in ruff_repo["hooks"] if h["id"] == "ruff-check")
        assert "--fix" in ruff_check.get("args", [])

    def test_ruff_check_excludes_dist(self, pre_commit_config):
        repos = pre_commit_config["repos"]
        ruff_repo = next(r for r in repos if "ruff" in r["repo"])
        ruff_check = next(h for h in ruff_repo["hooks"] if h["id"] == "ruff-check")
        assert "dist" in ruff_check.get("exclude", "")

    def test_ruff_format_excludes_build(self, pre_commit_config):
        repos = pre_commit_config["repos"]
        ruff_repo = next(r for r in repos if "ruff" in r["repo"])
        ruff_format = next(h for h in ruff_repo["hooks"] if h["id"] == "ruff-format")
        assert "build" in ruff_format.get("exclude", "")


class TestPreCommitStandardHooks:
    def test_pre_commit_hooks_repo_present(self, pre_commit_config):
        repos = pre_commit_config["repos"]
        repo_urls = [r["repo"] for r in repos]
        assert any("pre-commit-hooks" in url for url in repo_urls)

    def test_pre_commit_hooks_revision(self, pre_commit_config):
        repos = pre_commit_config["repos"]
        hooks_repo = next(r for r in repos if "pre-commit-hooks" in r["repo"])
        assert hooks_repo["rev"] == "v5.0.0"

    def test_check_yaml_hook_present(self, pre_commit_config):
        repos = pre_commit_config["repos"]
        hooks_repo = next(r for r in repos if "pre-commit-hooks" in r["repo"])
        hook_ids = [h["id"] for h in hooks_repo["hooks"]]
        assert "check-yaml" in hook_ids

    def test_end_of_file_fixer_hook_present(self, pre_commit_config):
        repos = pre_commit_config["repos"]
        hooks_repo = next(r for r in repos if "pre-commit-hooks" in r["repo"])
        hook_ids = [h["id"] for h in hooks_repo["hooks"]]
        assert "end-of-file-fixer" in hook_ids

    def test_trailing_whitespace_hook_present(self, pre_commit_config):
        repos = pre_commit_config["repos"]
        hooks_repo = next(r for r in repos if "pre-commit-hooks" in r["repo"])
        hook_ids = [h["id"] for h in hooks_repo["hooks"]]
        assert "trailing-whitespace" in hook_ids

    def test_exactly_two_repos(self, pre_commit_config):
        assert len(pre_commit_config["repos"]) == 2


# ---------------------------------------------------------------------------
# .github/workflows/ci.yml
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def ci_workflow() -> dict:
    path = REPO_ROOT / ".github" / "workflows" / "ci.yml"
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


class TestCiWorkflowExists:
    def test_file_present(self):
        assert (REPO_ROOT / ".github" / "workflows" / "ci.yml").is_file()

    def test_is_valid_yaml(self, ci_workflow):
        assert isinstance(ci_workflow, dict)


class TestCiWorkflowStructure:
    def test_workflow_name_is_ci(self, ci_workflow):
        assert ci_workflow["name"] == "CI"

    def test_triggers_on_push(self, ci_workflow):
        assert "push" in ci_workflow["on"]

    def test_triggers_on_pull_request(self, ci_workflow):
        assert "pull_request" in ci_workflow["on"]

    def test_triggers_on_main_branch(self, ci_workflow):
        assert "main" in ci_workflow["on"]["push"]["branches"]

    def test_triggers_on_develop_branch(self, ci_workflow):
        assert "develop" in ci_workflow["on"]["push"]["branches"]

    def test_has_ci_job(self, ci_workflow):
        assert "ci" in ci_workflow["jobs"]

    def test_runs_on_ubuntu_latest(self, ci_workflow):
        assert ci_workflow["jobs"]["ci"]["runs-on"] == "ubuntu-latest"


class TestCiWorkflowSteps:
    def _get_step_names(self, ci_workflow: dict) -> list:
        return [s.get("name", "") for s in ci_workflow["jobs"]["ci"]["steps"]]

    def test_has_checkout_step(self, ci_workflow):
        step_names = self._get_step_names(ci_workflow)
        assert any("Checkout" in n for n in step_names)

    def test_has_python_setup_step(self, ci_workflow):
        step_names = self._get_step_names(ci_workflow)
        assert any("Python" in n for n in step_names)

    def test_has_run_tests_step(self, ci_workflow):
        step_names = self._get_step_names(ci_workflow)
        assert any("test" in n.lower() or "Test" in n for n in step_names)

    def test_no_ruff_lint_step(self, ci_workflow):
        """Ruff linting was removed from CI in this PR and moved to lint.yml."""
        step_names = self._get_step_names(ci_workflow)
        assert not any("Lint Python" in n for n in step_names)

    def test_pytest_installed_not_ruff(self, ci_workflow):
        """After this PR, ruff is no longer installed in CI; only pytest and pyyaml."""
        steps = ci_workflow["jobs"]["ci"]["steps"]
        install_step = next(
            (s for s in steps if s.get("name", "") == "Install Python dependencies"), None
        )
        assert install_step is not None
        run_cmd = install_step["run"]
        assert "pytest" in run_cmd
        assert "ruff" not in run_cmd

    def test_has_shellcheck_step(self, ci_workflow):
        step_names = self._get_step_names(ci_workflow)
        assert any("shell" in n.lower() or "Shell" in n for n in step_names)


# ---------------------------------------------------------------------------
# .github/workflows/lint.yml
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def lint_workflow() -> dict:
    path = REPO_ROOT / ".github" / "workflows" / "lint.yml"
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


class TestLintWorkflowExists:
    def test_file_present(self):
        assert (REPO_ROOT / ".github" / "workflows" / "lint.yml").is_file()

    def test_is_valid_yaml(self, lint_workflow):
        assert isinstance(lint_workflow, dict)


class TestLintWorkflowStructure:
    def test_workflow_name_is_lint(self, lint_workflow):
        assert lint_workflow["name"] == "Lint"

    def test_triggers_on_main_branch(self, lint_workflow):
        assert "main" in lint_workflow["on"]["push"]["branches"]

    def test_has_lint_job(self, lint_workflow):
        assert "lint" in lint_workflow["jobs"]

    def test_runs_on_ubuntu_latest(self, lint_workflow):
        assert lint_workflow["jobs"]["lint"]["runs-on"] == "ubuntu-latest"


class TestLintWorkflowSteps:
    def _get_step_names(self, lint_workflow: dict) -> list:
        return [s.get("name", "") for s in lint_workflow["jobs"]["lint"]["steps"]]

    def _get_step_run(self, lint_workflow: dict, step_name: str) -> str:
        steps = lint_workflow["jobs"]["lint"]["steps"]
        step = next((s for s in steps if s.get("name", "") == step_name), None)
        return step["run"] if step else ""

    def test_has_ruff_lint_step(self, lint_workflow):
        step_names = self._get_step_names(lint_workflow)
        assert any("Ruff" in n and "lint" in n.lower() for n in step_names)

    def test_has_ruff_format_step(self, lint_workflow):
        """Ruff format --check was added in this PR."""
        step_names = self._get_step_names(lint_workflow)
        assert any("Ruff" in n and "format" in n.lower() for n in step_names)

    def test_has_mypy_step(self, lint_workflow):
        """Mypy was added in this PR."""
        step_names = self._get_step_names(lint_workflow)
        assert any("Mypy" in n or "mypy" in n for n in step_names)

    def test_has_shellcheck_step(self, lint_workflow):
        step_names = self._get_step_names(lint_workflow)
        assert any("ShellCheck" in n or "shellcheck" in n for n in step_names)

    def test_ruff_lint_runs_check(self, lint_workflow):
        run_cmd = self._get_step_run(lint_workflow, "Ruff lint")
        assert "ruff check" in run_cmd

    def test_ruff_format_runs_check_flag(self, lint_workflow):
        """ruff format --check is the new non-mutating format verification step."""
        run_cmd = self._get_step_run(lint_workflow, "Ruff format")
        assert "ruff format" in run_cmd
        assert "--check" in run_cmd

    def test_mypy_uses_explicit_package_bases(self, lint_workflow):
        run_cmd = self._get_step_run(lint_workflow, "Mypy")
        assert "mypy" in run_cmd
        assert "--explicit-package-bases" in run_cmd

    def test_mypy_and_ruff_installed_in_lint_deps(self, lint_workflow):
        steps = lint_workflow["jobs"]["lint"]["steps"]
        install_step = next(
            (s for s in steps if s.get("name", "") == "Install lint dependencies"), None
        )
        assert install_step is not None
        run_cmd = install_step["run"]
        assert "ruff" in run_cmd
        assert "mypy" in run_cmd
