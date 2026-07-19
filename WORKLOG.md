# Work log

## 2026-07-18 - Stage 1

- Selected the repository name `recoverops-lab`.
- Confirmed native WSL Ubuntu, Python 3.11.9, Git 2.43.0, Docker 29.1.3, and
  Docker Compose v1.29.2.
- Confirmed the project path did not already exist and initialized a new Git repository.
- Confirmed image manifests for PostgreSQL 17.6 Alpine, Python 3.12.11 Slim, and
  restic 0.19.0.
- Chose a logical PostgreSQL dump for v1. Physical backups and PITR remain explicit
  future work.
- Chose an isolated recovery database. Restore will never target the primary database.
- Chose a local encrypted restic repository to keep the first release reproducible and
  license-free; S3-compatible storage is future work.
- KubeDrift remains untouched and running.

Next: build the repository foundation and prove the Compose configuration and baseline
test suite.

## 2026-07-18 - Stage 2

- Added the Python `recoverctl` operator CLI with doctor, up, status, down, and test
  commands.
- Added a Compose v1/v2-compatible lab with separate primary and recovery PostgreSQL
  databases plus matching HTTP services.
- Added a non-root API image and loopback-only host bindings.
- Added an idempotent native WSL bootstrap that creates the virtual environment,
  generated credentials, and artifact directories with restrictive permissions.
- Added baseline API, CLI, boundary, and project-contract tests.
- The first test run caught an invalid FastAPI response-model union; route inference was
  made explicit and the complete suite was rerun.
- Replaced Starlette's deprecated `httpx` test fallback with the supported `httpx2`
  dependency after confirming the behavior in the installed source.
- Verified 11 tests, Ruff, shell syntax, Compose rendering, diagnostics, secret file
  modes, CLI version, and both API image builds.

Next: replace the placeholder database initialization with deterministic data,
fingerprinting, PostgreSQL dump creation, restic encryption, and backup evidence.
