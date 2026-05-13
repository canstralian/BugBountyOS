# BugBountyOS MCP Server

This adapter turns BugBountyOS into an **Authoritative Context Provider** for other AI agents.

## Tools Exposed

* **check_scope**: Verifies asset authorization via the Airtable Immune System.
* **list_vectors**: Surfaces the current registry and trust levels from `control-plane/registry/vectors.yaml`.
* **get_constitution**: Delivers the Kernel policy bundle from `kernel/constitution/INTERFACE.md`.

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
```

## Security Validation Evidence

The MCP adapter is security-sensitive because it exposes authorization and policy context to agents. Changes to this surface are validated by:

* `ruff check .` for static Python linting.
* `pytest -q` for registry-loading, scope, and import-script behavior.
* `bash -n import_vectors.sh` plus ShellCheck in CI for shell safety.
* CodeQL Python analysis in `.github/workflows/security.yml`.
* Semgrep default rules in `.github/workflows/security.yml`.

MCP tools intentionally return local repository state only; no network calls, shell execution, or credential reads are performed by `adapters/mcp/server.py`.
