from __future__ import annotations

import shutil
import subprocess
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
