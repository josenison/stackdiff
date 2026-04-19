"""Webhook formatter – emits a JSON payload suitable for generic HTTP webhooks."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from stackdiff.diff import DiffResult


def _change_counts(result: DiffResult) -> dict[str, int]:
    counts: dict[str, int] = {"added": 0, "removed": 0, "modified": 0, "unchanged": 0}
    for rd in result.diffs:
        counts[rd.change_type.value] += 1
    return counts


def _build_changes(result: DiffResult) -> list[dict[str, Any]]:
    changes = []
    for rd in result.diffs:
        entry: dict[str, Any] = {
            "resource_id": rd.resource_id,
            "resource_type": rd.resource_type,
            "change_type": rd.change_type.value,
        }
        if rd.diff_detail:
            entry["detail"] = rd.diff_detail
        changes.append(entry)
    return changes


def format_diff(result: DiffResult) -> str:
    """Return a JSON string suitable for posting to a generic webhook endpoint."""
    counts = _change_counts(result)
    payload: dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "has_changes": result.has_changes,
        "summary": {
            "added": counts["added"],
            "removed": counts["removed"],
            "modified": counts["modified"],
            "unchanged": counts["unchanged"],
            "total": len(result.diffs),
        },
        "changes": _build_changes(result),
    }
    return json.dumps(payload, indent=2)
