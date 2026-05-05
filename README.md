
# BugBountyOS
> Root nervous system of a governed, multi-vector security operating system.

BugBountyOS          → orchestration root
├── Spec Kit       → immune system (governance, HMAC, audit, scope)
├── OSINT          → sensory cortex (public intelligence collection)
├── DarkOSINT      → threat-memory layer (dark-web / breach signal)
├── RedSage        → offensive cognition (attack-path synthesis)
├── ATDA           → detection reflex loop (autonomous triage)
├── Sentinel       → defensive perception (monitoring surface)
└── BountyOps      → workflow orchestration (scope → submission)

-----
## Architecture
BugBountyOS is not a single application. It is a **security timescape** — a six-phase lifecycle
that connects recon, exploitation, detection, remediation, memory, and reporting into a governed
operating system for automated security work.

timescape/
recon/        → pre-engagement surface discovery
exploit/      → attack-path engagement
detection/    → signal triage and anomaly classification
remediation/  → patch dispatch and fix verification
memory/       → TTP store, engagement history, pgvector embeddings
reporting/    → disclosure packaging and submission

Each phase is populated by **vector modules** — specialized subsystems that own a temporal slice
of the security lifecycle but are governed by the same constitutional layer.
-----
## Constitutional Layer: Spec Kit v2.2
All vectors are governed by `core/spec_kit/`. No vector can bypass it.
| Control | Implementation |
|---|---|
| T1–T4 authority hierarchy | `core.spec_kit.governed_dispatcher` |
| HMAC-SHA256 approval tokens | `core.spec_kit.hmac` |
| SHA-256 hash-chained audit | `core.spec_kit.audit` |
| Scope validation hard-block | `core.spec_kit.scope` |
| Injection resistance A–I | `core.spec_kit.vectors` |
| GREENLIGHT / SECURITY_FAIL gate | `core.spec_kit.scope.enforce_scope` |
Spec Kit score: **[score]/35** | Gate: **[GREENLIGHT / SECURITY_FAIL]**
-----
## Vector Modules
| Vector | Role | Timescape Position | Status |
|---|---|---|---|
| `vectors/osint/` | Public intelligence collection | recon → memory | 🟡 importing |
| `vectors/darkosint/` | Dark-web and breach-signal correlation | recon → memory → reporting | 🟡 importing |
| `vectors/redsage/` | Attack-path synthesis | recon → exploit | 🟡 importing |
| `vectors/atda/` | Detection reflex loop | detection → memory | 🟡 importing |
| `vectors/sentinel_copilot/` | Defensive perception | detection + reporting | 🟡 importing |
| `vectors/bounty_ops/` | Workflow orchestration | all phases | 🟡 importing |
> 🟡 importing = subtree added, contract pending  
> 🟢 active = contract signed, CI passing  
> 🔵 canonical = standalone repo deprecated, this is the single source of truth
-----
## Intelligence Boundaries
OSINT and DarkOSINT are intelligence vectors, not exploitation vectors.
`vectors/osint/` is limited to passive public intelligence collection unless a scope file explicitly authorizes active probing.
`vectors/darkosint/` may collect and correlate dark-web, paste, breach, and underground references, but it must not expose raw credentials, validate credentials, purchase access, trade data, impersonate users, or interact with criminal marketplaces.
All intelligence artifacts must preserve:

source
timestamp
scope reference
confidence score
redaction status
audit hash

-----
## Stack

Python 3.12+     FastAPI          PostgreSQL + pgvector
Pydantic v2      FastMCP          structlog
asyncio          uv               ruff + mypy strict
Docker Compose   GitHub Actions   Spec Kit v2.2

-----
## Getting Started
```bash
# Clone
git clone https://github.com/canstralian/BugBountyOS.git
cd BugBountyOS
# Install
uv sync
# Start services
docker compose up -d
# Run tests
pytest tests/ -v
# Check Spec Kit compliance
python -m core.spec_kit.evaluate

⸻

Module Contracts

Each vector ships a CONTRACT.md defining its role, interfaces, and acceptance criteria.
Standalone source repos are not deprecated until all contract gates pass.

See docs/module_contracts/ for full contracts.

⸻

Security

This repository implements Spec Kit v2.2.
Report security issues: open a private advisory via GitHub Security tab.
Do not open public issues for security findings.
