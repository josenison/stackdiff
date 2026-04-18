"""Splunk HEC (HTTP Event Collector) formatter — emits newline-delimited JSON events."""
from __future__ import annotations

import json
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from stackdiff.diff import DiffResult


def format_diff(result: "DiffResult", source: str = "stackdiff") -> str:
    """Return newline-delimited Splunk HEC JSON events for each resource diff."""
    events = []
    timestamp = time.time()

    if not result.has_changes:
        event = {
            "time": timestamp,
            "source": source,
            "sourcetype": "stackdiff",
            "event": {
                "has_changes": False,
                "summary": result.summary,
            },
        }
        return json.dumps(event)

    for rd in result.diffs:
        payload = {
            "time": timestamp,
            "source": source,
            "sourcetype": "stackdiff",
            "event": {
                "has_changes": True,
                "change_type": rd.change_type.value,
                "resource_id": rd.resource_id,
                "resource_type": rd.resource_type,
                "before": rd.before,
                "after": rd.after,
            },
        }
        events.append(json.dumps(payload))

    return "\n".join(events)
