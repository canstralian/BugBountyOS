---

[![CI](https://github.com/canstralian/BugBountyOS/actions/workflows/ci.yml/badge.svg)](https://github.com/canstralian/BugBountyOS/actions/workflows/ci.yml)

[![ISO Build](https://github.com/canstralian/BugBountyOS/actions/workflows/build-iso.yml/badge.svg)](https://github.com/canstralian/BugBountyOS/actions/workflows/build-iso.yml)

A Debian-based operating environment for authorized bug bounty and security research.

> Bug bounty work should be **scoped, auditable, evidence-first, and report-ready by default.**
> 

BugBountyOS treats the operating system as a workflow plane for the full research lifecycle:

```
Scope → Asset Graph → Input Map → Hypotheses → Validated Findings → Report Artifacts
```

This is not a generic pentesting distro. It is a structured operator environment designed to enforce research discipline at the OS level.

---

## Overview

BugBountyOS is designed around a simple idea: *tools don’t create outcomes — workflows do.*  

The OS should help you:

- prove authorization and scope at every step
- generate evidence as you work (not later)
- keep findings traceable and reproducible
- ship report-ready artifacts with minimal friction

---

## Core Principles

### Scope First

# BugBountyOS

Scope is not a note you remember — it’s an enforced constraint.

- Make scope explicit before recon begins
- Treat “out of scope” as a hard failure mode
- Record the scope source (program page, contract, email, ticket, etc.)

### Evidence by Default

If it’s not captured, it didn’t happen.

- Prefer tooling and defaults that write to an evidence store automatically
- Preserve raw outputs (plus normalized summaries)
- Keep timestamps and provenance

### Workflow Over Tool Sprawl

More tools rarely means better results.

- Standardize the lifecycle and plug tools into it
- Keep a minimal set of opinionated defaults
- Prefer composable primitives over one-off “magic” wrappers

### Safer Execution

Operators make mistakes. Systems should reduce blast radius.

- Containment (namespaces, sandboxing, least privilege)
- Defaults that discourage risky actions
- Clear separation of “recon” vs “exploit-like” tooling

### Report-Ready State

The goal is not “found something interesting.” The goal is “shipped a defensible report.”

- Findings map to evidence bundles
- Reproduction steps are standardized
- Outputs are exportable into common report formats

---

## Workflow Model

The canonical workflow is:

1. **Scope**
2. **Asset Graph**
3. **Input Map**
4. **Hypotheses**
5. **Validated Findings**
6. **Report Artifacts**

### Example (operator view)

```
Scope
  → verify authorization + define targets
Asset Graph
  → enumerate hosts, apps, identities, dependencies
Input Map
  → endpoints, parameters, auth flows, attack surface
Hypotheses
  → “what could be true here?”
Validated Findings
  → reproduce + confirm impact + capture evidence
Report Artifacts
  → write-up + severity + remediation + attachments
```

---

## Architecture (High-Level)

1. **Scope Manifest**: a machine-readable scope definition that travels with a workspace
2. **Workspace Layout**: predictable folders for targets, logs, evidence, and reports
3. **Execution Model**: commands run through wrappers that preserve outputs and metadata
4. **Evidence Store**: raw + normalized artifacts with consistent naming
5. **Report Pipeline**: convert evidence + findings into report-ready deliverables

---

## Workspace Layout

```
workspaces/
  <program-or-client>/
    scope/
      scope.yaml
      notes.md
    assets/
      asset-graph.json
      inventory.csv
    inputs/
      urls.txt
      params.txt
      auth.md
    hypotheses/
      backlog.md
    findings/
      <finding-id>-<short-name>/
        evidence/
        reproduction.md
        impact.md
        remediation.md
    reports/
      report.md
      attachments/
    logs/
      commands.log
      tool-output/
```

---

## Scope Manifest (Example)

```yaml
program:
  name: Example Bug Bounty Program
  source: https://example.com/program-scope

authorization:
  type: bug_bounty
  reference: "Program scope page URL or ticket ID"

in_scope:
  domains:
    - example.com
    - api.example.com
  ip_ranges:
    - 203.0.113.0/24

out_of_scope:
  domains:
    - admin.example.com
  notes:
    - "No testing against production employee systems"
    - "No social engineering"

rules:
  rate_limit:
    requests_per_second: 5
  prohibited_actions:
    - "Denial of service"
    - "Physical attacks"
```

---

## Command Execution (Examples)

### Running a command (capturing output)

```bash
bbos run -- workspace=acme -- command "nuclei -l inputs/urls.txt -o logs/tool-output/nuclei.txt"
```

### Capturing a workspace tree snapshot

```bash
bbos tree -- workspace=acme > logs/workspace-tree.txt
```

### Validating scope before running recon

```bash
bbos scope validate -- workspace=acme
```

---

## Kali Comparison

| Category | Kali Linux | BugBountyOS |
| --- | --- | --- |
| Primary goal | Broad pentesting / training distro | Bug bounty / security research workflow plane |
| Defaults | Tool availability | Evidence + auditability + report readiness |
| Structure | User-defined | Opinionated workspace + lifecycle |
| Scope enforcement | Manual / process | Manifest-driven + workflow gates (planned) |
| Output handling | Depends on operator | Capture-first wrappers + standardized artifacts |
| Reporting | External / manual | Built-in artifact pipeline (planned) |

---

## Roadmap (High-Level)

### Phase 1 — Foundations

- ISO build pipeline
- Base packages + operator ergonomics
- Standard workspace structure

### Phase 2 — Workflow Enforcement

- Scope manifest validation and gating
- Command wrapper that captures output, timestamp, and metadata
- Evidence bundle generation per finding

### Phase 3 — Report Pipeline

- Findings → report template export
- Attachment packaging and integrity checks
- Optional integrations (Notion, GitHub Issues, etc.)

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.