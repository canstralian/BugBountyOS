# AIRTABLE Scope Mapping

This module acts as the **Immune System** guardrail for BugBountyOS.

## Flow
1.  **Fetch**: Pulls 'Scope Rules' from Airtable base `appT4zR1ybxgrujBD`.
2.  **Validate:** Checks assets against `in_scope` flags.
3.  **Enforce:** Prevents Vectors from acting on out-of-scope targets.

## Current Mapping
| Table | Role | Status |
|---|---|---|
| Scope Rules | Authorization | ✄ Wired |
| Assets | Target Inventory | ✄ Wired |
