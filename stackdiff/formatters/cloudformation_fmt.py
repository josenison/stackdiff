"""CloudFormation change-set style formatter for stack diffs."""
from __future__ import annotations

from stackdiff.diff import ChangeType, DiffResult

_ACTION: dict[ChangeType, str] = {
    ChangeType.ADDED: "Add",
    ChangeType.REMOVED: "Remove",
    ChangeType.MODIFIED: "Modify",
    ChangeType.UNCHANGED: "None",
}

_REPLACEMENT: dict[ChangeType, str] = {
    ChangeType.ADDED: "True",
    ChangeType.REMOVED: "True",
    ChangeType.MODIFIED: "Conditional",
    ChangeType.UNCHANGED: "False",
}


def _scope(change_type: ChangeType) -> list[str]:
    if change_type == ChangeType.UNCHANGED:
        return []
    if change_type == ChangeType.ADDED:
        return ["Properties"]
    if change_type == ChangeType.REMOVED:
        return ["Properties"]
    return ["Properties", "Tags"]


def format_diff(result: DiffResult) -> str:
    """Format *result* as a CloudFormation change-set summary."""
    lines: list[str] = []
    lines.append("CloudFormation Change Set")
    lines.append("=" * 40)

    if not result.has_changes:
        lines.append("Status: No changes detected.")
        return "\n".join(lines)

    changes = [
        rd for rd in result.changes if rd.change_type != ChangeType.UNCHANGED
    ]

    lines.append(f"Changes: {len(changes)}")
    lines.append("")

    for rd in changes:
        action = _ACTION[rd.change_type]
        replacement = _REPLACEMENT[rd.change_type]
        scope = ", ".join(_scope(rd.change_type)) or "None"
        resource_id = rd.resource_id
        res_type = (
            rd.source.resource_type
            if rd.source
            else (rd.target.resource_type if rd.target else "Unknown")
        )
        lines.append(f"  LogicalResourceId : {resource_id}")
        lines.append(f"  ResourceType      : {res_type}")
        lines.append(f"  Action            : {action}")
        lines.append(f"  Replacement       : {replacement}")
        lines.append(f"  Scope             : [{scope}]")
        lines.append("")

    summary = result.summary()
    lines.append(
        f"Summary: +{summary.added} added, "
        f"~{summary.modified} modified, "
        f"-{summary.removed} removed"
    )
    return "\n".join(lines)
