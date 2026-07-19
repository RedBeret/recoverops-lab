# Operations guide

## Normal rehearsal

```bash
./scripts/bootstrap.sh
./scripts/lab.sh doctor
./scripts/lab.sh rehearse --apply
./scripts/lab.sh report
```

The source database is intentionally absent after a completed rehearsal. This is the
expected end state: the primary API reports degraded while the isolated recovery API
reports healthy. The next `seed` or `rehearse --apply` recreates the source database.

## Preserve or remove state

`./scripts/lab.sh down` removes containers and the Compose network but preserves both
database volumes and the encrypted restic repository.

To start the existing containers again:

```bash
./scripts/lab.sh up
./scripts/lab.sh status
```

Generated artifacts are ignored by Git. If a full local reset is required, first bring
the project down, then remove only the `recoverops` Compose volumes and the repository's
`artifacts/` contents after confirming no evidence must be retained.

## Expected service transitions

| Stage | Primary API | Recovery API |
| --- | ---: | ---: |
| After `seed` | 200 | 503 or 200 from a previous restore |
| After `disaster --apply` | 503 | unchanged |
| After `restore` | 503 | 200 |

## Troubleshooting

### Doctor reports no Docker daemon

Start the Docker service available to the Ubuntu distribution, then rerun:

```bash
docker info
./scripts/lab.sh doctor
```

### Recovery reports do not exist

`report` reads evidence produced by `verify`. Run the missing stage:

```bash
./scripts/lab.sh verify
./scripts/lab.sh report
```

### Restore rejects the manifest

Do not bypass the check. Create a new source backup or restore the latest encrypted
snapshot again. A mismatch means the dump or fingerprint differs from the content that
was hashed before encryption.

### Compose v1 prints a legacy-builder warning

Compose v1 can fall back to Docker's legacy builder when Buildx is unavailable. The lab
supports that path, but upgrading to Docker Compose v2 removes the dependency on the
deprecated v1 client.

## Evidence retention

Reports contain synthetic hostnames and timings but no generated passwords. The restic
repository is encrypted. Keep `.secrets/restic-password` with any repository evidence
that must remain restorable; losing the password makes the repository unusable.
