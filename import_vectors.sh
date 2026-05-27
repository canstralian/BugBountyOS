#!/bin/bash
# BugBountyOS Vector Import Utility (v2.0)
set -euo pipefail

EXECUTE=${EXECUTE:-0}

VECTORS=(
  "dashboard:https://github.com/canstralian/BugBountyBot"
  "pipeline:https://github.com/canstralian/BugBountyPipeline"
  "storage:https://github.com/canstralian/BugBountyManager"
)

echo "--- BugBountyOS Kernel: Vector Loading ---"

for entry in "${VECTORS[@]}"; do
  NAME="${entry%%:*}"
  URL="${entry#*:}"

  if [[ ! "$URL" =~ ^https:// ]]; then
    echo "[KERNEL] Refusing to load '$NAME': invalid URL '$URL'" >&2
    exit 1
  fi

  echo "[KERNEL] Loading module: $NAME from $URL"
  if [ "$EXECUTE" -eq 1 ]; then
    git subtree add --prefix="vectors/$NAME" "$URL" "${BRANCH:-main}" --squash || {
      echo "[KERNEL] Failed to load '$NAME' from '$URL'" >&2
      exit 1
    }
  else
    echo "[DRY-RUN] git subtree add --prefix='vectors/$NAME' '$URL' main --squash"
  fi
done

echo "--- Kernel Load Complete ---"
