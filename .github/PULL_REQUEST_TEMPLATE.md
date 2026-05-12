## Summary

<!-- 1-3 bullets describing what changed and why -->

## Type

- [ ] Feature
- [ ] Fix
- [ ] Refactor
- [ ] Docs / chore
- [ ] CI / quality gates

## Quality Gates

- [ ] `ruff check . && ruff format --check .` passes
- [ ] `mypy adapters vectors --exclude vectors/dashboard` passes
- [ ] `pytest` passes with coverage threshold
- [ ] No new secrets, eval/exec, or unsafe shell calls
- [ ] Dependencies pinned where appropriate

## Test Plan

<!-- How was this verified? -->

## Notes for Reviewer

<!-- Anything reviewer should know up front -->
