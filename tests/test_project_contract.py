from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_required_entrypoints_exist() -> None:
    for relative in (
        "compose.yml",
        "scripts/bootstrap.sh",
        "scripts/lab.sh",
        "src/recoverops/cli.py",
        "ansible/playbooks/backup.yml",
        "ansible/playbooks/seed.yml",
        "ansible/playbooks/disaster.yml",
        "ansible/playbooks/restore.yml",
        "app/Dockerfile",
        "docs/PROJECT_PLAN.md",
    ):
        assert (ROOT / relative).is_file(), relative


def test_compose_ports_are_loopback_only() -> None:
    compose = yaml.safe_load((ROOT / "compose.yml").read_text(encoding="utf-8"))

    for service in compose["services"].values():
        for port in service.get("ports", []):
            assert port.startswith("127.0.0.1:"), port


def test_generated_secrets_are_ignored() -> None:
    patterns = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()

    assert ".env" in patterns
    assert ".secrets/" in patterns
    assert "artifacts/restic-repo/*" in patterns
