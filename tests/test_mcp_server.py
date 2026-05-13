from pathlib import Path

from adapters.mcp import server


def test_list_vectors_loads_registry_dynamically() -> None:
    vectors = server.list_vectors()

    assert [vector["id"] for vector in vectors] == [
        "dashboard",
        "pipeline",
        "storage",
        "red-sage",
    ]
    assert vectors[0]["trust_level"] == "permissive"


def test_load_vectors_reads_custom_registry(tmp_path: Path) -> None:
    registry = tmp_path / "vectors.yaml"
    registry.write_text(
        """
vectors:
  - id: sentinel
    role: guard
    state: importing
    trust_level: tainted
    source_repo: example/Sentinel
    contract_version: 0
""".strip(),
        encoding="utf-8",
    )

    assert server.load_vectors(registry) == [
        {
            "id": "sentinel",
            "role": "guard",
            "state": "importing",
            "trust_level": "tainted",
            "source_repo": "example/Sentinel",
            "contract_version": 0,
        }
    ]


def test_check_scope_rejects_empty_asset() -> None:
    assert server.check_scope("   ") == "Asset authorization unknown: empty asset_id."
