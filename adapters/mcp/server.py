from mcp.server.fastmcp import FastMCP

mcp = FastMCP("BugBountyOS Kernel")


@mcp.tool()
def check_scope(asset_id: str) -> str:
    """Query the BugBountyOS Immune System to verify if an asset is authorized."""
    return "Importing Airtable Adapter... Currently Permissive mode."


@mcp.tool()
def list_vectors() -> list:
    """Return the current state of the Vector Registry."""
    return ["dashboard", "pipeline", "storage", "red-sage"]


if __name__ == "__main__":
    mcp.run(transport="stdio")
