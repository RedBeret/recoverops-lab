from __future__ import annotations

import json
import subprocess
from typing import Any


class SafetyError(RuntimeError):
    """Raised when a requested lab target is outside the fixed safety boundary."""


def validate_container_scope(metadata: dict[str, Any], name: str, service: str) -> None:
    actual_name = str(metadata.get("Name", "")).lstrip("/")
    labels = metadata.get("Config", {}).get("Labels", {}) or {}
    state = metadata.get("State", {})
    if actual_name != name:
        raise SafetyError(f"container name mismatch: expected {name}, found {actual_name}")
    if labels.get("com.docker.compose.project") != "recoverops":
        raise SafetyError(f"container is outside Compose project recoverops: {name}")
    if labels.get("com.docker.compose.service") != service:
        raise SafetyError(f"container service mismatch: expected {service}")
    if not state.get("Running", False):
        raise SafetyError(f"container is not running: {name}")


def assert_container_scope(name: str, service: str) -> dict[str, Any]:
    result = subprocess.run(
        ["docker", "inspect", name],
        check=True,
        text=True,
        capture_output=True,
    )
    metadata = json.loads(result.stdout)[0]
    validate_container_scope(metadata, name, service)
    return {
        "ok": True,
        "container": name,
        "project": "recoverops",
        "service": service,
    }
