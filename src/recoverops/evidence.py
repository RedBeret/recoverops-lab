from __future__ import annotations

import hashlib
import json
from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any
from uuid import UUID

import psycopg

from recoverops.config import ProjectPaths, read_env_file

FINGERPRINT_FORMAT_VERSION = 1
MANIFEST_FORMAT_VERSION = 1

TABLE_QUERIES = {
    "owners": "SELECT id, name, team, email FROM owners ORDER BY id",
    "assets": (
        "SELECT id, hostname, environment, owner_id, criticality, created_at "
        "FROM assets ORDER BY id"
    ),
    "maintenance_events": (
        "SELECT id, asset_id, event_type, status, performed_at, notes "
        "FROM maintenance_events ORDER BY id"
    ),
}

SCHEMA_QUERY = """
SELECT table_name, column_name, ordinal_position, data_type, is_nullable,
       COALESCE(column_default, '')
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name IN ('owners', 'assets', 'maintenance_events')
ORDER BY table_name, ordinal_position
"""


def utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def json_value(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.astimezone(UTC).isoformat().replace("+00:00", "Z")
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, (Decimal, UUID)):
        return str(value)
    if isinstance(value, bytes):
        return value.hex()
    return value


def canonical_json(value: Any) -> str:
    return json.dumps(value, default=json_value, sort_keys=True, separators=(",", ":"))


def sha256_value(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(f"{path.suffix}.tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def connection_settings(paths: ProjectPaths, target: str) -> dict[str, Any]:
    values = read_env_file(paths.root / ".env")
    port_key = "PRIMARY_DB_PORT" if target == "primary" else "RECOVERY_DB_PORT"
    return {
        "host": "127.0.0.1",
        "port": int(values.get(port_key, "55432" if target == "primary" else "55433")),
        "dbname": values.get("POSTGRES_DB", "recoverops"),
        "user": values.get("POSTGRES_USER", "recoverops"),
        "password": values.get("POSTGRES_PASSWORD", ""),
        "connect_timeout": 5,
    }


def capture_fingerprint(paths: ProjectPaths, target: str) -> dict[str, Any]:
    data: dict[str, list[list[Any]]] = {}
    row_counts: dict[str, int] = {}
    with (
        psycopg.connect(**connection_settings(paths, target)) as connection,
        connection.cursor() as cursor,
    ):
        cursor.execute("SHOW server_version")
        server_version = str(cursor.fetchone()[0])
        cursor.execute("SELECT clock_timestamp()")
        database_time = json_value(cursor.fetchone()[0])
        cursor.execute(SCHEMA_QUERY)
        schema = [[json_value(item) for item in row] for row in cursor.fetchall()]
        for table, query in TABLE_QUERIES.items():
            cursor.execute(query)
            rows = [[json_value(item) for item in row] for row in cursor.fetchall()]
            data[table] = rows
            row_counts[table] = len(rows)
        cursor.execute("SELECT max(performed_at) FROM maintenance_events")
        latest_data_at = json_value(cursor.fetchone()[0])
    return {
        "format_version": FINGERPRINT_FORMAT_VERSION,
        "target": target,
        "captured_at": utc_now(),
        "database_time": database_time,
        "latest_data_at": latest_data_at,
        "server_version": server_version,
        "schema_sha256": sha256_value(schema),
        "data_sha256": sha256_value(data),
        "row_counts": row_counts,
    }


def create_manifest(paths: ProjectPaths) -> dict[str, Any]:
    files: dict[str, dict[str, Any]] = {}
    for name in ("database.dump", "source-fingerprint.json"):
        path = paths.backup / name
        if not path.is_file():
            raise FileNotFoundError(f"required backup artifact is missing: {path}")
        files[name] = {"sha256": sha256_file(path), "size_bytes": path.stat().st_size}
    return {
        "format_version": MANIFEST_FORMAT_VERSION,
        "created_at": utc_now(),
        "files": files,
    }


def verify_manifest(directory: Path, manifest_path: Path) -> list[str]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    errors: list[str] = []
    for name, expected in manifest.get("files", {}).items():
        path = directory / name
        if not path.is_file():
            errors.append(f"missing file: {name}")
            continue
        actual_size = path.stat().st_size
        actual_hash = sha256_file(path)
        if actual_size != expected["size_bytes"]:
            errors.append(f"size mismatch: {name}")
        if actual_hash != expected["sha256"]:
            errors.append(f"checksum mismatch: {name}")
    return errors
