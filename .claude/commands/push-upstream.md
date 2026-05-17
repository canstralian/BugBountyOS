---
description: Push a local vector's changes back to its upstream source repo via git subtree push
argument-hint: [vector-name]
allowed-tools: [Read, Bash]
---

# push-upstream

Push local changes in a BugBountyOS vector back to its upstream source repository using `git subtree push`.

Vectors in this project are git subtrees — edits made locally in `vectors/` do not flow back automatically. This skill constructs and optionally runs the correct `git subtree push` command for a named vector.

## Input

The user invoked this skill with: $ARGUMENTS

## Instructions

1. **Parse the argument.** If `$ARGUMENTS` is empty, read `control-plane/registry/vectors.yaml` and list all vectors that have a `source_repo` field, then ask the user which one to push.

2. **Look up the vector.** Read `control-plane/registry/vectors.yaml`. Find the entry where `id` matches the argument (case-insensitive). Extract:
   - `id` → the vector name (used as the subtree prefix path `vectors/<id>`)
   - `source_repo` → the GitHub repo slug (e.g. `canstralian/BugBountyPipeline`)
   - `trust_level` → if `tainted`, warn the user before proceeding

3. **Check for uncommitted changes.** Run `git status --short vectors/<id>/`. If there are staged-but-not-committed changes, tell the user to commit them first and stop.

4. **Show the command.** Display the exact command that will be run:
   ```
   git subtree push --prefix=vectors/<id> https://github.com/<source_repo> main
   ```
   Explain that this replays all commits touching `vectors/<id>` onto the upstream `main` branch. Warn that this requires push access to `<source_repo>`.

5. **Confirm.** Ask the user to confirm before running. Do not execute without explicit confirmation.

6. **Execute.** On confirmation, run:
   ```bash
   git subtree push --prefix=vectors/<id> https://github.com/<source_repo> main
   ```
   Stream output. If it fails (e.g. non-fast-forward), explain the cause and suggest the recovery path:
   - Non-fast-forward: the upstream has diverged — the user needs to pull upstream changes back into BugBountyOS first with `git subtree pull --prefix=vectors/<id> https://github.com/<source_repo> main --squash`, resolve any conflicts, then retry.

7. **Report.** On success, confirm which vector was pushed, the upstream repo, and remind the user that the local `vectors/<id>` subtree and the upstream are now in sync.
