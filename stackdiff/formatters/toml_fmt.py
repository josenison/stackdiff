"""TOML formatter for diff results."""
from __future__ import annotations

try:
    import tomllib  # Python 3.11+
except ImportError:  # pragma: no cover
    tomllib = None  # type: ignore

try:
    import tomli_w
    _HAS_TOMLI_W = True
except ImportError:  # pragma: no cover
    _HAS_TOMLI_W = False

from stackdiff.diff import DiffResult, ChangeType


def _diff_to_dict(result: DiffResult) -> dict:
    changes = []
    for rd in result.changes:
        entry: dict = {
            "resource_id": rd.resource_id,
            "change_type": rd.change_type.value,
        }
        if rd.before is not None:
            entry["before"] = {
                "id": rd.before.id,
                "type": rd.before.type,
                "properties": rd.before.properties,
            }
        if rd.after is not None:
            entry["after"] = {
                "id": rd.after.id,
                "type": rd.after.type,
                "properties": rd.after.properties,
            }
        changes.append(entry)
    return {
        "has_changes": result.has_changes,
        "summary": result.summary,
        "changes": changes,
    }


def format_diff(result: DiffResult) -> str:
    if not _HAS_TOMLI_W:
        raise RuntimeError(
            "tomli_w is required for TOML output: pip install tomli_w"
        )
    data = _diff_to_dict(result)
    return tomli_w.dumps(data)
