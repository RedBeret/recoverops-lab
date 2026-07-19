from __future__ import annotations

import subprocess
from typing import Any

from recoverops.safety import assert_container_scope


def ensure_recoverops_database(container: str, service: str) -> dict[str, Any]:
    assert_container_scope(container, service)
    query = "SELECT 1 FROM pg_database WHERE datname = 'recoverops';"
    result = subprocess.run(
        [
            "docker",
            "exec",
            container,
            "psql",
            "--username",
            "recoverops",
            "--dbname",
            "postgres",
            "--tuples-only",
            "--no-align",
            "--command",
            query,
        ],
        check=True,
        text=True,
        capture_output=True,
    )
    if result.stdout.strip() == "1":
        return {"created": False, "database": "recoverops", "container": container}
    subprocess.run(
        [
            "docker",
            "exec",
            container,
            "createdb",
            "--username",
            "recoverops",
            "--owner",
            "recoverops",
            "recoverops",
        ],
        check=True,
        text=True,
    )
    return {"created": True, "database": "recoverops", "container": container}
