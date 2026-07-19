# Contributing

## Development setup

```bash
./scripts/bootstrap.sh
./scripts/lab.sh doctor
./scripts/lab.sh test
```

Use a focused branch for each change. Keep source changes, tests, and documentation in
the same pull request when they describe one behavior.

## Pull request checks

- New behavior has a test or a named live check.
- Error paths are exercised, not only the successful path.
- Destructive code validates its exact target and requires explicit approval.
- Secrets and generated evidence remain ignored.
- `./scripts/lab.sh test` passes.
- Operator-facing behavior is reflected in the README or operations guide.

## Live workflow changes

Changes to backup, disaster, restore, or verification behavior should be tested with:

```bash
./scripts/lab.sh rehearse --apply
./scripts/lab.sh report
./scripts/lab.sh down
```

Do not use real infrastructure, credentials, or production data in this repository.
