from mcp.server.fastmcp import FastMCP

mcp = FastMCP("BugBountyOS Kernel")


@mcp.tool()
def check_scope(asset_id: str) -> str:
    """
    Provide a static scope-check status message for a given asset.
    
    Parameters:
        asset_id (str): Asset identifier (currently unused).
    
    Returns:
        str: The current scope-check status message: "Importing Airtable Adapter... Currently Permissive mode."
    """
    return "Importing Airtable Adapter... Currently Permissive mode."


@mcp.tool()
def list_vectors() -> list:
    """
    List available entries in the Vector Registry.
    
    Returns:
        list: The names of registered vectors, e.g. ["dashboard", "pipeline", "storage", "red-sage"].
    """
    return ["dashboard", "pipeline", "storage", "red-sage"]


if __name__ == "__main__":
    mcp.run(transport="stdio")
