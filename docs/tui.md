# Workspace TUI

A read-only Textual dashboard over the BugBountyOS workflow plane:

    Scope -> Assets -> Inputs -> Findings -> Reports

The TUI never mutates state. It is a window onto the authoritative YAML in
`control-plane/registry/vectors.yaml` and `contracts/*.yaml`. To change
scope or contract status, edit those files directly (they are base64-encoded
on disk; see `CLAUDE.md`).

## Install

    pip install -e '.[tui]'

or, for the existing dev workflow:

    pip install -r requirements-dev.txt
    pip install -e .

## Launch

    bbos tui
    # or
    bbos-tui
    # or
    python -m bbos tui

## Views

| Tab      | Source                                       | Shows                              |
| -------- | -------------------------------------------- | ---------------------------------- |
| Scope    | `control-plane/registry/vectors.yaml`        | Authorized vectors + lifecycle     |
| Assets   | `contracts/*.yaml` -> `interfaces.output`    | Output types produced per vector   |
| Inputs   | `contracts/*.yaml` -> `interfaces.input`     | Input types consumed per vector    |
| Findings | `contracts/*.yaml` -> `gates`                | Per-vector gate status (5 gates)   |
| Reports  | aggregated                                   | Lifecycle and gate roll-up         |

## Keys

| Key   | Action                |
| ----- | --------------------- |
| 1..5  | Switch tab            |
| q     | Quit                  |
