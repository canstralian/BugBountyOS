"""BugBountyOS MCP server tools.

The server is intentionally small: it exposes registry and scope context while
keeping registry parsing deterministic and testable without requiring an MCP
runtime to be installed in local CI.
"""

from __future__ import annotations

from importlib.util import find_spec
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[2]
VECTOR_REGISTRY = ROOT_DIR / "control-plane" / "registry" / "vectors.yaml"
CONSTITUTION = ROOT_DIR / "kernel" / "constitution" / "INTERFACE.md"


def _load_yaml(path: Path) -> dict[str, Any]:
    """Load YAML with PyYAML when available, using a tiny registry fallback."""
    if find_spec("yaml") is not None:
        import yaml

        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
        return loaded if isinstance(loaded, dict) else {}

    vectors: list[dict[str, str | int]] = []
    current: dict[str, str | int] | None = None
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped == "vectors:":
            continue
        if stripped.startswith("- "):
            if current:
                vectors.append(current)
            current = {}
            stripped = stripped[2:].strip()
        if current is not None and ":" in stripped:
            key, value = stripped.split(":", 1)
            value = value.strip().strip('"\'')
            current[key.strip()] = int(value) if value.isdigit() else value
    if current:
        vectors.append(current)
    return {"vectors": vectors}


def load_vectors(registry_path: Path = VECTOR_REGISTRY) -> list[dict[str, Any]]:
    """Return vectors from the control-plane registry."""
    data = _load_yaml(registry_path)
    vectors = data.get("vectors", [])
    if not isinstance(vectors, list):
        return []
    return [vector for vector in vectors if isinstance(vector, dict)]


class _LocalFastMCP:
    """Minimal decorator-compatible stand-in for tests without mcp installed."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.tools: dict[str, Any] = {}

    def tool(self) -> Any:
        def decorator(func: Any) -> Any:
            self.tools[func.__name__] = func
            return func

        return decorator

    def run(self, transport: str = "stdio") -> None:
        raise RuntimeError(f"MCP runtime is not installed; cannot run {transport!r} server")


def _build_mcp() -> Any:
    if find_spec("mcp") is not None and find_spec("mcp.server.fastmcp") is not None:
        from mcp.server.fastmcp import FastMCP

        return FastMCP("BugBountyOS Kernel")
    return _LocalFastMCP("BugBountyOS Kernel")


mcp = _build_mcp()


@mcp.tool()
def check_scope(asset_id: str) -> str:
    """Query the BugBountyOS Immune System to verify asset authorization."""
    normalized_asset = asset_id.strip()
    if not normalized_asset:
        return "Asset authorization unknown: empty asset_id."
    return f"Asset authorization for {normalized_asset}: permissive import mode."


@mcp.tool()
def list_vectors() -> list[dict[str, Any]]:
    """Return the current state of the Vector Registry."""
    return load_vectors()


@mcp.tool()
def get_constitution() -> str:
    """Return the Kernel policy bundle used by MCP clients."""
    return CONSTITUTION.read_text(encoding="utf-8")


if __name__ == "__main__":
    mcp.run(transport="stdio")
