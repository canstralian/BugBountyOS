# Security Policy

## Scope

BugBountyOS is an operating environment for **authorized** bug bounty and
security research. Anything pushed to this repository is expected to comply
with the project's scope-first / evidence-first principles.

## Supported Versions

This project is pre-1.0. Only the `main` branch receives security fixes.

## Reporting a Vulnerability

If you discover a security issue in the **BugBountyOS code itself** (not in a
target you are researching with it), please:

1. **Do not** open a public issue.
2. Email the maintainer or open a private GitHub Security Advisory via the
   "Security" tab on this repository.
3. Include reproduction steps, affected versions, and proposed remediation if
   you have one.

We aim to acknowledge reports within 5 business days.

## Out of Scope

- Vulnerabilities that require already-compromised credentials, environments,
  or systems.
- Social engineering of project maintainers.
- DoS / volumetric attacks against project infrastructure.

## Hardening Defaults

This repository ships with the following automated quality gates:

- `ruff` (lint + format)
- `mypy` (static type-check)
- `bandit` (Python static security)
- `pip-audit` (dependency vulnerability scan)
- `gitleaks` (committed-secret scan, pre-commit + CI)
- CodeQL (security-extended queries) on push, PR, and weekly schedule
- GitHub `dependency-review-action` on every PR

If you bypass any of these gates locally, please flag it in the PR description.
