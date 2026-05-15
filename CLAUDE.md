# CLAUDE.md

Guidance for Claude (and other AI assistants) working in this repository.

## What this repo is

**BugBountyOS** is a Debian-based "security operating system" for authorized
bug bounty and security research. It is not a generic pentesting distro — it
treats the OS as a **workflow plane** that enforces a structured research
lifecycle:

```
Scope → Asset Graph → Input Map → Hypotheses → Validated Findings → Report Artifacts
```

The repo is the **kernel + control plane** that governs modular **Vectors**
(capability subsystems imported from sister repositories under
`canstralian/*`). The README is the operator-facing pitch; `docs/ARCHITECTURE.md`
and `docs/CONTRACTS.md` describe the underlying model.

Important: the project is in an **early scaffolding phase**. Most vector
modules contain stub code. Treat existing files as load-bearing architecture
declarations even when implementations are skeletal — names, roles, and
contract IDs are part of the public surface.

## Repository layout

```
.
├── kernel/                        # Constitutional layer (policy, audit, routing)
│   └── constitution/INTERFACE.md  # Kernel API spec (policy/decision, health, telemetry)
├── control-plane/
│   └── registry/vectors.yaml      # Authoritative vector registry (id, role, state, source)
├── contracts/                     # Per-vector contracts (5 gates + typed In/Out interfaces)
│   ├── cognition.yaml             # prompt synthesis
│   ├── recon.yaml                 # external OSINT
│   ├── redsage.yaml               # offensive reflex
│   └── sensory.yaml               # WiFi/BLE/RF peripheral sensing
├── adapters/
│   ├── airtable/scope_mapper.py   # "Immune System" — scope authorization gate
│   └── mcp/server.py              # FastMCP server exposing kernel to AI agents
├── vectors/                       # Imported vector subtrees
│   ├── dashboard/                 # React + Vite + Express + Drizzle (visual-cortex)
│   ├── pipeline/                  # Flask stub (metabolism)
│   └── storage/                   # Flask + SQLAlchemy stub (memory)
├── docs/
│   ├── ARCHITECTURE.md            # Security OS frame, lifecycle, promotion flow
│   └── CONTRACTS.md               # The 5 gates spec
├── tests/test_repo_structure.py   # Smoke tests (structure invariants)
├── import_vectors.sh              # Vector import via `git subtree add --squash`
├── .github/workflows/             # ci.yml, tests.yml, lint.yml, build-iso.yml
└── README.md
```

## Core concepts (don't paraphrase these — they're terms of art)

- **Kernel** — policy decision authority, audit eligibility, routing.
- **Control Plane** — vector registry + lifecycle state + telemetry.
- **Vector** — a routable capability subsystem with a typed contract. Each has
  a `role` (e.g. `visual-cortex`, `metabolism`, `memory`, `reflex`, `cognition`,
  `peripheral-sensing`, `external-reconnaissance`).
- **Immune System** — the Airtable-backed scope/authorization adapter. Out of
  scope is a hard failure, not a warning.
- **Lifecycle (traffic-light)**: `Importing` (yellow) → `Active` (blue/green)
  → `Canonical` (green). Failure at any gate → `Quarantined` (red).
- **The Five Gates** (from `docs/CONTRACTS.md`) every vector must clear:
  Contract Signed, Tests Pass, Spec Kit Score ≥ 27.5/35, Integration Pass,
  Owner Approval.

When adding or modifying a vector, update **both** `control-plane/registry/vectors.yaml`
and the corresponding `contracts/<vector>.yaml`. They are paired.

## Development workflows

### Python (kernel, adapters, vector stubs, tests)

- Lint: `ruff check .`
- Tests: `pytest -q`
- Shell scripts: `find . -type f -name "*.sh" -print0 | xargs -0 -r shellcheck`

CI (`.github/workflows/ci.yml`) runs all three on push/PR to `main` and
`develop`. There is no `requirements.txt` checked in; CI installs `ruff`,
`pytest`, `pyyaml` directly. The MCP adapter imports `mcp.server.fastmcp` —
add to a `requirements-dev.txt` if you need it locally.

### Dashboard vector (`vectors/dashboard/`)

React 18 + Vite 6 + TypeScript (strict) + Tailwind + Radix UI + Zustand,
with an Express server layer and Drizzle ORM against Postgres (Neon
serverless driver). Path aliases: `@/*` → `client/src/*`, `@db/*` → `db/*`.

```bash
cd vectors/dashboard
npm install
npm run dev        # Vite dev server on :5173
npm run typecheck  # tsc --noEmit
npm run build      # tsc --noEmit && vite build
```

The build script type-checks before bundling, so a type error fails the
build. Required env: `DATABASE_URL` (Drizzle), `AIRTABLE_API_KEY` (programs
route). No automated test runner is wired up in this vector yet.

### Vector import

`./import_vectors.sh` performs `git subtree add --prefix=vectors/<name>
<url> main --squash` for each registered vector. It's a **dry run by
default**; set `EXECUTE=1` to actually run the subtree adds. Do not invoke
with `EXECUTE=1` casually — subtree imports rewrite directory history.

### ISO build

`.github/workflows/build-iso.yml` runs `lb config && lb build` against
`distro/live-build/`. That directory is **not yet present in-tree** —
the workflow is scaffolding for Phase 1 of the roadmap. Don't fabricate
the distro tree to "fix" it; reference the README roadmap if asked.

## Conventions

- **Branching**: feature branches use the `claude/<slug>-<suffix>` pattern
  (e.g. `claude/add-claude-documentation-GP3GQ`). PRs target `main` or
  `develop`.
- **Vector READMEs** are intentionally one-liners stating role + status.
  Don't expand them into full docs unless asked — the contract YAML and
  `docs/CONTRACTS.md` are the source of truth.
- **Some files (`docs/ARCHITECTURE.md`, `docs/CONTRACTS.md`,
  `kernel/constitution/INTERFACE.md`, several `contracts/*.yaml`, adapter
  READMEs) are base64-encoded on disk.** When asked to edit them, decode
  first (`base64 -d <file>`), edit the plaintext, then re-encode if the
  encoding was intentional — or ask the user whether to keep them
  base64-encoded. Don't assume corruption.
- **No emojis** in commit messages, code, or docs unless the user asks.
- **No new top-level directories** without an entry in `tests/test_repo_structure.py`'s
  required-dirs list (currently: `adapters`, `contracts`, `docs`, `kernel`,
  `vectors`). If you add one, update the test.
- **MIT license** — `tests/test_repo_structure.py::test_license_is_mit`
  enforces the `LICENSE` file contains "MIT".

## Things to avoid

- Don't generate fictitious vector contracts or modify
  `control-plane/registry/vectors.yaml` to register vectors that don't have
  a sister repo. The `source_repo` field is canonical.
- Don't rewrite the Python stubs in `vectors/pipeline/` and `vectors/storage/`
  into "real" implementations — they're placeholders for subtree imports
  from `BugBountyPipeline` and `BugBountyManager`. Implementations land via
  `import_vectors.sh`, not handwritten code.
- Don't add Python dependencies without a corresponding `requirements*.txt`
  update — the CI install step is the only place deps materialize.
- Don't push to `main` directly. Use the branch designated in the session
  prompt (currently `claude/add-claude-documentation-GP3GQ`) and open a draft PR.

## Quick reference: where to look first

| Question                                | File                                              |
| --------------------------------------- | ------------------------------------------------- |
| What vectors exist and their state?     | `control-plane/registry/vectors.yaml`             |
| What does vector X promise?             | `contracts/<vector>.yaml`                         |
| What is the kernel API?                 | `kernel/constitution/INTERFACE.md` (base64)       |
| What's the lifecycle/promotion model?   | `docs/ARCHITECTURE.md` (base64)                   |
| What are the 5 gates?                   | `docs/CONTRACTS.md` (base64)                      |
| How is scope authorization enforced?    | `adapters/airtable/scope_mapper.py`               |
| How do AI agents talk to the kernel?    | `adapters/mcp/server.py`                          |
| What runs in CI?                        | `.github/workflows/{ci,tests,lint,build-iso}.yml` |
