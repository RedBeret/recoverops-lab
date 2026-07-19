import json
from pathlib import Path

from recoverops.config import ProjectPaths
from recoverops.state import record_event


def test_state_events_preserve_start_and_completion_times(tmp_path: Path) -> None:
    artifacts = tmp_path / "artifacts"
    paths = ProjectPaths(
        root=tmp_path,
        artifacts=artifacts,
        backup=artifacts / "backup",
        reports=artifacts / "reports",
        restic_repository=artifacts / "restic-repo",
        restore=artifacts / "restore",
        state=artifacts / "state",
        secrets=tmp_path / ".secrets",
    )
    paths.ensure_generated_directories()

    record_event(paths, "restore", "started")
    record_event(paths, "restore", "completed")

    payload = json.loads((paths.state / "workflow.json").read_text(encoding="utf-8"))
    restore = payload["events"]["restore"]
    assert restore["status"] == "completed"
    assert restore["started_at"].endswith("Z")
    assert restore["completed_at"].endswith("Z")


def test_starting_a_new_event_clears_stale_completion(tmp_path: Path) -> None:
    artifacts = tmp_path / "artifacts"
    paths = ProjectPaths(
        root=tmp_path,
        artifacts=artifacts,
        backup=artifacts / "backup",
        reports=artifacts / "reports",
        restic_repository=artifacts / "restic-repo",
        restore=artifacts / "restore",
        state=artifacts / "state",
        secrets=tmp_path / ".secrets",
    )
    paths.ensure_generated_directories()
    record_event(paths, "restore", "started")
    record_event(paths, "restore", "completed")

    payload = record_event(paths, "restore", "started")

    restore = payload["events"]["restore"]
    assert restore["status"] == "started"
    assert "completed_at" not in restore
