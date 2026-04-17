"""OpsGenie alert payload formatter for diff results."""
from __future__ import annotations
import json
from stackdiff.diff import DiffResult, ChangeType

_PRIORITY_MAP = {
    0: "P5",
    1: "P4",
    2: "P3",
    3: "P2",
}


def _priority(result: DiffResult) -> str:
    count = len(result.diffs)
    has_removed = any(d.change_type == ChangeType.REMOVED for d in result.diffs)
    if has_removed and count >= 3:
        return "P1"
    idx = min(count, 3)
    return _PRIORITY_MAP[idx]


def format_diff(result: DiffResult) -> str:
    if not result.has_changes:
        return json.dumps({"message": "No infrastructure changes detected.", "priority": "P5"}, indent=2)

    details = {
        d.resource_id: f"{d.change_type.value} ({d.resource_type})"
        for d in result.diffs
    }

    payload = {
        "message": f"Infrastructure diff: {result.summary()}",
        "priority": _priority(result),
        "details": details,
        "tags": list({d.resource_type for d in result.diffs}),
    }
    return json.dumps(payload, indent=2)
