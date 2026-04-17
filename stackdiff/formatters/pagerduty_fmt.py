"""PagerDuty Events API v2 payload formatter."""
from __future__ import annotations

import json
from typing import Any

from stackdiff.diff import ChangeType, DiffResult


def _severity(result: DiffResult) -> str:
    counts = {ct: 0 for ct in ChangeType}
    for rd in result.diffs:
        counts[rd.change_type] += 1

    if counts[ChangeType.REMOVED] > 0:
        return "critical"
    if counts[ChangeType.MODIFIED] > 0:
        return "error"
    if counts[ChangeType.ADDED] > 0:
        return "warning"
    return "info"


def format_diff(result: DiffResult, **kwargs: Any) -> str:
    """Return a PagerDuty Events API v2 compatible JSON payload string."""
    severity = _severity(result)

    summary_parts: list[str] = []
    counts: dict[ChangeType, int] = {ct: 0 for ct in ChangeType}
    for rd in result.diffs:
        counts[rd.change_type] += 1

    if not result.has_changes:
        summary_parts.append("No infrastructure changes detected")
    else:
        if counts[ChangeType.ADDED]:
            summary_parts.append(f"{counts[ChangeType.ADDED]} added")
        if counts[ChangeType.REMOVED]:
            summary_parts.append(f"{counts[ChangeType.REMOVED]} removed")
        if counts[ChangeType.MODIFIED]:
            summary_parts.append(f"{counts[ChangeType.MODIFIED]} modified")

    custom_details: dict[str, Any] = {
        "changes": [
            {
                "resource_id": rd.resource_id,
                "resource_type": rd.resource_type,
                "change": rd.change_type.value,
            }
            for rd in result.diffs
        ]
    }

    payload = {
        "payload": {
            "summary": "stackdiff: " + ", ".join(summary_parts),
            "severity": severity,
            "source": "stackdiff",
            "custom_details": custom_details,
        },
        "routing_key": kwargs.get("routing_key", ""),
        "event_action": "trigger" if result.has_changes else "resolve",
    }

    return json.dumps(payload, indent=2)
