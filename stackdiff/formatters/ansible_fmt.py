"""Ansible-compatible formatter: emits a JSON structure matching
Ansible's custom facts / debug output convention so the diff result
can be consumed directly by an Ansible playbook or role."""
from __future__ import annotations

import json
from typing import Any

from stackdiff.diff import DiffResult, ChangeType


def _change_to_dict(rd) -> dict[str, Any]:
    return {
        "resource_id": rd.resource_id,
        "resource_type": rd.resource_type,
        "change_type": rd.change_type.value,
        "left": (
            {"id": rd.left.id, "type": rd.left.type, "attributes": rd.left.attributes}
            if rd.left
            else None
        ),
        "right": (
            {"id": rd.right.id, "type": rd.right.type, "attributes": rd.right.attributes}
            if rd.right
            else None
        ),
    }


def format_diff(result: DiffResult) -> str:
    """Return a JSON string shaped for Ansible's ``set_fact`` / ``debug`` tasks.

    The top-level keys mirror Ansible's convention for structured return values:
    ``changed``, ``failed``, ``msg``, and a ``stackdiff`` namespace with the
    full detail.
    """
    counts = {
        ChangeType.ADDED.value: 0,
        ChangeType.REMOVED.value: 0,
        ChangeType.MODIFIED.value: 0,
        ChangeType.UNCHANGED.value: 0,
    }
    changes = []
    for rd in result.diffs:
        counts[rd.change_type.value] += 1
        if rd.change_type != ChangeType.UNCHANGED:
            changes.append(_change_to_dict(rd))

    has_changes = result.has_changes()
    payload: dict[str, Any] = {
        "changed": has_changes,
        "failed": False,
        "msg": result.summary() if has_changes else "No infrastructure changes detected.",
        "stackdiff": {
            "has_changes": has_changes,
            "counts": counts,
            "changes": changes,
        },
    }
    return json.dumps(payload, indent=2)
