from __future__ import annotations

import json

from recoverops.config import ProjectPaths
from recoverops.evidence import utc_now, write_json


def record_event(paths: ProjectPaths, name: str, status: str) -> dict[str, object]:
    state_file = paths.state / "workflow.json"
    if state_file.is_file():
        payload = json.loads(state_file.read_text(encoding="utf-8"))
    else:
        payload = {"format_version": 1, "events": {}}
    event = payload["events"].setdefault(name, {})
    if status == "started":
        event.clear()
    event["status"] = status
    event[f"{status}_at"] = utc_now()
    write_json(state_file, payload)
    return payload
