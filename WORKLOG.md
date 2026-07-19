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

## 2026-07-18 - Stage 3

- Added a deterministic PostgreSQL schema with four owners, six assets, and twelve
  maintenance events.
- Added canonical schema, row-count, and data fingerprints with atomic JSON writes.
- Added Ansible seed and backup roles plus playbooks.
- Added a custom-format `pg_dump`, SHA-256 manifest generation, and pre-encryption
  verification.
- Added containerized restic 0.19.0 repository initialization, tagged snapshots, and a
  100 percent repository data read after every backup.
- The first live restic backup exposed an unwritable default cache location for the
  remapped WSL UID. The container now uses an ephemeral cache under `/tmp`, and command
  failures surface the underlying stderr.
- Verified deterministic fingerprints across two resets, healthy source API output,
  two successful encrypted snapshots, complete restic integrity checks, and no known
  source hostname appearing in repository bytes.
- Verified 15 tests, Ruff, both Ansible syntax checks, and the Ansible production lint
  profile.

Next: add the explicit disaster approval gate and restore the latest verified snapshot
into the isolated recovery database.

## 2026-07-18 - Stage 4

- Added exact Docker Compose project and service label validation before database
  destruction or recovery changes.
- Added a `disaster` command that exits with code 2 unless `--apply` is supplied.
- Added Ansible disaster and restore roles with guarded blocks, failure recording, and
  target validation.
- Added restic restoration into a project-bound temporary directory and manifest
  verification before the recovery database is touched.
- Verified live that the missing approval leaves the source API healthy and unchanged.
- Verified live database removal, primary API degradation, isolated restore, recovery
  API health, and exact source-to-recovery schema, data, and row-count hashes.
- The evidence read-back found that completion events overwrote their start times. State
  events now preserve separate start, completion, and failure timestamps for RTO
  calculation.
- Verified 20 tests, Ruff, both new Ansible syntax checks, and the Ansible production
  lint profile.

Next: turn the raw fingerprints and timestamps into explicit recovery evidence, add a
repeatable rehearsal command, and prove modified dump rejection before `pg_restore`.

## 2026-07-18 - Stage 5

- Added source database recreation so the lab can repeat after intentional data loss.
- Added the gated `rehearse --apply` command for the complete up, seed, backup,
  disaster, restore, verify, and report lifecycle.
- Added recovery comparison and evidence generation for schema hash, data hash, row
  counts, PostgreSQL version, expected API states, RTO, restore duration, and backup age.
- Added JSON evidence for automation and a human-readable Markdown report.
- Verified a complete repeat rehearsal from a missing source database. The report passed
  with a 32.154-second measured RTO and a 12.114-second restore duration on this WSL host.
- Modified the restored dump after recovery, confirmed checksum rejection with exit code
  2, and proved the recovery database fingerprints remained unchanged.
- Re-restored the encrypted artifact and confirmed its manifest was valid after the
  negative test.
- Added contract coverage requiring repository preflight and manifest verification before
  the recovery database is replaced.
- Verified 28 tests, Ruff, Ansible syntax, and the Ansible production lint profile.

Next: complete CI, the operator-focused README, contribution and security guidance, and
release metadata before a clean acceptance run.

## 2026-07-18 - Stage 6

- Replaced the placeholder README with the complete native WSL workflow, architecture,
  safety model, evidence definitions, endpoints, testing guide, and production boundary.
- Added an operations guide, changelog, contribution guide, security policy, code of
  conduct, and MIT license.
- Added fast pull-request CI plus a separate scheduled and manually dispatched live
  recovery rehearsal that uploads evidence artifacts.
- Added grouped Dependabot updates, an issue form, and a pull request template.
- Expanded `lab.sh test` to include Ruff formatting, every Ansible syntax check, and the
  Ansible production lint profile.
- Added a contract test that verifies every local README link resolves.
- Verified 29 tests, the complete local validation command, Actionlint, ShellCheck,
  Compose rendering, and clean whitespace checks.

Next: run the release candidate from a clean generated state, review the repository as a
skeptical operator, then set the final version only if all acceptance criteria pass.

## 2026-07-18 - Stage 7

- Removed the generated RecoverOps containers and volumes, then cloned the committed
  release candidate into a clean temporary WSL directory.
- Verified bootstrap, diagnostics, 29 tests, Ruff formatting and linting, five Ansible
  syntax checks, and the Ansible production lint profile from the clean clone.
- Confirmed the rehearsal refuses to run without `--apply` and exits with code 2 before
  making changes.
- Ran the complete approved rehearsal and received a passing evidence report with a
  21.781-second RTO, 10.41-second restore duration, and 47.479-second backup age.
- Confirmed the source API returned 503 after the controlled failure, the recovery API
  returned 200, and schema, data, row counts, and PostgreSQL version matched exactly.
- Verified the disposable volumes carried the `recoverops` project label before removing
  them, removed the temporary clone, and confirmed KubeDrift was still the only running
  container.
- Promoted the project to version 1.0.0 only after the clean acceptance criteria passed.

Next: publish the repository and use focused pull requests for future capabilities such
as object storage, physical backups, point-in-time recovery, and recovery trend reports.
