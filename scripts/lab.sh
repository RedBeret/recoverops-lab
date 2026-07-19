#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ ! -x "$root/.venv/bin/recoverctl" ]]; then
  echo "Missing project environment. Run ./scripts/bootstrap.sh first." >&2
  exit 1
fi

cd "$root"
exec "$root/.venv/bin/recoverctl" "$@"
