"""New Relic custom event formatter."""
from __future__ import annotations

import json
from datetime import datetime, timezone

from stackdiff.diff import ChangeType, DiffResult

_EVENT_TYPE = "StackDiffEvent"


def _severity(result: DiffResult) -> str:
    if not result.has_changes:
        return "INFO"
    counts = {ct: 0 for ct in ChangeType}
    for rd in result.diffs:
        counts[rd.change_type] += 1
    if counts[ChangeType.REMOVED] > 0:
        return "CRITICAL"
    if counts[ChangeType.MODIFIED] > 0:
        return "WARNING"
    return "INFO"


def format_diff(result: DiffResult, **_kwargs) -> str:
    """Return a New Relic Insights custom event payload as JSON."""
    timestamp = int(datetime.now(timezone.utc).timestamp())
    counts = {ct.value: 0 for ct in ChangeType}
    for rd in result.diffs:
        counts[rd.change_type.value] += 1

    event = {
        "eventType": _EVENT_TYPE,
        "timestamp": timestamp,
        "hasChanges": result.has_changes,
        "severity": _severity(result),
        "totalChanges": len(result.diffs),
        **{f"{k}Count": v for k, v in counts.items()},
    }
    return json.dumps([event], indent=2)
