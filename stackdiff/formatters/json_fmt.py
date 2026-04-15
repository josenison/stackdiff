"""JSON formatter for diff results — useful for machine consumption."""

import json
from typing import TextIO, Any, Dict
import sys

from stackdiff.diff import DiffResult, ChangeType


def _diff_to_dict(diff) -> Dict[str, Any]:
    record: Dict[str, Any] = {
        "resource_id": diff.resource_id,
        "resource_type": diff.resource_type,
        "change_type": diff.change_type.value,
    }
    if diff.change_type == ChangeType.MODIFIED and diff.attribute_diffs:
        record["attributes"] = {
            attr: {"old": old, "new": new}
            for attr, (old, new) in diff.attribute_diffs.items()
        }
    return record


def format_diff(result: DiffResult, out: TextIO = sys.stdout, indent: int = 2) -> None:
    """Serialize *result* as JSON and write to *out*."""
    summary = result.summary()
    payload: Dict[str, Any] = {
        "has_changes": result.has_changes(),
        "summary": summary,
        "changes": [
            _diff_to_dict(d)
            for d in result.diffs
            if d.change_type != ChangeType.UNCHANGED
        ],
    }
    json.dump(payload, out, indent=indent)
    out.write("\n")
