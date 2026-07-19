import re
import tomllib
from pathlib import Path

import yaml
from recoverops_api.main import app

from recoverops import __version__

ROOT = Path(__file__).resolve().parents[1]


def test_release_versions_match() -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))

    assert project["project"]["version"] == "1.0.0"
    assert __version__ == project["project"]["version"]
    assert app.version == __version__


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
        "ansible/playbooks/verify.yml",
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


def test_bootstrap_rebuilds_a_virtualenv_created_by_another_python() -> None:
    bootstrap = (ROOT / "scripts/bootstrap.sh").read_text(encoding="utf-8")

    assert "configured_executable" in bootstrap
    assert "current_real" in bootstrap
    assert "venv_args=(--clear)" in bootstrap
    assert 'python3 -m venv "${venv_args[@]}" .venv' in bootstrap


def test_restore_verifies_manifest_before_replacing_recovery_database() -> None:
    tasks = yaml.safe_load(
        (ROOT / "ansible/roles/restore/tasks/main.yml").read_text(encoding="utf-8")
    )
    block = next(task for task in tasks if "block" in task)["block"]
    names = [task["name"] for task in block]

    verify_index = names.index("Verify restored artifact checksums before database changes")
    drop_index = names.index("Remove any previous isolated recovery database")
    assert verify_index < drop_index


def test_restore_requires_repository_before_entering_restore_block() -> None:
    tasks = yaml.safe_load(
        (ROOT / "ansible/roles/restore/tasks/main.yml").read_text(encoding="utf-8")
    )
    task_names = [task["name"] for task in tasks]

    assert task_names.index("Require an initialized backup repository") < task_names.index(
        "Restore the latest verified snapshot"
    )


def test_local_readme_links_resolve() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    targets = re.findall(r"\]\((?!https?://|#|mailto:)([^)]+)\)", readme)

    assert targets
    for target in targets:
        assert (ROOT / target).exists(), target
