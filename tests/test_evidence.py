import json
from pathlib import Path

from recoverops.config import ProjectPaths
from recoverops.evidence import (
    canonical_json,
    create_manifest,
    sha256_value,
    verify_manifest,
    write_json,
)


def project_paths(tmp_path: Path) -> ProjectPaths:
    artifacts = tmp_path / "artifacts"
    return ProjectPaths(
        root=tmp_path,
        artifacts=artifacts,
        backup=artifacts / "backup",
        reports=artifacts / "reports",
        restic_repository=artifacts / "restic-repo",
        restore=artifacts / "restore",
        state=artifacts / "state",
        secrets=tmp_path / ".secrets",
    )


def test_canonical_hash_ignores_dictionary_insertion_order() -> None:
    left = {"b": [2, 1], "a": {"value": 3}}
    right = {"a": {"value": 3}, "b": [2, 1]}

    assert canonical_json(left) == canonical_json(right)
    assert sha256_value(left) == sha256_value(right)


def test_manifest_detects_modified_dump(tmp_path: Path) -> None:
    paths = project_paths(tmp_path)
    paths.ensure_generated_directories()
    (paths.backup / "database.dump").write_bytes(b"known database dump")
    write_json(paths.backup / "source-fingerprint.json", {"data_sha256": "abc"})
    manifest = create_manifest(paths)
    write_json(paths.backup / "manifest.json", manifest)

    assert verify_manifest(paths.backup, paths.backup / "manifest.json") == []

    (paths.backup / "database.dump").write_bytes(b"modified database dump")

    errors = verify_manifest(paths.backup, paths.backup / "manifest.json")
    assert "checksum mismatch: database.dump" in errors


def test_json_writer_replaces_file_atomically(tmp_path: Path) -> None:
    destination = tmp_path / "evidence.json"

    write_json(destination, {"ok": True})

    assert json.loads(destination.read_text(encoding="utf-8")) == {"ok": True}
    assert not destination.with_suffix(".json.tmp").exists()
