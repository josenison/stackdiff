"""Newline-delimited JSON (NDJSON) formatter.

Each resource diff is emitted as a separate JSON object on its own line,
making the output suitable for streaming pipelines and log aggregators.
"""
from __future__ import annotations

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from stackdiff.diff import DiffResult


def _diff_entry(rd) -> dict:
    """Convert a single ResourceDiff to a plain dict."""
    entry: dict = {
        "change_type": rd.change_type.value,
        "resource_id": rd.resource_id,
    }
    if rd.resource_type is not None:
        entry["resource_type"] = rd.resource_type
    if rd.before is not None:
        entry["before"] = rd.before
    if rd.after is not None:
        entry["after"] = rd.after
    if rd.attribute_changes:
        entry["attribute_changes"] = rd.attribute_changes
    return entry


def format_diff(result: "DiffResult") -> str:
    """Return NDJSON string — one JSON object per changed resource.

    When there are no changes a single summary line is emitted so that
    downstream consumers always receive at least one record.
    """
    if not result.has_changes:
        summary = {
            "has_changes": False,
            "added": 0,
            "removed": 0,
            "modified": 0,
        }
        return json.dumps(summary)

    lines = []
    for rd in result.diffs:
        lines.append(json.dumps(_diff_entry(rd)))
    return "\n".join(lines)
