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
