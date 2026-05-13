# Vector Module Contracts

Every imported vector must clear five gates before its standalone repository is deprecated.

## The Five Gates
1.  **Contract Signed:** Typed interfaces (In/Out) are defined.
2.  **Tests Pass:** Vector-level unit tests remain green.
3.  **Spec Kit Score:** Must achieve ≥ 27.5/35 on the Compliance Audit.
4.  **Integration Pass:** End-to-end flow verified in BugBountyOS CI.
5.  **Owner Approval:** Final sign-off by WhacktheJacker.


## Current Vector Contracts
- **Dashboard Vector:** Requires Next.js 15+ and Drizzle compliance.
- **Pipeline Vector:** Requires Mistral/Claude dual-provider support.
- **Storage Vector:** Requires Snowflake-native DDL parity.