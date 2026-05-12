from pathlib import Path

import yaml
from mcp.server.fastmcp import FastMCP

_REGISTRY_PATH = (
    Path(__file__).resolve().parent.parent.parent / "control-plane" / "registry" / "vectors.yaml"
)

mcp = FastMCP("BugBountyOS Kernel")


@mcp.tool()
def check_scope(asset_id: str) -> str:
    """Query the BugBountyOS Immune System to verify if an asset is authorized."""
    return "Importing Airtable Adapter... Currently Permissive mode."


@mcp.tool()
def list_vectors() -> list[str]:
    """Return the current state of the Vector Registry, sourced from vectors.yaml."""
    data = yaml.safe_load(_REGISTRY_PATH.read_text())
    return [vector["id"] for vector in data.get("vectors", [])]


if __name__ == "__main__":
    mcp.run(transport="stdio")
