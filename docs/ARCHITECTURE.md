# Architecture

## Components

| Component | Responsibility |
| --- | --- |
| `recoverctl` | Operator CLI, approval gates, subprocess orchestration, and status output |
| Ansible playbooks | Backup, disaster, restore, verification, and cleanup workflow |
| `primary-db` | PostgreSQL 17.6 source database |
| `primary-api` | HTTP health and inventory summary backed by the source database |
| `recovery-db` | Isolated PostgreSQL 17.6 recovery target |
| `recovery-api` | HTTP validation endpoint backed by the recovered database |
| restic 0.19.0 | Encrypted repository, snapshots, restoration, and integrity checking |
| Evidence engine | Deterministic fingerprints plus JSON and Markdown recovery reports |

## Recovery flow

```mermaid
flowchart LR
    OP["WSL operator"] --> CLI["recoverctl"]
    CLI --> ANS["Ansible playbooks"]
    ANS --> SRC["Primary PostgreSQL"]
    SRC --> DUMP["Custom-format dump"]
    DUMP --> HASH["SHA-256 manifest"]
    HASH --> RESTIC["Encrypted restic repository"]
    RESTIC --> RESTORE["Isolated recovery database"]
    RESTORE --> VERIFY["Schema, row-count, data, and HTTP checks"]
    VERIFY --> REPORT["JSON and Markdown evidence"]
```

## Data and evidence

The deterministic dataset contains service assets, owners, and maintenance events.
Fingerprints use sorted query results and explicit JSON serialization so the same
logical state produces the same SHA-256 hash regardless of query execution order.

Backup evidence records:

- capture timestamp
- database server version
- schema hash
- per-table row counts
- canonical data hash
- dump checksum and size
- restic snapshot identifier
- restic integrity-check result

Recovery evidence adds:

- restore start and finish timestamps
- measured RTO
- estimated RPO from the source capture time
- recovered fingerprint
- source-to-recovery comparison
- recovery API health result
- overall pass or fail status

## Filesystem boundaries

All generated state lives below `artifacts/`:

```text
artifacts/
  backup/       # current dump, manifest, and source fingerprint
  reports/      # JSON and Markdown evidence
  restic-repo/  # encrypted restic repository
  restore/      # temporary restic restore output
  state/        # workflow timestamps and small state records
```

The bootstrap creates `.env` and `.secrets/restic-password`. Neither is committed.

## Failure handling

Ansible `block`, `rescue`, and `always` sections record failures and remove temporary
restore content. Restic and dump checks must pass before the recovery database is
modified. Verification failures produce evidence and a nonzero exit code.

## Production boundary

This lab demonstrates recovery mechanics and evidence collection. Production designs
must add retention policy, off-host copies, credential management, access controls,
immutable storage, monitoring, capacity testing, and a PostgreSQL backup strategy
appropriate to the required RPO and RTO.
