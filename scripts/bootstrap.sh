#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"

for command in python3 docker git; do
  if ! command -v "$command" >/dev/null 2>&1; then
    echo "Missing required command: $command" >&2
    exit 1
  fi
done

if ! docker info >/dev/null 2>&1; then
  echo "Docker is installed but its daemon is not available." >&2
  exit 1
fi

if ! docker compose version >/dev/null 2>&1 && ! docker-compose --version >/dev/null 2>&1; then
  echo "Docker Compose v1 or v2 is required." >&2
  exit 1
fi

venv_args=()
if [[ -f .venv/pyvenv.cfg ]]; then
  configured_executable="$(sed -n 's/^executable = //p' .venv/pyvenv.cfg | head -n 1)"
  configured_real="$(readlink -f -- "$configured_executable" 2>/dev/null || true)"
  current_real="$(python3 -c 'import os, sys; print(os.path.realpath(sys.executable))')"

  if [[ -z "$configured_real" || "$configured_real" != "$current_real" ]]; then
    echo "Python interpreter changed; rebuilding the project virtual environment."
    venv_args=(--clear)
  fi
fi

python3 -m venv "${venv_args[@]}" .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements-dev.txt -e .

mkdir -p \
  .secrets \
  artifacts/backup \
  artifacts/reports \
  artifacts/restic-repo \
  artifacts/restore \
  artifacts/state

if [[ ! -f .env ]]; then
  postgres_password="$(.venv/bin/python -c 'import secrets; print(secrets.token_urlsafe(32))')"
  printf '%s\n' \
    'POSTGRES_USER=recoverops' \
    "POSTGRES_PASSWORD=$postgres_password" \
    'POSTGRES_DB=recoverops' \
    'PRIMARY_DB_PORT=55432' \
    'RECOVERY_DB_PORT=55433' \
    'PRIMARY_API_PORT=18080' \
    'RECOVERY_API_PORT=18081' \
    'POSTGRES_IMAGE=postgres:17.6-alpine' \
    'PYTHON_IMAGE=python:3.12.11-slim' \
    'RESTIC_IMAGE=restic/restic:0.19.0' > .env
fi

if [[ ! -f .secrets/restic-password ]]; then
  .venv/bin/python -c 'import secrets; print(secrets.token_urlsafe(48))' \
    > .secrets/restic-password
fi

chmod 600 .env .secrets/restic-password

echo "Bootstrap complete. Run: ./scripts/lab.sh doctor"
