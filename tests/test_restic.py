from pathlib import Path

from recoverops.config import ProjectPaths
from recoverops.restic import restic_base


def test_restic_container_uses_ephemeral_cache_without_secret_value(tmp_path: Path) -> None:
    paths = ProjectPaths(
        root=tmp_path,
        artifacts=tmp_path / "artifacts",
        backup=tmp_path / "artifacts/backup",
        reports=tmp_path / "artifacts/reports",
        restic_repository=tmp_path / "artifacts/restic-repo",
        restore=tmp_path / "artifacts/restore",
        state=tmp_path / "artifacts/state",
        secrets=tmp_path / ".secrets",
    )
    paths.ensure_generated_directories()
    (paths.secrets / "restic-password").write_text("do-not-leak-this-value\n", encoding="utf-8")

    command = restic_base(paths)

    assert "XDG_CACHE_HOME=/tmp/restic-cache" in command
    assert "do-not-leak-this-value" not in command
    assert str(paths.secrets / "restic-password") in " ".join(command)
