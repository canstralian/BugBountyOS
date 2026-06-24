"""
tests/test_semgrep_workflow.py — Semgrep CI Workflow Structural Tests.

Validates the structure and content of the Semgrep security audit workflow
defined in .github/workflows/semgrep-ci. yml (note: space in filename).

Covers:
  - File presence and YAML parseability
  - Job-level metadata (name, runner, container)
  - Steps existence and correct ordering
  - Semgrep scan command flags and configs
  - SARIF upload conditions and parameters
  - Artifact upload conditions and parameters
  - Consistency of SARIF filename across steps
  - Security-critical configuration requirements
"""

import re
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "semgrep-ci. yml"

SARIF_FILENAME = "semgrep-results.sarif"


@pytest.fixture(scope="module")
def workflow_yaml():
    """
    Load and parse the Semgrep workflow YAML.
    
    Returns:
    	(dict): The parsed workflow YAML document.
    """
    assert WORKFLOW_PATH.is_file(), (
        f"Workflow file not found: {WORKFLOW_PATH}. "
        "Ensure .github/workflows/semgrep-ci. yml exists."
    )
    content = WORKFLOW_PATH.read_text(encoding="utf-8")
    return yaml.safe_load(content)


@pytest.fixture(scope="module")
def job(workflow_yaml):
    """
    Return the top-level `semgrep` job definition.
    
    Parameters:
    	workflow_yaml (dict): Parsed workflow YAML mapping.
    
    Returns:
    	dict: The `semgrep` job configuration.
    """
    assert "semgrep" in workflow_yaml, (
        "Top-level 'semgrep' key must be present in workflow YAML"
    )
    return workflow_yaml["semgrep"]


@pytest.fixture(scope="module")
def steps(job):
    """
    Get the steps defined for the Semgrep job.
    
    Parameters:
    	job: The Semgrep job configuration.
    
    Returns:
    	list: The job's step definitions.
    """
    assert "steps" in job, "Job must define 'steps'"
    assert isinstance(job["steps"], list), "'steps' must be a list"
    assert len(job["steps"]) > 0, "Job must have at least one step"
    return job["steps"]


# ---------------------------------------------------------------------------
# File-level tests
# ---------------------------------------------------------------------------

class TestWorkflowFilePresence:
    def test_workflow_file_exists(self):
        assert WORKFLOW_PATH.is_file(), f"Missing workflow file: {WORKFLOW_PATH}"

    def test_workflow_file_is_nonempty(self):
        assert WORKFLOW_PATH.stat().st_size > 0, "Workflow file must not be empty"

    def test_workflow_yaml_is_parseable(self):
        content = WORKFLOW_PATH.read_text(encoding="utf-8")
        parsed = yaml.safe_load(content)
        assert parsed is not None, "YAML file parsed to None — likely empty or invalid"
        assert isinstance(parsed, dict), "Top-level YAML document must be a mapping"

    def test_workflow_has_semgrep_top_level_key(self, workflow_yaml):
        assert "semgrep" in workflow_yaml, (
            "Top-level key 'semgrep' must exist in the workflow YAML"
        )


# ---------------------------------------------------------------------------
# Job-level metadata
# ---------------------------------------------------------------------------

class TestJobMetadata:
    def test_job_display_name(self, job):
        assert "name" in job, "Job must have a 'name' field"
        assert "Semgrep" in job["name"], (
            "Job display name must reference 'Semgrep'"
        )

    def test_job_display_name_includes_security_audit(self, job):
        assert "Security Audit" in job["name"], (
            "Job name should identify the purpose: 'Security Audit'"
        )

    def test_job_runs_on_ubuntu(self, job):
        assert "runs-on" in job, "Job must specify 'runs-on'"
        assert "ubuntu" in job["runs-on"], (
            "Job must run on an Ubuntu runner for Linux compatibility"
        )

    def test_job_uses_container(self, job):
        assert "container" in job, "Job must define a 'container'"
        assert isinstance(job["container"], dict), "'container' must be a mapping"

    def test_container_uses_semgrep_image(self, job):
        container = job["container"]
        assert "image" in container, "Container must specify an 'image'"
        assert "semgrep/semgrep" in container["image"], (
            "Container image must be semgrep/semgrep to ensure correct tool version"
        )

    def test_container_image_is_latest_or_pinned(self, job):
        image = job["container"]["image"]
        # Accept either :latest or a pinned version tag (e.g., :1.x.x)
        assert ":" in image, (
            "Container image should include a tag (e.g., :latest or a pinned version)"
        )


# ---------------------------------------------------------------------------
# Steps structure
# ---------------------------------------------------------------------------

class TestStepsStructure:
    def test_job_has_exactly_four_steps(self, steps):
        assert len(steps) == 4, (
            f"Expected 4 steps (checkout, scan, upload-sarif, upload-artifact), "
            f"got {len(steps)}"
        )

    def test_all_steps_have_names(self, steps):
        for i, step in enumerate(steps):
            assert "name" in step, f"Step {i} must have a 'name'"
            assert step["name"].strip(), f"Step {i} name must not be blank"

    def test_first_step_is_checkout(self, steps):
        assert "checkout" in steps[0]["name"].lower(), (
            "First step should be 'Checkout repository'"
        )

    def test_second_step_is_semgrep_scan(self, steps):
        assert "semgrep" in steps[1]["name"].lower() or "scan" in steps[1]["name"].lower(), (
            "Second step should run the Semgrep scan"
        )

    def test_third_step_is_sarif_upload_to_security(self, steps):
        name = steps[2]["name"].lower()
        assert "sarif" in name or "upload" in name or "security" in name, (
            "Third step should upload SARIF to GitHub Security tab"
        )

    def test_fourth_step_is_artifact_upload(self, steps):
        name = steps[3]["name"].lower()
        assert "artifact" in name or "upload" in name, (
            "Fourth step should upload the SARIF as a build artifact"
        )


# ---------------------------------------------------------------------------
# Checkout step
# ---------------------------------------------------------------------------

class TestCheckoutStep:
    def test_checkout_uses_actions_checkout(self, steps):
        checkout_step = steps[0]
        assert "uses" in checkout_step, "Checkout step must use an action (uses:)"
        assert checkout_step["uses"].startswith("actions/checkout"), (
            "Checkout step must use actions/checkout"
        )

    def test_checkout_uses_v4(self, steps):
        uses = steps[0]["uses"]
        assert "@v4" in uses, (
            f"Checkout action should pin to @v4, got: {uses}"
        )


# ---------------------------------------------------------------------------
# Semgrep scan step
# ---------------------------------------------------------------------------

class TestSemgrepScanStep:
    def test_scan_step_has_run_command(self, steps):
        scan_step = steps[1]
        assert "run" in scan_step, "Scan step must define a 'run' command"
        assert scan_step["run"].strip(), "Scan 'run' command must not be empty"

    def test_scan_includes_security_audit_config(self, steps):
        run_cmd = steps[1]["run"]
        assert "p/security-audit" in run_cmd, (
            "Semgrep must include '--config p/security-audit' for security scanning"
        )

    def test_scan_includes_secrets_config(self, steps):
        run_cmd = steps[1]["run"]
        assert "p/secrets" in run_cmd, (
            "Semgrep must include '--config p/secrets' to detect credential leaks"
        )

    def test_scan_uses_sarif_output_format(self, steps):
        run_cmd = steps[1]["run"]
        assert "--sarif" in run_cmd, (
            "Semgrep scan must use '--sarif' flag to emit SARIF-format results"
        )

    def test_scan_specifies_sarif_output_file(self, steps):
        run_cmd = steps[1]["run"]
        assert f"--sarif-output={SARIF_FILENAME}" in run_cmd, (
            f"Scan must write SARIF output to '{SARIF_FILENAME}'"
        )

    def test_scan_uses_error_flag(self, steps):
        run_cmd = steps[1]["run"]
        assert "--error" in run_cmd, (
            "Semgrep must use '--error' flag so the workflow fails when findings exist"
        )

    def test_scan_invokes_semgrep_binary(self, steps):
        run_cmd = steps[1]["run"]
        assert run_cmd.strip().startswith("semgrep"), (
            "Scan run command must invoke the semgrep binary directly"
        )

    def test_scan_uses_scan_subcommand(self, steps):
        run_cmd = steps[1]["run"]
        assert "semgrep scan" in run_cmd or "semgrep  scan" in run_cmd.replace("\\\n", " "), (
            "Scan command must use the 'semgrep scan' subcommand"
        )

    def test_scan_has_both_config_flags(self, steps):
        run_cmd = steps[1]["run"]
        config_matches = re.findall(r"--config\s+\S+", run_cmd.replace("\\\n", " "))
        assert len(config_matches) >= 2, (
            f"Expected at least 2 '--config' flags, found: {config_matches}"
        )


# ---------------------------------------------------------------------------
# SARIF upload to GitHub Security tab (step 3)
# ---------------------------------------------------------------------------

class TestSarifSecurityUploadStep:
    def test_sarif_upload_uses_codeql_action(self, steps):
        upload_step = steps[2]
        assert "uses" in upload_step, (
            "SARIF upload step must reference a GitHub Action via 'uses:'"
        )
        assert "codeql-action/upload-sarif" in upload_step["uses"], (
            "SARIF upload must use github/codeql-action/upload-sarif"
        )

    def test_sarif_upload_action_pinned_to_v4(self, steps):
        uses = steps[2]["uses"]
        assert "@v4" in uses, (
            f"upload-sarif action should be pinned to @v4, got: {uses}"
        )

    def test_sarif_upload_specifies_sarif_file(self, steps):
        with_params = steps[2].get("with", {})
        assert "sarif_file" in with_params, (
            "SARIF upload step must specify 'sarif_file' parameter"
        )
        assert with_params["sarif_file"] == SARIF_FILENAME, (
            f"sarif_file must be '{SARIF_FILENAME}', got: {with_params['sarif_file']}"
        )

    def test_sarif_upload_specifies_category(self, steps):
        with_params = steps[2].get("with", {})
        assert "category" in with_params, (
            "SARIF upload step should specify a 'category' for GitHub Security filtering"
        )
        assert with_params["category"] == "semgrep", (
            f"Category must be 'semgrep', got: {with_params['category']}"
        )

    def test_sarif_upload_has_always_condition(self, steps):
        step_if = steps[2].get("if", "")
        assert "always()" in str(step_if), (
            "SARIF upload to Security tab must run with 'always()' so it executes "
            "even when the scan step fails (findings were detected)"
        )

    def test_sarif_upload_checks_file_exists(self, steps):
        step_if = steps[2].get("if", "")
        assert "hashFiles" in str(step_if), (
            "Upload condition must use hashFiles() to verify the SARIF file was created"
        )

    def test_sarif_upload_condition_checks_correct_file(self, steps):
        step_if = str(steps[2].get("if", ""))
        assert SARIF_FILENAME in step_if, (
            f"Upload condition must reference '{SARIF_FILENAME}' in hashFiles()"
        )


# ---------------------------------------------------------------------------
# Artifact upload step (step 4)
# ---------------------------------------------------------------------------

class TestArtifactUploadStep:
    def test_artifact_upload_uses_upload_artifact_action(self, steps):
        upload_step = steps[3]
        assert "uses" in upload_step, (
            "Artifact upload step must reference an action via 'uses:'"
        )
        assert "upload-artifact" in upload_step["uses"], (
            "Artifact upload must use actions/upload-artifact"
        )

    def test_artifact_upload_action_pinned_to_v4(self, steps):
        uses = steps[3]["uses"]
        assert "@v4" in uses, (
            f"upload-artifact action should be pinned to @v4, got: {uses}"
        )

    def test_artifact_upload_specifies_name(self, steps):
        with_params = steps[3].get("with", {})
        assert "name" in with_params, (
            "Artifact upload must specify an artifact 'name'"
        )

    def test_artifact_name_includes_run_id(self, steps):
        artifact_name = str(steps[3].get("with", {}).get("name", ""))
        assert "github.run_id" in artifact_name, (
            "Artifact name must include github.run_id to ensure uniqueness across runs"
        )

    def test_artifact_upload_specifies_path(self, steps):
        with_params = steps[3].get("with", {})
        assert "path" in with_params, (
            "Artifact upload must specify 'path' of the file to upload"
        )
        assert with_params["path"] == SARIF_FILENAME, (
            f"Artifact path must be '{SARIF_FILENAME}', got: {with_params['path']}"
        )

    def test_artifact_retention_days_is_set(self, steps):
        with_params = steps[3].get("with", {})
        assert "retention-days" in with_params, (
            "Artifact upload must specify 'retention-days' to control storage lifecycle"
        )

    def test_artifact_retention_days_is_30(self, steps):
        retention = steps[3].get("with", {}).get("retention-days")
        assert retention == 30, (
            f"Artifact retention must be 30 days, got: {retention}"
        )

    def test_artifact_upload_has_always_condition(self, steps):
        step_if = steps[3].get("if", "")
        assert "always()" in str(step_if), (
            "Artifact upload must run with 'always()' so SARIF is preserved "
            "even when the scan detects findings and the scan step exits non-zero"
        )

    def test_artifact_upload_checks_file_exists(self, steps):
        step_if = steps[3].get("if", "")
        assert "hashFiles" in str(step_if), (
            "Artifact upload condition must use hashFiles() to verify SARIF file exists"
        )

    def test_artifact_upload_condition_checks_correct_file(self, steps):
        step_if = str(steps[3].get("if", ""))
        assert SARIF_FILENAME in step_if, (
            f"Artifact upload condition must reference '{SARIF_FILENAME}'"
        )


# ---------------------------------------------------------------------------
# Cross-step consistency
# ---------------------------------------------------------------------------

class TestCrossStepConsistency:
    def test_sarif_filename_consistent_in_scan_and_security_upload(self, steps):
        """The SARIF filename written by the scan must match what the upload steps reference."""
        scan_run = steps[1]["run"]
        sarif_upload_file = steps[2].get("with", {}).get("sarif_file", "")
        assert SARIF_FILENAME in scan_run, (
            f"Scan must write to '{SARIF_FILENAME}'"
        )
        assert sarif_upload_file == SARIF_FILENAME, (
            f"Security upload step must reference the same SARIF file '{SARIF_FILENAME}'"
        )

    def test_sarif_filename_consistent_in_scan_and_artifact_upload(self, steps):
        """The SARIF filename written by the scan must match the artifact path."""
        scan_run = steps[1]["run"]
        artifact_path = steps[3].get("with", {}).get("path", "")
        assert SARIF_FILENAME in scan_run
        assert artifact_path == SARIF_FILENAME, (
            f"Artifact upload path must match SARIF output filename '{SARIF_FILENAME}'"
        )

    def test_both_upload_steps_use_always_condition(self, steps):
        """Both post-scan upload steps must run even when scan finds issues."""
        for i in (2, 3):
            step_if = str(steps[i].get("if", ""))
            assert "always()" in step_if, (
                f"Step {i} ('{steps[i]['name']}') must use always() condition "
                "to upload SARIF results even on non-zero scan exit"
            )

    def test_both_upload_steps_check_hashfiles_for_same_sarif(self, steps):
        """Both upload steps must guard against missing SARIF using hashFiles."""
        for i in (2, 3):
            step_if = str(steps[i].get("if", ""))
            assert "hashFiles" in step_if, (
                f"Step {i} must use hashFiles() to guard against missing SARIF"
            )
            assert SARIF_FILENAME in step_if, (
                f"Step {i} hashFiles() must reference '{SARIF_FILENAME}'"
            )

    def test_no_step_before_checkout_uses_repository_code(self, steps):
        """Checkout must be the first step; no step before it should use repository files."""
        assert steps[0]["uses"].startswith("actions/checkout"), (
            "Checkout must be the very first step so subsequent steps can access code"
        )


# ---------------------------------------------------------------------------
# Security-critical configuration requirements
# ---------------------------------------------------------------------------

class TestSecurityConfiguration:
    def test_workflow_fails_on_findings_via_error_flag(self, steps):
        """--error ensures CI is blocked when Semgrep detects security issues."""
        run_cmd = steps[1]["run"]
        assert "--error" in run_cmd, (
            "'--error' flag is required to fail the build on Semgrep findings; "
            "omitting it would silently pass a scan with detected vulnerabilities"
        )

    def test_secrets_scanning_is_enabled(self, steps):
        """p/secrets config detects committed credentials and API keys."""
        run_cmd = steps[1]["run"]
        assert "p/secrets" in run_cmd, (
            "'p/secrets' config is required to detect accidentally committed secrets"
        )

    def test_security_audit_ruleset_is_enabled(self, steps):
        """p/security-audit provides OWASP and CVE-level vulnerability detection."""
        run_cmd = steps[1]["run"]
        assert "p/security-audit" in run_cmd, (
            "'p/security-audit' config is required for comprehensive vulnerability coverage"
        )

    def test_semgrep_container_prevents_tool_version_drift(self, job):
        """Running in the semgrep container avoids relying on a potentially stale pip install."""
        assert "semgrep/semgrep" in job["container"]["image"], (
            "Using the official semgrep container ensures a consistent, up-to-date tool version"
        )

    def test_sarif_uploaded_to_github_security_tab(self, steps):
        """Results must reach the GitHub Security tab for centralized visibility."""
        uses = steps[2].get("uses", "")
        assert "upload-sarif" in uses, (
            "SARIF must be uploaded to GitHub Security tab via codeql-action/upload-sarif"
        )

    def test_sarif_also_preserved_as_downloadable_artifact(self, steps):
        """Artifact upload ensures SARIF is accessible even if Security tab access is restricted."""
        uses = steps[3].get("uses", "")
        assert "upload-artifact" in uses, (
            "SARIF must also be saved as a downloadable artifact for offline inspection"
        )

    def test_upload_steps_run_on_scan_failure(self, steps):
        """Regression: if scan detects issues (exit code != 0), uploads must still occur."""
        for i in (2, 3):
            step_if = str(steps[i].get("if", ""))
            assert "always()" in step_if, (
                f"Step {i} must use 'always()' — without it, a failing scan (due to "
                f"'--error') would prevent SARIF from being uploaded to review findings"
            )
