from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ProjectPaths:
    root: Path
    artifacts: Path
    backup: Path
    reports: Path
    restic_repository: Path
    restore: Path
    state: Path
    secrets: Path

    @classmethod
    def discover(cls) -> ProjectPaths:
        configured = os.getenv("RECOVEROPS_ROOT")
        root = (
            Path(configured).expanduser().resolve()
            if configured
            else Path(__file__).resolve().parents[2]
        )
        artifacts = root / "artifacts"
        return cls(
            root=root,
            artifacts=artifacts,
            backup=artifacts / "backup",
            reports=artifacts / "reports",
            restic_repository=artifacts / "restic-repo",
            restore=artifacts / "restore",
            state=artifacts / "state",
            secrets=root / ".secrets",
        )

    def ensure_generated_directories(self) -> None:
        for path in (
            self.backup,
            self.reports,
            self.restic_repository,
            self.restore,
            self.state,
            self.secrets,
        ):
            path.mkdir(parents=True, exist_ok=True)

    def require_artifact_path(self, path: Path) -> Path:
        resolved = path.resolve()
        if not resolved.is_relative_to(self.artifacts.resolve()):
            raise ValueError(f"path is outside the artifacts boundary: {resolved}")
        return resolved


def read_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values
