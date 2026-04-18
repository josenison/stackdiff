"""Grafana annotation payload formatter."""
from __future__ import annotations

import json
from datetime import datetime, timezone

from stackdiff.diff import DiffResult


def _tags(result: DiffResult) -> list[str]:
    tags = ["stackdiff"]
    if result.has_changes:
        tags.append("drift")
    else:
        tags.append("clean")
    return tags


def format_diff(result: DiffResult, **_kwargs) -> str:
    """Return a Grafana annotation payload as a JSON string."""
    now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)

    lines: list[str] = []
    for rd in result.diffs:
        lines.append(f"{rd.change_type.value}: {rd.resource_id} ({rd.resource_type})")

    text = "\n".join(lines) if lines else "No infrastructure changes detected."

    payload = {
        "time": now_ms,
        "isRegion": False,
        "tags": _tags(result),
        "text": text,
    }
    return json.dumps(payload, indent=2)
