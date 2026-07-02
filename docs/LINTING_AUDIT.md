# Linting Configuration Audit

Branch: `claude/audit-linting-config-0dnDj`

## 1. Scope

Audit of every linting, formatting, and static-analysis surface exercised by
this repository, plus the CI workflows that gate them. Out of scope: the
`vectors/dashboard` subtree, which is a placeholder pending import from a
sister repository per `CLAUDE.md`.

## 2. Inventory

| Surface           | Path                                | Status              |
| ----------------- | ----------------------------------- | ------------------- |
| Python lint       | `ruff check .` in `lint.yml`/`ci.yml` | Configured, defaults |
| Shell lint        | `shellcheck` over `*.sh`            | Configured, defaults |
| Python format     | `ruff format`                       | Not invoked         |
| YAML lint         | (none)                              | Gap                 |
| Markdown lint     | (none)                              | Gap                 |
| TypeScript / ESLint / Prettier | `vectors/dashboard/`   | Out of scope (stub) |
| Tests             | `pytest -q`                         | Configured          |

Python sources (16 files — 13 modules + 3 `__init__.py`):

```text
adapters/airtable/scope_mapper.py
adapters/mcp/server.py
tests/__init__.py
tests/test_repo_structure.py
tests/test_substrate_guardrails.py
vectors/pipeline/{app,models,nlp_processor,routes}.py
vectors/storage/{app,routes}.py
vectors/substrate/__init__.py
vectors/substrate/processor.py
vectors/substrate/guardrails/__init__.py
vectors/substrate/guardrails/{input_scanner,output_validator}.py
```

Shell sources: `import_vectors.sh` (1 file).

## 3. Ground-truth baseline

Captured 2026-06-30 with `ruff 0.15.8`, Python 3.12.

```console
$ ruff check .
All checks passed!

$ ruff check --select E,F,W,I,B,UP --statistics .
16  E501   line-too-long
14  UP006  non-pep585-annotation
 9  I001   unsorted-imports
 8  UP035  deprecated-import
 7  UP045  non-pep604-annotation-optional
 6  W292   missing-newline-at-end-of-file
Found 60 errors. [37 fixable with --fix]

$ ruff format --check .
13 files would be reformatted, 3 files already formatted
```

Interpretation: today's CI exercises only Ruff's stock default selection
(`E4 + E7 + E9 + F`). The headroom between the configured selection and a
more conventional one (`E,F,W,I,B,UP`) is **60 findings** — none blocking
today, all surfaced only if rules are turned on.

## 4. Findings

Severity is operational impact, not rule severity.

### F-1  Ruff has no project config — CI behaviour drifts with Ruff version

**File**: missing `pyproject.toml` / `ruff.toml`.
**Impact**: `ruff check .` runs with whatever Ruff's compiled-in defaults
happen to be in the installed version. A future Ruff bump can silently
add or remove rules without any change in this repo, breaking CI on an
unrelated PR.
**Severity**: High (determinism).
**Remediation in this PR**: added `pyproject.toml` pinning
`target-version = "py312"`, explicit `select = ["E4","E7","E9","F"]`
(matches today's effective behaviour, zero new errors), `line-length = 100`,
and an `extend-exclude` that keeps the dashboard subtree and the
yet-to-be-created `distro/` build directory out of scope.

### F-2  Ruff version not pinned in CI

**File**: `.github/workflows/lint.yml`, `.github/workflows/ci.yml`.
**Impact**: `pip install ruff` resolves to whatever is latest at run time.
Combined with F-1, this means a single Ruff release can cause CI to fail
on a PR that touched no Python.
**Severity**: High (determinism).
**Remediation in this PR**: added `requirements-dev.txt` pinning
`ruff==0.15.8`, `pytest>=8,<9`, `pyyaml>=6,<7`. Both `lint.yml` and
`ci.yml` now install via `pip install -r requirements-dev.txt`. Tool
upgrades become explicit, reviewable commits.

### F-3  Triplicated CI work — three workflows, overlapping jobs

**Files**: `.github/workflows/lint.yml`, `.github/workflows/ci.yml`, `.github/workflows/tests.yml`.
**Observed topology**:
- `.github/workflows/lint.yml` → `ruff check .` + `shellcheck`
- `.github/workflows/ci.yml` → `ruff check .` + `shellcheck` + `pytest`
- `.github/workflows/tests.yml` → `pytest`

Every push/PR to `main` and `develop` runs `ruff` twice, `shellcheck`
twice, and `pytest` twice. Three required-status checks where one suffices.
**Severity**: Medium (cost + clarity, not correctness).
**Remediation**: **not applied here** — collapsing jobs may break branch
protection rules that reference specific check names. Recommended path:
keep `.github/workflows/ci.yml` as the single source of truth and delete
`.github/workflows/lint.yml` and `.github/workflows/tests.yml`, after
first updating any branch protection or required-check configuration.
Owner decision.

### F-4  No formatter gate

**Files**: all Python.
**Impact**: `ruff format --check .` reports 13 of 16 files would
reformat. Code today drifts from any formatter's idea of canonical
output. Choosing a formatter later means a noisy one-shot diff.
**Severity**: Low (cosmetic, not correctness).
**Remediation**: **not applied here** — the choice to adopt
`ruff format` (or skip it) is a policy decision, and applying it would
produce a large mechanical diff that should land in its own commit so
`git blame` survives. The `[tool.ruff.format]` block in `pyproject.toml`
declares the formatter style so that if/when it is run, output is stable.

### F-5  Optional stricter rule selections deferred

**Impact**: 60 findings live behind `select = ["E","F","W","I","B","UP"]`
(of which 37 are auto-fixable). The most common are stale `typing.Dict`
imports (`UP006`/`UP035`) — a real correctness/readability win on
Python 3.12.
**Severity**: Low (current code works).
**Remediation**: **not applied here**. Recommended phased adoption in
`pyproject.toml`:

1. `select = ["E4","E7","E9","F"]` — today's behaviour. (Now pinned.)
2. Add `"I"` (import sorting) → run `ruff check --fix`, commit.
3. Add `"UP"` (pyupgrade) → run `ruff check --fix`, commit.
4. Add `"B"` (bugbear, real defects) → review each manually.
5. Add `"W"`, decide on `E501` (line length) policy.

Each step is one PR, one mechanical fix, no policy drift.

### F-6  YAML files have no linter

**Files**: `contracts/*.yaml`, `control-plane/registry/vectors.yaml`,
`.github/workflows/*.yml`.
**Impact**: invalid YAML in a contract file or a workflow file fails
only at consumer-load time, not at PR review. `CLAUDE.md` calls these
files canonical and base64-encoded in places — schema drift here is
load-bearing.
**Severity**: Medium for `contracts/`, High for workflows.
**Remediation**: **not applied here** — adding `yamllint` is a new
tool surface and a new ignore list. Recommended follow-up: add
`yamllint` to `requirements-dev.txt` with a relaxed config (`line-length:
disable`, `document-start: disable`) and run it in `lint.yml`.

### F-7  Shellcheck severity not pinned

**File**: `.github/workflows/lint.yml`, `.github/workflows/ci.yml`.
**Impact**: Shellcheck's default severity is `style`. New shell scripts
may produce style noise that warrants neither failure nor silence.
**Severity**: Low (one script in tree).
**Remediation**: **not applied here**. Recommended: `shellcheck
--severity=warning` when the script count grows.



### F-8  `.editorconfig` missing

**Impact**: no shared whitespace contract. Editors guess.
**Severity**: Low.
**Remediation in this PR**: added `.editorconfig` declaring LF line
endings, final newline, trim trailing whitespace, 4-space Python, 2-space
JS/TS/YAML/JSON/Markdown, tab Makefile.

## 5. What changed in this PR

| File                              | Change                                              |
| --------------------------------- | --------------------------------------------------- |
| `pyproject.toml`                  | New. Pins Ruff target version, rule selection, line length, excludes, formatter style. |
| `requirements-dev.txt`            | New. Pins `ruff==0.15.8`, `pytest>=8,<9`, `pyyaml>=6,<7`. |
| `.editorconfig`                   | New. Shared whitespace contract.                    |
| `.github/workflows/lint.yml`      | `pip install ruff` → `pip install -r requirements-dev.txt`. |
| `.github/workflows/ci.yml`        | `pip install ruff pytest pyyaml` → `pip install -r requirements-dev.txt`. (Drops the now-redundant `[ -f requirements-dev.txt ]` guard.) |
| `docs/LINTING_AUDIT.md`           | This document.                                      |

No Python source files were modified. No CI job was added or removed.
No new rule fires today; the zero-issue Ruff baseline is preserved.

## 6. Recommended follow-ups (not in this PR)

In priority order:

1. **Decide F-3** — collapse `.github/workflows/lint.yml` /
   `.github/workflows/ci.yml` / `.github/workflows/tests.yml` into one
   workflow. Coordinate with branch protection rules first.
2. **Adopt F-5 in phases** — `I` then `UP` are the cheapest, highest-value
   passes (auto-fixable, modernise stale typing).
3. **F-6** — add `yamllint` for workflows + contracts.
4. **F-4** — decide on `ruff format`. If yes, land the one-shot reformat
   in a dedicated commit and add `ruff format --check .` to
   `.github/workflows/lint.yml`.
5. **TypeScript surface** — when `vectors/dashboard` is imported via
   `import_vectors.sh`, audit its ESLint / Prettier / tsconfig in its own
   PR. The current `package.json` is a one-line stub.
