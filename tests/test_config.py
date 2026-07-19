from pathlib import Path

import pytest

from recoverops.config import ProjectPaths, read_env_file


def test_artifact_boundary_accepts_generated_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("RECOVEROPS_ROOT", str(tmp_path))
    paths = ProjectPaths.discover()
    paths.ensure_generated_directories()

    assert paths.require_artifact_path(paths.backup / "database.dump").is_relative_to(
        paths.artifacts
    )


def test_artifact_boundary_rejects_outside_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("RECOVEROPS_ROOT", str(tmp_path))
    paths = ProjectPaths.discover()

    with pytest.raises(ValueError, match="outside the artifacts boundary"):
        paths.require_artifact_path(tmp_path.parent / "unsafe")


def test_read_env_file_ignores_comments(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("# comment\nONE=1\n\nTWO=value=with=equals\n", encoding="utf-8")

    assert read_env_file(env_file) == {"ONE": "1", "TWO": "value=with=equals"}
