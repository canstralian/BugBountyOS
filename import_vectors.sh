#!/usr/bin/env bash
# BugBountyOS Vector Import Utility (v2.1)

set -euo pipefail

EXECUTE=${EXECUTE:-0}
REGISTRY=${REGISTRY:-control-plane/registry/vectors.yaml}

if [[ ! -f "$REGISTRY" ]]; then
  echo "[KERNEL] Registry not found: $REGISTRY" >&2
  exit 1
fi

mapfile -t VECTORS < <(
  python - "$REGISTRY" <<'PY'
from pathlib import Path
import sys

registry = Path(sys.argv[1])
entries = []
current = {}

for line in registry.read_text(encoding="utf-8").splitlines():
    stripped = line.strip()
    if not stripped or stripped.startswith("#") or stripped == "vectors:":
        continue
    if stripped.startswith("- "):
        if current:
            entries.append(current)
        current = {}
        stripped = stripped[2:].strip()
    if ":" in stripped:
        key, value = stripped.split(":", 1)
        current[key.strip()] = value.strip().strip('"\'')

if current:
    entries.append(current)

for entry in entries:
    vector_id = entry.get("id", "")
    source_repo = entry.get("source_repo", "")
    if vector_id and source_repo:
        print(f"{vector_id}|https://github.com/{source_repo}")
PY
)

echo "--- BugBountyOS Kernel: Vector Loading ---"

for entry in "${VECTORS[@]}"; do
  NAME="${entry%%|*}"
  URL="${entry#*|}"
  TARGET="vectors/$NAME"

  echo "[KERNEL] Loading module: $NAME from $URL"
  if [[ -d "$TARGET" ]]; then
    echo "[SKIP] $TARGET already exists; import is idempotent."
    continue
  fi

  if [[ "$EXECUTE" == "1" ]]; then
    git subtree add --prefix="$TARGET" "$URL" main --squash
  else
    echo "[DRY-RUN] git subtree add --prefix='$TARGET' '$URL' main --squash"
  fi
done

echo "--- Kernel Load Complete ---"
