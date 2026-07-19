# Security policy

## Supported version

Security fixes are applied to the current `main` branch and latest release.

## Reporting a vulnerability

Do not open a public issue for a suspected vulnerability that could expose credentials,
permit unsafe host changes, or bypass a destructive-action boundary. Report it privately
to `contact@redberet.dev` with the affected version, reproduction steps, impact, and any
suggested mitigation.

## Lab boundaries

- Use synthetic data only.
- Never commit `.env`, `.secrets/`, database dumps, reports, or restic repository data.
- Do not weaken the `--apply` gate or Compose label checks.
- Do not expose database or API ports beyond loopback by default.
- Treat recovery evidence as operational data even though this repository uses synthetic
  records.

The repository demonstrates recovery controls but is not a production backup or secrets
management product.
