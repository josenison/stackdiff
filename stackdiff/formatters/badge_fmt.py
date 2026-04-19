"""Badge formatter – emits a Shields.io endpoint JSON badge payload."""
from __future__ import annotations

import json

from stackdiff.diff import DiffResult


def _color(result: DiffResult) -> str:
    if not result.has_changes:
        return "brightgreen"
    counts = result.summary()
    if counts.get("removed", 0) > 0:
        return "red"
    if counts.get("modified", 0) > 0:
        return "orange"
    return "yellow"


def _label_message(result: DiffResult) -> str:
    if not result.has_changes:
        return "in sync"
    counts = result.summary()
    parts = []
    for key in ("added", "removed", "modified"):
        n = counts.get(key, 0)
        if n:
            parts.append(f"{n} {key}")
    return ", ".join(parts)


def format_diff(result: DiffResult, **kwargs) -> str:
    """Return a Shields.io endpoint-compatible JSON string."""
    payload = {
        "schemaVersion": 1,
        "label": kwargs.get("label", "stackdiff"),
        "message": _label_message(result),
        "color": _color(result),
        "isError": result.has_changes,
    }
    return json.dumps(payload, indent=2)
