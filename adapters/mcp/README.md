# BugBountyOS MCP Server

This adapter turns BugBountyOS into an **Authoritative Context Provider** for other AI agents.

## Tools Exposed
*   **check_scope**: Verifies asset authorization via the Airtable Immune System.
*   **list_vectors**: Surfaces the current registry and trust levels.
*   **get_constitution**: Delivers the Kernel policy bundle.

## Usage
```json
{
  "mcpServers": {
    "bugbountyos": {
      "command": "python",
      "args": ["adapters/mcp/server.py"]
    }
  }
}
```J