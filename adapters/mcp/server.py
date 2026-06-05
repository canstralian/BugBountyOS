from mcp.server.fastmcp import FastMCP

mcp = FastMCP("BugBountyOS Kernel")


@mcp.tool()
def check_scope(asset_id: str) -> str:
    """Placeholder: returns a permissive static response (Currently Permissive mode).

    TODO: replace with real MCP/Airtable scope-query logic.
    """
    return "Importing Airtable Adapter... Currently Permissive mode."


@mcp.tool()
def list_vectors() -> list[str]:
    """Return a hardcoded placeholder vector list.

    TODO: replace with dynamic Vector Registry state once implemented.
    """
    return ["dashboard", "pipeline", "storage", "red-sage"]


if __name__ == "__main__":
    mcp.run(transport="stdio")
