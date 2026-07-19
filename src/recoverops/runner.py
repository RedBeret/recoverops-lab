from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
from collections.abc import Sequence
from pathlib import Path


def run(
    command: Sequence[str],
    *,
    cwd: Path,
    check: bool = True,
    capture_output: bool = False,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(command),
        cwd=cwd,
        check=check,
        text=True,
        capture_output=capture_output,
    )


def compose_command() -> list[str]:
    docker = shutil.which("docker")
    if docker:
        result = subprocess.run(
            [docker, "compose", "version"],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if result.returncode == 0:
            return [docker, "compose"]
    legacy = shutil.which("docker-compose")
    if legacy:
        return [legacy]
    raise RuntimeError("Docker Compose v1 or v2 is required")


def compose_base(root: Path) -> list[str]:
    return [*compose_command(), "-p", "recoverops", "-f", str(root / "compose.yml")]


def ansible_playbook(root: Path, playbook: str) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment["ANSIBLE_CONFIG"] = str(root / "ansible.cfg")
    return subprocess.run(
        [
            str(root / ".venv/bin/ansible-playbook"),
            str(root / "ansible/playbooks" / playbook),
            "--extra-vars",
            json.dumps({"recoverops_root": str(root)}),
        ],
        cwd=root,
        env=environment,
        check=True,
        text=True,
    )


def wait_for_container_health(name: str, timeout_seconds: int = 120) -> None:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        result = subprocess.run(
            ["docker", "inspect", "--format", "{{.State.Health.Status}}", name],
            check=False,
            text=True,
            capture_output=True,
        )
        status = result.stdout.strip()
        if result.returncode == 0 and status == "healthy":
            print(f"ok healthy container {name}")
            return
        if status == "unhealthy":
            raise RuntimeError(f"container became unhealthy: {name}")
        time.sleep(2)
    raise RuntimeError(f"timed out waiting for healthy container: {name}")
