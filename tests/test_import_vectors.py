import os
import subprocess
from pathlib import Path


def test_import_vectors_is_dry_run_and_idempotent() -> None:
    env = os.environ.copy()
    env["EXECUTE"] = "0"
    result = subprocess.run(
        ["bash", "import_vectors.sh"],
        check=True,
        env=env,
        text=True,
        capture_output=True,
    )

    assert "[SKIP] vectors/dashboard already exists; import is idempotent." in result.stdout
    assert "[SKIP] vectors/pipeline already exists; import is idempotent." in result.stdout
    assert "[SKIP] vectors/storage already exists; import is idempotent." in result.stdout
    assert "[DRY-RUN] git subtree add --prefix='vectors/red-sage'" in result.stdout


def test_import_vectors_accepts_custom_registry(tmp_path: Path) -> None:
    registry = tmp_path / "vectors.yaml"
    registry.write_text(
        """
vectors:
  - id: new-vector
    source_repo: example/NewVector
""".strip(),
        encoding="utf-8",
    )
    env = os.environ.copy()
    env.update({"EXECUTE": "0", "REGISTRY": str(registry)})

    result = subprocess.run(
        ["bash", "import_vectors.sh"],
        check=True,
        env=env,
        text=True,
        capture_output=True,
    )

    assert "https://github.com/example/NewVector" in result.stdout
    assert "--prefix='vectors/new-vector'" in result.stdout
