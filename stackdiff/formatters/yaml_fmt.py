"""YAML formatter for diff results."""
from __future__ import annotations

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore

from stackdiff.diff import DiffResult, ChangeType


def _diff_to_dict(result: DiffResult) -> dict:
    """Convert a DiffResult into a plain dict suitable for YAML serialisation."""
    changes = []
    for rd in result.diffs:
        entry: dict = {
            "resource_id": rd.resource_id,
            "resource_type": rd.resource_type,
            "change": rd.change_type.value,
        }
        if rd.change_type == ChangeType.MODIFIED:
            attribute_changes = []
            for attr, (old_val, new_val) in (rd.attribute_changes or {}).items():
                attribute_changes.append({
                    "attribute": attr,
                    "old": old_val,
                    "new": new_val,
                })
            entry["attribute_changes"] = attribute_changes
        changes.append(entry)

    return {
        "summary": {
            "added": result.summary.get(ChangeType.ADDED, 0),
            "removed": result.summary.get(ChangeType.REMOVED, 0),
            "modified": result.summary.get(ChangeType.MODIFIED, 0),
            "unchanged": result.summary.get(ChangeType.UNCHANGED, 0),
        },
        "changes": changes,
    }


def format_diff(result: DiffResult) -> str:
    """Return a YAML string representing *result*."""
    if yaml is None:  # pragma: no cover
        raise RuntimeError(
            "PyYAML is required for YAML output. Install it with: pip install pyyaml"
        )
    data = _diff_to_dict(result)
    return yaml.dump(data, default_flow_style=False, sort_keys=False)
