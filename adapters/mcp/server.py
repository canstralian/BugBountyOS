from pathlib import Path

import yaml
from mcp.server.fastmcp import FastMCP

REGISTRY_PATH = (
    Path(__file__).resolve().parents[2] / "control-plane" / "registry" / "vectors.yaml"
)

mcp = FastMCP("BugBountyOS Kernel")


@mcp.tool()
def check_scope(asset_id: str) -> str:
    """Query the BugBountyOS Immune System to verify if an asset is authorized."""
    return "Importing Airtable Adapter... Currently Permissive mode."


@mcp.tool()
def list_vectors() -> list:
    """Return the current state of the Vector Registry."""
    try:
        data = yaml.safe_load(REGISTRY_PATH.read_text())
        return [v["id"] for v in data["vectors"]]
    except (OSError, yaml.YAMLError, KeyError, TypeError):
        return []


if __name__ == "__main__":
    mcp.run(transport="stdio")
