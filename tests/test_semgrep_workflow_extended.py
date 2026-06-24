"""
tests/test_semgrep_workflow_extended.py — Extended tests for the Semgrep CI workflow.

Supplements tests/test_semgrep_workflow.py with additional boundary, negative,
and precision tests not covered by the primary suite.

Covers:
  - Unusual filename (space in filename) regression
  - Exact `if` condition syntax on upload steps
  - Unconditional execution of checkout and scan steps
  - Negative: dangerous/suppressing flags must NOT appear in scan command
  - Exact artifact name prefix
  - Exact `runs-on` value and container image tag
  - Checkout step has no `with:` parameters
  - Retention days is an integer (not a string)
  - Raw file content assertions
  - Top-level YAML has only the expected key
  - Separate --sarif and --sarif-output flags both present
  - SARIF upload `with:` params limited to expected keys
"""

import re
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "semgrep-ci. yml"

SARIF_FILENAME = "semgrep-results.sarif"
EXPECTED_IF_CONDITION = f"always() && hashFiles('{SARIF_FILENAME}') != ''"


@pytest.fixture(scope="module")
def workflow_raw():
    """
    Return the workflow file contents as raw UTF-8 text.
    
    Returns:
        str: The workflow file content.
    """
    assert WORKFLOW_PATH.is_file(), f"Workflow file not found: {WORKFLOW_PATH}"
    return WORKFLOW_PATH.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def workflow_yaml(workflow_raw):
    """
    Parse the workflow file into a YAML object.
    
    Parameters:
    	workflow_raw: Raw workflow file contents.
    
    Returns:
    	Parsed workflow YAML.
    """
    return yaml.safe_load(workflow_raw)


@pytest.fixture(scope="module")
def job(workflow_yaml):
    """Return the semgrep job definition."""
    return workflow_yaml["semgrep"]


@pytest.fixture(scope="module")
def steps(job):
    """Extract the workflow steps from the Semgrep job.
    
    Parameters:
    	job: Parsed YAML for the `semgrep` job.
    
    Returns:
    	list: The job's `steps` list.
    """
    return job["steps"]


# ---------------------------------------------------------------------------
# Filename regression: space in filename
# ---------------------------------------------------------------------------

class TestWorkflowFilenameWithSpace:
    def test_workflow_filename_contains_a_space(self):
        """Regression: the file intentionally has a space in its name ('semgrep-ci. yml')."""
        assert " " in WORKFLOW_PATH.name, (
            f"Workflow filename '{WORKFLOW_PATH.name}' must contain a space character "
            "as per the project's naming convention for this file"
        )

    def test_workflow_filename_has_yml_extension(self):
        assert WORKFLOW_PATH.suffix == ".yml", (
            f"Workflow file must have .yml extension, got: '{WORKFLOW_PATH.suffix}'"
        )

    def test_workflow_parent_directory_is_workflows(self):
        assert WORKFLOW_PATH.parent.name == "workflows", (
            "Workflow file must be inside the 'workflows' directory"
        )

    def test_workflow_grandparent_directory_is_github(self):
        assert WORKFLOW_PATH.parent.parent.name == ".github", (
            "Workflow file must be inside '.github/workflows/'"
        )


# ---------------------------------------------------------------------------
# Raw content assertions
# ---------------------------------------------------------------------------

class TestRawFileContent:
    def test_raw_content_contains_semgrep_scan_invocation(self, workflow_raw):
        assert "semgrep scan" in workflow_raw, (
            "Raw file must contain 'semgrep scan' invocation"
        )

    def test_raw_content_contains_sarif_output_flag(self, workflow_raw):
        assert f"--sarif-output={SARIF_FILENAME}" in workflow_raw, (
            f"Raw file must contain '--sarif-output={SARIF_FILENAME}'"
        )

    def test_raw_content_contains_error_flag(self, workflow_raw):
        assert "--error" in workflow_raw, (
            "Raw file must contain '--error' flag"
        )

    def test_raw_content_contains_always_condition(self, workflow_raw):
        assert "always()" in workflow_raw, (
            "Raw file must contain 'always()' condition for upload steps"
        )

    def test_raw_content_references_sarif_filename_multiple_times(self, workflow_raw):
        """SARIF filename must appear in scan output, sarif_file param, artifact path, and if conditions."""
        count = workflow_raw.count(SARIF_FILENAME)
        assert count >= 4, (
            f"'{SARIF_FILENAME}' should appear at least 4 times in the workflow "
            f"(scan output, sarif_file, artifact path, two if conditions); found {count}"
        )


# ---------------------------------------------------------------------------
# Exact `if` condition syntax on upload steps
# ---------------------------------------------------------------------------

class TestExactIfConditionSyntax:
    def test_sarif_upload_if_condition_exact_syntax(self, steps):
        """Step 3 must use the exact if-condition that checks file existence."""
        step_if = str(steps[2].get("if", ""))
        assert "always()" in step_if, "SARIF upload step must include always()"
        assert "hashFiles" in step_if, "SARIF upload step must include hashFiles()"
        assert SARIF_FILENAME in step_if, f"SARIF upload step if must reference '{SARIF_FILENAME}'"
        assert "!= ''" in step_if or '!= ""' in step_if, (
            "SARIF upload step if condition must check hashFiles result is non-empty"
        )

    def test_artifact_upload_if_condition_exact_syntax(self, steps):
        """Assert that the artifact upload step uses the expected file-existence condition."""
        step_if = str(steps[3].get("if", ""))
        assert "always()" in step_if, "Artifact upload step must include always()"
        assert "hashFiles" in step_if, "Artifact upload step must include hashFiles()"
        assert SARIF_FILENAME in step_if, f"Artifact upload step if must reference '{SARIF_FILENAME}'"
        assert "!= ''" in step_if or '!= ""' in step_if, (
            "Artifact upload step if condition must check hashFiles result is non-empty"
        )

    def test_upload_steps_use_and_operator_in_condition(self, steps):
        """The if condition must combine always() and hashFiles() with &&."""
        for i in (2, 3):
            step_if = str(steps[i].get("if", ""))
            assert "&&" in step_if, (
                f"Step {i} if condition must use '&&' to combine always() and hashFiles(); "
                f"got: '{step_if}'"
            )


# ---------------------------------------------------------------------------
# Unconditional execution of checkout and scan steps
# ---------------------------------------------------------------------------

class TestUnconditionalSteps:
    def test_checkout_step_has_no_if_condition(self, steps):
        """Checkout must run unconditionally — no 'if:' guard."""
        assert "if" not in steps[0], (
            "Checkout step must not have an 'if' condition; it must always run"
        )

    def test_scan_step_has_no_if_condition(self, steps):
        """Scan must run unconditionally — no 'if:' guard."""
        assert "if" not in steps[1], (
            "Semgrep scan step must not have an 'if' condition; it must always run"
        )


# ---------------------------------------------------------------------------
# Negative: dangerous or suppressing flags must NOT appear in scan command
# ---------------------------------------------------------------------------

class TestNegativeScanFlags:
    def test_no_error_flag_is_absent(self, steps):
        """--no-error would silence findings and allow a vulnerable codebase to pass CI."""
        run_cmd = steps[1]["run"]
        assert "--no-error" not in run_cmd, (
            "'--no-error' must NOT be present; it disables the exit-code enforcement "
            "that blocks CI when Semgrep finds security issues"
        )

    def test_quiet_flag_is_absent(self, steps):
        """--quiet or -q suppresses scan output, making findings invisible in CI logs."""
        run_cmd = steps[1]["run"]
        assert "--quiet" not in run_cmd, (
            "'--quiet' must NOT be present; it suppresses Semgrep output in CI logs"
        )
        assert " -q " not in run_cmd and not run_cmd.strip().endswith(" -q"), (
            "'-q' shorthand must NOT be present; it suppresses Semgrep output"
        )

    def test_dry_run_flag_is_absent(self, steps):
        """--dry-run would prevent actual scanning from occurring."""
        run_cmd = steps[1]["run"]
        assert "--dry-run" not in run_cmd, (
            "'--dry-run' must NOT be present in the production scan command"
        )

    def test_exclude_all_flag_is_absent(self, steps):
        """--exclude=* or broad excludes could silently skip all files."""
        run_cmd = steps[1]["run"]
        assert "--exclude=*" not in run_cmd and "--exclude '*'" not in run_cmd, (
            "Broad --exclude patterns must not be present as they could skip all files"
        )

    def test_allow_untrusted_validators_flag_is_absent(self, steps):
        """Scan must not disable validation-related safety checks."""
        run_cmd = steps[1]["run"]
        assert "--allow-untrusted-validators" not in run_cmd, (
            "'--allow-untrusted-validators' must not be used in production CI scans"
        )


# ---------------------------------------------------------------------------
# Exact runner and container image
# ---------------------------------------------------------------------------

class TestExactRunnerAndImage:
    def test_runs_on_is_exactly_ubuntu_latest(self, job):
        """Runner must be exactly 'ubuntu-latest', not a pinned version or other distro."""
        assert job["runs-on"] == "ubuntu-latest", (
            f"'runs-on' must be exactly 'ubuntu-latest', got: '{job['runs-on']}'"
        )

    def test_container_image_is_exactly_semgrep_semgrep_latest(self, job):
        """Container image must be exactly 'semgrep/semgrep:latest'."""
        image = job["container"]["image"]
        assert image == "semgrep/semgrep:latest", (
            f"Container image must be exactly 'semgrep/semgrep:latest', got: '{image}'"
        )

    def test_container_has_no_extra_keys(self, job):
        """Container block should only specify 'image'; no credentials or volumes."""
        container = job["container"]
        assert set(container.keys()) == {"image"}, (
            f"Container block should only have 'image' key, found: {set(container.keys())}"
        )


# ---------------------------------------------------------------------------
# Checkout step has no `with:` parameters
# ---------------------------------------------------------------------------

class TestCheckoutStepNoExtraParams:
    def test_checkout_step_has_no_with_params(self, steps):
        """Checkout step should not specify 'with:' parameters (no token override, etc.)."""
        assert "with" not in steps[0], (
            "Checkout step must not have 'with' parameters; it should use default settings"
        )

    def test_checkout_step_has_no_env(self, steps):
        """Checkout step should not set environment variables."""
        assert "env" not in steps[0], (
            "Checkout step must not define 'env' overrides"
        )


# ---------------------------------------------------------------------------
# Retention days is an integer, not a string
# ---------------------------------------------------------------------------

class TestRetentionDaysType:
    def test_retention_days_is_integer_type(self, steps):
        """YAML must parse retention-days as an int, not a quoted string."""
        retention = steps[3].get("with", {}).get("retention-days")
        assert isinstance(retention, int), (
            f"'retention-days' must be an integer (unquoted in YAML), got type: {type(retention).__name__}"
        )

    def test_retention_days_is_positive(self, steps):
        retention = steps[3].get("with", {}).get("retention-days", 0)
        assert retention > 0, (
            f"'retention-days' must be a positive integer, got: {retention}"
        )

    def test_retention_days_within_github_limit(self, steps):
        """Ensures the artifact retention period stays within GitHub Actions limits.
        
        Returns:
        	None
        """
        retention = steps[3].get("with", {}).get("retention-days", 0)
        assert retention <= 90, (
            f"'retention-days' must be <= 90 (GitHub Actions maximum), got: {retention}"
        )


# ---------------------------------------------------------------------------
# Artifact name prefix
# ---------------------------------------------------------------------------

class TestArtifactNamePrefix:
    def test_artifact_name_starts_with_semgrep_sarif_prefix(self, steps):
        """Artifact name must begin with 'semgrep-sarif-' for easy identification."""
        artifact_name = str(steps[3].get("with", {}).get("name", ""))
        assert artifact_name.startswith("semgrep-sarif-"), (
            f"Artifact name must start with 'semgrep-sarif-' prefix, got: '{artifact_name}'"
        )

    def test_artifact_name_uses_expression_syntax_for_run_id(self, steps):
        """github.run_id must be referenced with GitHub Actions expression syntax."""
        artifact_name = str(steps[3].get("with", {}).get("name", ""))
        assert "${{" in artifact_name or "${{ " in artifact_name.replace("${{", "${{ "), (
            f"Artifact name must use '${{{{ ... }}}}' expression syntax for github.run_id"
        )


# ---------------------------------------------------------------------------
# Separate --sarif and --sarif-output flags
# ---------------------------------------------------------------------------

class TestSarifFlagsDistinct:
    def test_sarif_flag_and_sarif_output_flag_both_present(self, steps):
        """--sarif and --sarif-output are separate flags; both must be present."""
        run_cmd = steps[1]["run"]
        # --sarif-output= contains --sarif as substring; check both independently
        assert "--sarif-output=" in run_cmd, (
            "Scan command must include '--sarif-output=<filename>' flag"
        )
        # Strip --sarif-output occurrences and verify --sarif still present
        stripped = run_cmd.replace("--sarif-output", "")
        assert "--sarif" in stripped, (
            "Scan command must include the standalone '--sarif' flag in addition to '--sarif-output'"
        )

    def test_sarif_output_points_to_correct_filename(self, steps):
        run_cmd = steps[1]["run"]
        assert f"--sarif-output={SARIF_FILENAME}" in run_cmd, (
            f"--sarif-output must point to '{SARIF_FILENAME}', check for typos or path changes"
        )


# ---------------------------------------------------------------------------
# Top-level YAML structure
# ---------------------------------------------------------------------------

class TestTopLevelYamlStructure:
    def test_top_level_has_exactly_one_key(self, workflow_yaml):
        """Ensures the workflow file contains exactly one top-level key.
        
        Parameters:
        	workflow_yaml: Parsed workflow YAML mapping.
        """
        keys = list(workflow_yaml.keys())
        assert len(keys) == 1, (
            f"Expected exactly 1 top-level key ('semgrep'), found: {keys}"
        )

    def test_top_level_key_is_semgrep(self, workflow_yaml):
        assert list(workflow_yaml.keys()) == ["semgrep"], (
            f"The only top-level key must be 'semgrep', found: {list(workflow_yaml.keys())}"
        )


# ---------------------------------------------------------------------------
# SARIF upload step `with:` params
# ---------------------------------------------------------------------------

class TestSarifUploadWithParams:
    def test_sarif_upload_with_has_only_expected_keys(self, steps):
        """
        Ensures the SARIF upload step only defines the expected `with` keys.
        """
        with_params = steps[2].get("with", {})
        expected_keys = {"sarif_file", "category"}
        extra_keys = set(with_params.keys()) - expected_keys
        assert not extra_keys, (
            f"SARIF upload 'with' block has unexpected keys: {extra_keys}; "
            f"expected only: {expected_keys}"
        )

    def test_sarif_upload_with_has_both_required_keys(self, steps):
        with_params = steps[2].get("with", {})
        assert "sarif_file" in with_params, "SARIF upload must specify 'sarif_file'"
        assert "category" in with_params, "SARIF upload must specify 'category'"


# ---------------------------------------------------------------------------
# Step ordering verification (index-independent approach)
# ---------------------------------------------------------------------------

class TestStepActionValues:
    def test_checkout_action_full_reference(self, steps):
        """Verify the full action reference for checkout."""
        assert steps[0]["uses"] == "actions/checkout@v4", (
            f"Checkout action must be exactly 'actions/checkout@v4', "
            f"got: '{steps[0]['uses']}'"
        )

    def test_sarif_upload_action_full_reference(self, steps):
        """Verify the full action reference for SARIF upload."""
        assert steps[2]["uses"] == "github/codeql-action/upload-sarif@v4", (
            f"SARIF upload action must be exactly 'github/codeql-action/upload-sarif@v4', "
            f"got: '{steps[2]['uses']}'"
        )

    def test_artifact_upload_action_full_reference(self, steps):
        """Verify the full action reference for artifact upload."""
        assert steps[3]["uses"] == "actions/upload-artifact@v4", (
            f"Artifact upload action must be exactly 'actions/upload-artifact@v4', "
            f"got: '{steps[3]['uses']}'"
        )

    def test_scan_step_uses_run_not_uses(self, steps):
        """Scan step must use 'run:' to invoke the semgrep binary, not 'uses:' (no action)."""
        assert "run" in steps[1], "Scan step must have a 'run' key"
        assert "uses" not in steps[1], (
            "Scan step must not reference a pre-built action; "
            "it must invoke 'semgrep scan' directly via 'run:'"
        )


# ---------------------------------------------------------------------------
# Regression: SARIF filename consistency across all four references
# ---------------------------------------------------------------------------

class TestSarifFilenameAllFourReferences:
    def test_sarif_filename_in_scan_sarif_output_flag(self, steps):
        run_cmd = steps[1]["run"]
        assert f"--sarif-output={SARIF_FILENAME}" in run_cmd

    def test_sarif_filename_in_sarif_upload_with_param(self, steps):
        assert steps[2].get("with", {}).get("sarif_file") == SARIF_FILENAME

    def test_sarif_filename_in_artifact_upload_path(self, steps):
        assert steps[3].get("with", {}).get("path") == SARIF_FILENAME

    def test_sarif_filename_in_step3_if_condition(self, steps):
        assert SARIF_FILENAME in str(steps[2].get("if", ""))

    def test_sarif_filename_in_step4_if_condition(self, steps):
        assert SARIF_FILENAME in str(steps[3].get("if", ""))

    def test_all_sarif_filename_references_are_identical(self, steps):
        """No reference to SARIF file should use a different name or casing."""
        scan_output = re.search(
            r"--sarif-output=(\S+)", steps[1]["run"].replace("\\\n", " ")
        )
        assert scan_output is not None, "--sarif-output flag not found in scan command"
        output_file = scan_output.group(1).strip()

        sarif_file_param = steps[2].get("with", {}).get("sarif_file", "")
        artifact_path = steps[3].get("with", {}).get("path", "")

        assert output_file == sarif_file_param == artifact_path == SARIF_FILENAME, (
            f"SARIF filename mismatch: scan writes '{output_file}', "
            f"upload-sarif references '{sarif_file_param}', "
            f"artifact path is '{artifact_path}', "
            f"expected all to be '{SARIF_FILENAME}'"
        )