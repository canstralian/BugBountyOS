```markdown
# BugBountyOS Development Patterns

> Auto-generated skill from repository analysis

## Overview
This skill covers the development patterns and conventions used in the BugBountyOS repository, a Python codebase built with the Flask framework. It documents coding standards, commit practices, and testing patterns to help contributors maintain consistency and quality across the project.

## Coding Conventions

### File Naming
- **Style:** camelCase
- **Example:**  
  - `bugReportHandler.py`
  - `userProfileManager.py`

### Import Style
- **Style:** Relative imports are preferred.
- **Example:**
  ```python
  from .models import BugReport
  from .utils import sendNotification
  ```

### Export Style
- **Style:** Named exports (explicitly listing what is exported).
- **Example:**
  ```python
  __all__ = ['BugReportHandler', 'UserProfileManager']
  ```

### Commit Message Patterns
- **Type:** Conventional commits
- **Prefix:** `chore`
- **Average Length:** 71 characters
- **Example:**
  ```
  chore: update dependencies and fix minor linting issues
  ```

## Workflows

_No automated workflows detected in this repository._

## Testing Patterns

- **Framework:** Unknown (not detected)
- **File Pattern:** Test files are named with the `.test.ts` suffix, suggesting TypeScript-based tests (possibly for frontend or API contracts).
- **Example:**
  ```
  userProfile.test.ts
  bugReportHandler.test.ts
  ```

## Commands
| Command | Purpose |
|---------|---------|
| /commit-convention | Show commit message guidelines |
| /file-naming | Show file naming conventions |
| /import-style | Show import style examples |
| /export-style | Show export style examples |
| /testing-patterns | Show how tests are organized |
```
