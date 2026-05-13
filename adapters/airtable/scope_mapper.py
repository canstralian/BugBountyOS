"""Airtable scope adapter for BugBountyOS authorization checks."""

from __future__ import annotations


class AirtableScopeAdapter:
    """Read authorized assets from Airtable scope rules."""

    def __init__(self) -> None:
        """Initialize the Airtable adapter with base config."""
        self.base_id = "appT4zR1ybxgrujBD"
        self.scope_rules_table = "Scope Rules"

    def get_active_scope(self) -> list[dict[str, object]]:
        """Fetch all in-scope entities from Airtable.

        This is a stub for the live API call. In an execution context, this
        would use the Airtable list-records integration.
        """
        return []

    def is_authorized(self, asset_id: str) -> bool:
        """Verify whether a specific asset is marked as in scope."""
        return any(record.get("asset_id") == asset_id for record in self.get_active_scope())


if __name__ == "__main__":
    adapter = AirtableScopeAdapter()
    print("[AIRTABLE] Adapter initialized for base:", adapter.base_id)
