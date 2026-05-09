# BugBountyOS
[![CI](https://github.com/canstralian/BugBountyOS/actions/workflows/ci.yml/badge.svg)](https://github.com/canstralian/BugBountyOS/actions/workflows/ci.yml)
[![ISO Build](https://github.com/canstralian/BugBountyOS/actions/workflows/build-iso.yml/badge.svg)](https://github.com/canstralian/BugBountyOS/actions/workflows/build-iso.yml)

A Debian-based operating environment for authorized bug bounty and security research.
> Bug bounty work should be **scoped, auditable, evidence-first, and report-ready by default.**
BugBountyOS treats the operating system as a workflow plane for the full research lifecycle:
```text
Scope → Asset Graph → Input Map → Hypotheses → Validated Findings → Report Artifacts

This is not a generic pentesting distro. It is a structured operator environment designed to enforce research discipline at the OS level.

⸻

Overview

Most security distros optimize for tool availability.

BugBountyOS optimizes for:

* Scope-aware execution
* Evidence capture
* Reproducible workflows
* Safer defaults
* Report-ready state

The goal is not to out-Kali Kali or ship every offensive tool with a pulse.

The goal is to create a controlled research environment where operators can move from scoped recon to validated findings with less drift, less chaos, and less evidence archaeology later.

⸻

Why It Exists

Bug bounty workflows tend to fail in predictable places:

* scope gets ignored or lost mid-stream
* outputs scatter across terminals, screenshots, notebooks, and browser tabs
* evidence is collected inconsistently
* risky actions are launched without enough structure or review
* findings are drafted later from memory instead of from preserved state

BugBountyOS is designed to reduce that entropy.

Instead of treating the OS as a neutral shell full of tools, it treats the OS as a workflow enforcement layer. The operating system, project model, tool wrappers, evidence handling, and report generation all reinforce the same operating discipline.

⸻

Design Goals

BugBountyOS is built to:

* enforce scope before execution
* preserve evidence as first-class state
* make findings traceable to collected artifacts
* keep operator workflows reproducible
* prefer safe defaults over tool sprawl
* support authorized research, not indiscriminate activity
* turn project state into report-ready outputs

⸻

What Makes BugBountyOS Different

BugBountyOS is not:

* a wallpapered Debian remaster
* a generic “ethical hacking” live ISO
* a random bundle of recon tools
* a thin Kali clone

BugBountyOS is a structured operator environment for authorized bug bounty work.

It is intended to provide:

* a defined workspace model
* typed scope manifests
* policy-aware tool wrappers
* evidence indexing and hashing
* notes and hypotheses tied to project state
* finding drafts linked to artifacts
* report generation from structured data

In short:

Kali-style distributions optimize for tool access.
BugBountyOS optimizes for controlled research flow.

⸻

How It Differs from Kali

	Kali	BugBountyOS
Optimized for	Tool breadth	Controlled research flow
Scope enforcement	Manual	Machine-readable manifest
Evidence handling	Ad hoc	Automatic indexing and hashing
Workflow model	General-purpose toolkit	Structured project lifecycle
Primary user model	Broad security work	Authorized bug bounty operators

BugBountyOS does not try to replace Kali’s coverage. It provides structure around a curated, workflow-oriented toolset.

⸻

Core Principles

Scope First

Every project begins with an explicit scope manifest.

Targets, exclusions, allowed actions, and constraints are defined before execution. Wrapped tools can inspect that manifest and refuse, warn, or constrain execution based on policy.

Evidence by Default

Artifacts should not disappear into terminal history.

BugBountyOS is designed to capture logs, screenshots, responses, hashes, and tool metadata in a consistent project structure so findings can be traced back to their source.

Workflow Over Tool Sprawl

The project is not trying to ship every possible offensive utility.

It focuses on the minimum useful set of curated tools needed to support a disciplined bug bounty workflow.

Safer Execution

Potentially noisy or risky actions should be explicit, gated, and reviewable.

BugBountyOS is designed to encourage bounded, authorized testing rather than loose, unstructured execution.

Report-Ready State

Notes, evidence, observations, and findings should accumulate into usable report artifacts instead of becoming a forensic excavation six hours later.

⸻

Architecture

BugBountyOS is built as a Debian derivative with five major layers.

1. Distro Layer

Provides the Debian base, ISO build profile, package sources, branding, and release mechanics.

2. Platform Layer

Provides shared defaults, workspace conventions, CLI entry points, state paths, and package structure.

3. Workflow Layer

Implements the bug bounty lifecycle through project initialization, scope handling, assets, notes, evidence capture, findings, and reports.

4. Execution Layer

Exposes selected security tools through wrapped execution paths and curated profiles rather than relying on raw, unstructured invocation.

5. Policy Layer

Enforces scope checks, action-class restrictions, and trust boundaries between trusted configuration and untrusted target-derived data.

⸻

Project Status

Early build phase. v0.1 is the first milestone.

The v0.1 target is to provide a Debian-based bootable image that can:

* initialize a structured project workspace
* validate a scope manifest
* run a small set of wrapped recon actions against authorized targets
* capture and hash evidence automatically
* create finding drafts linked to evidence
* generate a report skeleton from project state

⸻

Planned Workflow

Full ISO, APT repository, and install instructions land with v0.1.

# Initialize a project
bbos init example-program
# Validate your scope manifest
bbos scope validate scope/scope.yml
# Import targets
bbos asset import domains domains.txt
# Run a wrapped recon action
bbos run recon httpx --targets assets/domains.txt
# Capture evidence
bbos evidence add screenshots/homepage.png --kind screenshot --target app.example.com
# Create a finding draft
bbos finding create open-redirect
# Build a report
bbos report build

The point is not command novelty. The point is that execution, evidence, and reporting all live inside the same structured project model.

⸻

Workspace Model

Every project follows a defined layout:

/workspaces/<project_slug>/
  project.yml
  scope/
    scope.yml
    exclusions.yml
  assets/
    domains.txt
    subdomains.txt
    urls.txt
    hosts.txt
    services.json
  notes/
    hypotheses.md
    observations.md
    timeline.md
  evidence/
    screenshots/
    responses/
    logs/
    attachments/
    hashes/
    index.json
  findings/
    drafts/
    submitted/
  reports/
    technical/
    executive/
  state/
    assets.json
    tool_runs.jsonl
    decisions.jsonl
    evidence.jsonl
    findings.json

This structure is intentional. Bug bounty workflows generate fragmented state. BugBountyOS is designed to make that state legible, portable, and reviewable.

⸻

Scope Manifest

Every project starts with a typed scope manifest:

version: 1
program:
  name: "Example Program"
  platform: "HackerOne"
  handle: "example"
targets:
  include:
    - "*.example.com"
    - "api.example.com"
  exclude:
    - "admin.example.com"
    - "*.internal.example.com"
actions:
  allowed:
    - passive_recon
    - web_enum
    - screenshot_capture
    - safe_http_probe
  restricted:
    - aggressive_fuzzing
    - auth_bruteforce
constraints:
  rate_limit: "low"
  notes:
    - "No testing against payment flows"
    - "No authenticated testing without explicit approval"
timebox:
  start: "2026-05-08T00:00:00Z"
  end: "2026-05-30T23:59:59Z"

Wrapped tools read this manifest before executing. Out-of-scope targets are blocked. Restricted actions require an explicit override path.

⸻

Command Reference

bbos init             Initialize a project workspace
bbos scope validate   Validate a scope manifest
bbos scope show       Display active scope
bbos asset import     Import targets into structured state
bbos asset list       List known assets
bbos note add         Append to notes
bbos hypothesis add   Record a testable hypothesis
bbos run              Execute a wrapped tool
bbos evidence add     Manually add an artifact
bbos evidence hash    Hash and index a file
bbos finding create   Create a finding draft
bbos report build     Compile a report from project state
bbos status           Project summary
bbos doctor           Environment health check

The CLI is the primary control surface for the MVP. A richer TUI or desktop console can come later, once the foundations stop moving underfoot.

⸻

Package Layout

The planned package model is:

bugbountyos-base            System defaults, shared paths, shell profile
bugbountyos-branding        Identity, motd, release metadata
bugbountyos-cli             Main bbos entry point and subcommands
bugbountyos-scope           Manifest parser, schema validation, policy engine
bugbountyos-workspace       Project init, template generation, state management
bugbountyos-evidence        Artifact storage, hashing, indexing
bugbountyos-reporting       Finding templates, report generation
bugbountyos-guardrails      Risky-command wrappers, action-class enforcement
bugbountyos-recon           Curated recon tools and wrappers
bugbountyos-web             Browser stack, proxy tooling, API helpers
bugbountyos-control-center  CLI/TUI operator console

Each package is meant to own a distinct part of the system so the project does not collapse into one giant maintenance swamp.

⸻

Execution Model

Wrapped execution is the core enforcement path.

A typical bbos run flow is expected to look like this:

user request
  → tool alias lookup
  → action class resolution
  → target normalization
  → scope check
  → policy check
  → command render
  → execution
  → output capture
  → metadata logging
  → artifact indexing

This is how the project encodes governance into execution rather than burying it in documentation nobody reads once packets start moving.

⸻

Evidence Model

Artifacts are treated as first-class project objects.

Evidence may include:

* screenshots
* HTTP responses
* logs
* command outputs
* attachments
* hashes
* timestamps
* target linkage
* source tool metadata

The purpose is straightforward: findings should be reconstructable from preserved state, not from operator memory.

⸻

Reporting Model

BugBountyOS is intended to accumulate enough structure during execution that reporting becomes compilation rather than improvisation.

A finding draft should ultimately be able to reference:

* title
* target
* hypothesis
* observed behavior
* impact notes
* reproduction steps
* linked evidence
* severity estimate
* current status

The workflow should end in report-ready artifacts, not a pile of disconnected terminal transcripts and a worsening mood.

⸻

Security Posture

BugBountyOS is designed around explicit trust boundaries:

* signed packages and repository metadata
* strict manifest parsing
* scope-aware tool wrappers with hard block on out-of-scope targets
* hash-based evidence integrity
* append-only state logs where feasible
* unprivileged default operator workflows
* separation of trusted configuration from target-derived data
* minimal implicit trust in tool output

This is a security environment. Trust should be engineered, not assumed because something printed green text and sounded confident.

⸻

Threat Model

The initial project threat model includes:

* operator error
* scope drift
* dangerous tool execution against unauthorized targets
* malformed or hostile target-derived data
* evidence tampering after collection
* untrusted command output contaminating notes or reports
* supply-chain risk in package and release infrastructure

BugBountyOS is intended to reduce these risks through policy-aware execution, structured storage, and clearer system boundaries.

⸻

Build Philosophy

BugBountyOS should be:

* boring at the base
* strict at the boundaries
* useful in the workflow
* explicit about trust
* disciplined about scope

The distro is not the product by itself.

The workflow is the product.
The distro is the delivery mechanism.

⸻

Roadmap

v0.1

* Debian-based bootable image
* core CLI
* scope manifest validation
* structured workspace initialization
* wrapped recon commands for a small curated toolset
* automatic evidence hashing and indexing
* finding draft support
* report skeleton generation

v0.2

* stronger policy engine
* richer evidence linking
* asset graph support
* safer browser and container isolation
* better reporting templates

v0.3+

* control center / TUI
* AI-assisted summarization constrained by local evidence
* encrypted project export bundles
* optional team-oriented workflows
* containerized high-risk execution paths

⸻

What v0.1 Will Not Do

To keep the project from becoming a cosplay convention for unfinished ambition, v0.1 will not attempt to:

* replace Kali in breadth of tooling
* ship every offensive utility available
* build a full custom desktop environment
* require a complex AI agent stack for core usability
* solve team collaboration before the single-operator workflow is solid

BugBountyOS starts with operator workflow first.

⸻

Intended Audience

BugBountyOS is intended for:

* independent bug bounty researchers
* structured operators who want reproducible project state
* builders who care about evidence integrity and reporting flow
* teams evaluating whether the workflow can later be extended into shared infrastructure

It is not intended as a general-purpose “hacker distro” for anyone who wants a themed desktop and 800 tools they do not understand.

⸻

Contributing

Contributions are welcome, especially in:

* Debian packaging and live-build
* CLI and scope engine implementation
* evidence handling and artifact indexing
* report generation and finding templates
* reproducible build workflows
* operator UX for structured security research

Contribution guidelines will be published as the repository structure stabilizes.

⸻

Documentation

* docs/architecture.md￼ — system design and layer breakdown
* docs/manifests.md￼ — scope manifest schema and policy engine
* docs/roadmap.md￼ — versioned milestone plan
* docs/threat-model.md￼ — trust boundaries and initial threat assumptions

⸻

License

[Insert license]

⸻

Long-Term Direction

BugBountyOS is intended to become a research environment where:

* authorized scope is machine-readable
* execution is policy-aware
* evidence is preserved automatically
* findings emerge from artifacts, not memory
* reports are generated from structured state
* trust boundaries remain explicit throughout the system

Not more tools.

Better structure.

A couple of blunt notes so this doesn’t become README theater:
Replace the badge URLs if your workflow filenames differ.
Here’s a complete repo-ready README you can drop in as README.md.

# BugBountyOS
[![CI](https://github.com/canstralian/BugBountyOS/actions/workflows/ci.yml/badge.svg)](https://github.com/canstralian/BugBountyOS/actions/workflows/ci.yml)
[![ISO Build](https://github.com/canstralian/BugBountyOS/actions/workflows/build-iso.yml/badge.svg)](https://github.com/canstralian/BugBountyOS/actions/workflows/build-iso.yml)
A Debian-based operating environment for authorized bug bounty and security research.
> Bug bounty work should be **scoped, auditable, evidence-first, and report-ready by default.**
BugBountyOS treats the operating system as a workflow plane for the full research lifecycle:
```text
Scope → Asset Graph → Input Map → Hypotheses → Validated Findings → Report Artifacts

This is not a generic pentesting distro. It is a structured operator environment designed to enforce research discipline at the OS level.

⸻

Overview

Most security distros optimize for tool availability.

BugBountyOS optimizes for:

* Scope-aware execution
* Evidence capture
* Reproducible workflows
* Safer defaults
* Report-ready state

The goal is not to out-Kali Kali or ship every offensive tool with a pulse.

The goal is to create a controlled research environment where operators can move from scoped recon to validated findings with less drift, less chaos, and less evidence archaeology later.

⸻

Why It Exists

Bug bounty workflows tend to fail in predictable places:

* scope gets ignored or lost mid-stream
* outputs scatter across terminals, screenshots, notebooks, and browser tabs
* evidence is collected inconsistently
* risky actions are launched without enough structure or review
* findings are drafted later from memory instead of from preserved state

BugBountyOS is designed to reduce that entropy.

Instead of treating the OS as a neutral shell full of tools, it treats the OS as a workflow enforcement layer. The operating system, project model, tool wrappers, evidence handling, and report generation all reinforce the same operating discipline.

⸻

Design Goals

BugBountyOS is built to:

* enforce scope before execution
* preserve evidence as first-class state
* make findings traceable to collected artifacts
* keep operator workflows reproducible
* prefer safe defaults over tool sprawl
* support authorized research, not indiscriminate activity
* turn project state into report-ready outputs

⸻

What Makes BugBountyOS Different

BugBountyOS is not:

* a wallpapered Debian remaster
* a generic “ethical hacking” live ISO
* a random bundle of recon tools
* a thin Kali clone

BugBountyOS is a structured operator environment for authorized bug bounty work.

It is intended to provide:

* a defined workspace model
* typed scope manifests
* policy-aware tool wrappers
* evidence indexing and hashing
* notes and hypotheses tied to project state
* finding drafts linked to artifacts
* report generation from structured data

In short:

Kali-style distributions optimize for tool access.
BugBountyOS optimizes for controlled research flow.

⸻

How It Differs from Kali

	Kali	BugBountyOS
Optimized for	Tool breadth	Controlled research flow
Scope enforcement	Manual	Machine-readable manifest
Evidence handling	Ad hoc	Automatic indexing and hashing
Workflow model	General-purpose toolkit	Structured project lifecycle
Primary user model	Broad security work	Authorized bug bounty operators

BugBountyOS does not try to replace Kali’s coverage. It provides structure around a curated, workflow-oriented toolset.

⸻

Core Principles

Scope First

Every project begins with an explicit scope manifest.

Targets, exclusions, allowed actions, and constraints are defined before execution. Wrapped tools can inspect that manifest and refuse, warn, or constrain execution based on policy.

Evidence by Default

Artifacts should not disappear into terminal history.

BugBountyOS is designed to capture logs, screenshots, responses, hashes, and tool metadata in a consistent project structure so findings can be traced back to their source.

Workflow Over Tool Sprawl

The project is not trying to ship every possible offensive utility.

It focuses on the minimum useful set of curated tools needed to support a disciplined bug bounty workflow.

Safer Execution

Potentially noisy or risky actions should be explicit, gated, and reviewable.

BugBountyOS is designed to encourage bounded, authorized testing rather than loose, unstructured execution.

Report-Ready State

Notes, evidence, observations, and findings should accumulate into usable report artifacts instead of becoming a forensic excavation six hours later.

⸻

Architecture

BugBountyOS is built as a Debian derivative with five major layers.

1. Distro Layer

Provides the Debian base, ISO build profile, package sources, branding, and release mechanics.

2. Platform Layer

Provides shared defaults, workspace conventions, CLI entry points, state paths, and package structure.

3. Workflow Layer

Implements the bug bounty lifecycle through project initialization, scope handling, assets, notes, evidence capture, findings, and reports.

4. Execution Layer

Exposes selected security tools through wrapped execution paths and curated profiles rather than relying on raw, unstructured invocation.

5. Policy Layer

Enforces scope checks, action-class restrictions, and trust boundaries between trusted configuration and untrusted target-derived data.

⸻

Project Status

Early build phase. v0.1 is the first milestone.

The v0.1 target is to provide a Debian-based bootable image that can:

* initialize a structured project workspace
* validate a scope manifest
* run a small set of wrapped recon actions against authorized targets
* capture and hash evidence automatically
* create finding drafts linked to evidence
* generate a report skeleton from project state

⸻

Planned Workflow

Full ISO, APT repository, and install instructions land with v0.1.

# Initialize a project
bbos init example-program
# Validate your scope manifest
bbos scope validate scope/scope.yml
# Import targets
bbos asset import domains domains.txt
# Run a wrapped recon action
bbos run recon httpx --targets assets/domains.txt
# Capture evidence
bbos evidence add screenshots/homepage.png --kind screenshot --target app.example.com
# Create a finding draft
bbos finding create open-redirect
# Build a report
bbos report build

The point is not command novelty. The point is that execution, evidence, and reporting all live inside the same structured project model.

⸻

Workspace Model

Every project follows a defined layout:

/workspaces/<project_slug>/
  project.yml
  scope/
    scope.yml
    exclusions.yml
  assets/
    domains.txt
    subdomains.txt
    urls.txt
    hosts.txt
    services.json
  notes/
    hypotheses.md
    observations.md
    timeline.md
  evidence/
    screenshots/
    responses/
    logs/
    attachments/
    hashes/
    index.json
  findings/
    drafts/
    submitted/
  reports/
    technical/
    executive/
  state/
    assets.json
    tool_runs.jsonl
    decisions.jsonl
    evidence.jsonl
    findings.json

This structure is intentional. Bug bounty workflows generate fragmented state. BugBountyOS is designed to make that state legible, portable, and reviewable.

⸻

Scope Manifest

Every project starts with a typed scope manifest:

version: 1
program:
  name: "Example Program"
  platform: "HackerOne"
  handle: "example"
targets:
  include:
    - "*.example.com"
    - "api.example.com"
  exclude:
    - "admin.example.com"
    - "*.internal.example.com"
actions:
  allowed:
    - passive_recon
    - web_enum
    - screenshot_capture
    - safe_http_probe
  restricted:
    - aggressive_fuzzing
    - auth_bruteforce
constraints:
  rate_limit: "low"
  notes:
    - "No testing against payment flows"
    - "No authenticated testing without explicit approval"
timebox:
  start: "2026-05-08T00:00:00Z"
  end: "2026-05-30T23:59:59Z"

Wrapped tools read this manifest before executing. Out-of-scope targets are blocked. Restricted actions require an explicit override path.

⸻

Command Reference

bbos init             Initialize a project workspace
bbos scope validate   Validate a scope manifest
bbos scope show       Display active scope
bbos asset import     Import targets into structured state
bbos asset list       List known assets
bbos note add         Append to notes
bbos hypothesis add   Record a testable hypothesis
bbos run              Execute a wrapped tool
bbos evidence add     Manually add an artifact
bbos evidence hash    Hash and index a file
bbos finding create   Create a finding draft
bbos report build     Compile a report from project state
bbos status           Project summary
bbos doctor           Environment health check

The CLI is the primary control surface for the MVP. A richer TUI or desktop console can come later, once the foundations stop moving underfoot.

⸻

Package Layout

The planned package model is:

bugbountyos-base            System defaults, shared paths, shell profile
bugbountyos-branding        Identity, motd, release metadata
bugbountyos-cli             Main bbos entry point and subcommands
bugbountyos-scope           Manifest parser, schema validation, policy engine
bugbountyos-workspace       Project init, template generation, state management
bugbountyos-evidence        Artifact storage, hashing, indexing
bugbountyos-reporting       Finding templates, report generation
bugbountyos-guardrails      Risky-command wrappers, action-class enforcement
bugbountyos-recon           Curated recon tools and wrappers
bugbountyos-web             Browser stack, proxy tooling, API helpers
bugbountyos-control-center  CLI/TUI operator console

Each package is meant to own a distinct part of the system so the project does not collapse into one giant maintenance swamp.

⸻

Execution Model

Wrapped execution is the core enforcement path.

A typical bbos run flow is expected to look like this:

user request
  → tool alias lookup
  → action class resolution
  → target normalization
  → scope check
  → policy check
  → command render
  → execution
  → output capture
  → metadata logging
  → artifact indexing

This is how the project encodes governance into execution rather than burying it in documentation nobody reads once packets start moving.

⸻

Evidence Model

Artifacts are treated as first-class project objects.

Evidence may include:

* screenshots
* HTTP responses
* logs
* command outputs
* attachments
* hashes
* timestamps
* target linkage
* source tool metadata

The purpose is straightforward: findings should be reconstructable from preserved state, not from operator memory.

⸻

Reporting Model

BugBountyOS is intended to accumulate enough structure during execution that reporting becomes compilation rather than improvisation.

A finding draft should ultimately be able to reference:

* title
* target
* hypothesis
* observed behavior
* impact notes
* reproduction steps
* linked evidence
* severity estimate
* current status

The workflow should end in report-ready artifacts, not a pile of disconnected terminal transcripts and a worsening mood.

⸻

Security Posture

BugBountyOS is designed around explicit trust boundaries:

* signed packages and repository metadata
* strict manifest parsing
* scope-aware tool wrappers with hard block on out-of-scope targets
* hash-based evidence integrity
* append-only state logs where feasible
* unprivileged default operator workflows
* separation of trusted configuration from target-derived data
* minimal implicit trust in tool output

This is a security environment. Trust should be engineered, not assumed because something printed green text and sounded confident.

⸻

Threat Model

The initial project threat model includes:

* operator error
* scope drift
* dangerous tool execution against unauthorized targets
* malformed or hostile target-derived data
* evidence tampering after collection
* untrusted command output contaminating notes or reports
* supply-chain risk in package and release infrastructure

BugBountyOS is intended to reduce these risks through policy-aware execution, structured storage, and clearer system boundaries.

⸻

Build Philosophy

BugBountyOS should be:

* boring at the base
* strict at the boundaries
* useful in the workflow
* explicit about trust
* disciplined about scope

The distro is not the product by itself.

The workflow is the product.
The distro is the delivery mechanism.

⸻

Roadmap

v0.1

* Debian-based bootable image
* core CLI
* scope manifest validation
* structured workspace initialization
* wrapped recon commands for a small curated toolset
* automatic evidence hashing and indexing
* finding draft support
* report skeleton generation

v0.2

* stronger policy engine
* richer evidence linking
* asset graph support
* safer browser and container isolation
* better reporting templates

v0.3+

* control center / TUI
* AI-assisted summarization constrained by local evidence
* encrypted project export bundles
* optional team-oriented workflows
* containerized high-risk execution paths

⸻

What v0.1 Will Not Do

To keep the project from becoming a cosplay convention for unfinished ambition, v0.1 will not attempt to:

* replace Kali in breadth of tooling
* ship every offensive utility available
* build a full custom desktop environment
* require a complex AI agent stack for core usability
* solve team collaboration before the single-operator workflow is solid

BugBountyOS starts with operator workflow first.

⸻

Intended Audience

BugBountyOS is intended for:

* independent bug bounty researchers
* structured operators who want reproducible project state
* builders who care about evidence integrity and reporting flow
* teams evaluating whether the workflow can later be extended into shared infrastructure

It is not intended as a general-purpose “hacker distro” for anyone who wants a themed desktop and 800 tools they do not understand.

⸻

Contributing

Contributions are welcome, especially in:

* Debian packaging and live-build
* CLI and scope engine implementation
* evidence handling and artifact indexing
* report generation and finding templates
* reproducible build workflows
* operator UX for structured security research

Contribution guidelines will be published as the repository structure stabilizes.

⸻

Documentation

* docs/architecture.md￼ — system design and layer breakdown
* docs/manifests.md￼ — scope manifest schema and policy engine
* docs/roadmap.md￼ — versioned milestone plan
* docs/threat-model.md￼ — trust boundaries and initial threat assumptions

⸻

License

[Insert license]

⸻

Long-Term Direction

BugBountyOS is intended to become a research environment where:

* authorized scope is machine-readable
* execution is policy-aware
* evidence is preserved automatically
* findings emerge from artifacts, not memory
* reports are generated from structured state
* trust boundaries remain explicit throughout the system

Not more tools.

Better structure.
