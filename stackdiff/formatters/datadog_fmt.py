"""Datadog Events API formatter."""
from __future__ import annotations

import json
from typing import Any

from stackdiff.diff import DiffResult, ChangeType


def _alert_type(result: DiffResult) -> str:
    if not result.has_changes:
        return "success"
    counts = result.summary
    if counts.get(ChangeType.REMOVED, 0) > 0:
        return "error"
    if counts.get(ChangeType.MODIFIED, 0) > 0:
        return "warning"
    return "info"


def _build_text(result: DiffResult) -> str:
    if not result.has_changes:
        return "No infrastructure changes detected."
    lines: list[str] = []
    for rd in result.diffs:
        lines.append(f"%%% \n**{rd.change_type.value}** `{rd.resource_id}` ({rd.resource_type})\n %%%")
    return "\n".join(lines)


def format_diff(result: DiffResult, **kwargs: Any) -> str:
    """Return a Datadog Events API-compatible JSON payload."""
    summary = result.summary
    added = summary.get(ChangeType.ADDED, 0)
    removed = summary.get(ChangeType.REMOVED, 0)
    modified = summary.get(ChangeType.MODIFIED, 0)

    title = (
        "Infrastructure diff: no changes"
        if not result.has_changes
        else f"Infrastructure diff: +{added} ~{modified} -{removed}"
    )

    payload: dict[str, Any] = {
        "title": title,
        "text": _build_text(result),
        "alert_type": _alert_type(result),
        "tags": [
            f"added:{added}",
            f"modified:{modified}",
            f"removed:{removed}",
        ],
        "source_type_name": "stackdiff",
    }
    return json.dumps(payload, indent=2)
