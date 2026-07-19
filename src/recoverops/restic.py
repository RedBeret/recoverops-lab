from __future__ import annotations

import json
import os
import subprocess
from typing import Any

from recoverops.config import ProjectPaths, read_env_file
from recoverops.evidence import write_json


def restic_base(paths: ProjectPaths) -> list[str]:
    values = read_env_file(paths.root / ".env")
    image = values.get("RESTIC_IMAGE", "restic/restic:0.19.0")
    password_file = paths.secrets / "restic-password"
    if not password_file.is_file():
        raise FileNotFoundError(f"missing restic password file: {password_file}")
    return [
        "docker",
        "run",
        "--rm",
        "--user",
        f"{os.getuid()}:{os.getgid()}",
        "--env",
        "RESTIC_REPOSITORY=/repo",
        "--env",
        "RESTIC_PASSWORD_FILE=/run/secrets/restic-password",
        "--env",
        "XDG_CACHE_HOME=/tmp/restic-cache",
        "--volume",
        f"{paths.restic_repository}:/repo",
        "--volume",
        f"{paths.backup}:/backup:ro",
        "--volume",
        f"{paths.restore}:/restore",
        "--volume",
        f"{password_file}:/run/secrets/restic-password:ro",
        image,
    ]


def run_restic(paths: ProjectPaths, arguments: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [*restic_base(paths), *arguments],
        cwd=paths.root,
        check=True,
        text=True,
        capture_output=True,
    )


def initialize_repository(paths: ProjectPaths) -> dict[str, Any]:
    if (paths.restic_repository / "config").is_file():
        return {"initialized": False, "reason": "repository already exists"}
    result = run_restic(paths, ["init", "--json"])
    payload = json.loads(result.stdout)
    return {"initialized": True, **payload}


def backup_artifacts(paths: ProjectPaths) -> dict[str, Any]:
    result = run_restic(
        paths,
        [
            "backup",
            "/backup/database.dump",
            "/backup/manifest.json",
            "/backup/source-fingerprint.json",
            "--tag",
            "recoverops",
            "--json",
        ],
    )
    records = [json.loads(line) for line in result.stdout.splitlines() if line.strip()]
    summary = next(
        record for record in reversed(records) if record.get("message_type") == "summary"
    )
    write_json(paths.backup / "restic-backup.json", summary)
    return summary


def check_repository(paths: ProjectPaths) -> dict[str, Any]:
    result = run_restic(paths, ["check", "--read-data-subset=100%"])
    payload = {"ok": True, "output": result.stdout.strip()}
    write_json(paths.backup / "restic-check.json", payload)
    return payload
