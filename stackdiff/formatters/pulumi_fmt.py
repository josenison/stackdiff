"""Pulumi-style output formatter for stack diffs."""
from __future__ import annotations

from stackdiff.diff import ChangeType, DiffResult

_SYMBOLS: dict[ChangeType, str] = {
    ChangeType.ADDED: "+",
    ChangeType.REMOVED: "-",
    ChangeType.MODIFIED: "~",
    ChangeType.UNCHANGED: " ",
}

_COLORS: dict[ChangeType, str] = {
    ChangeType.ADDED: "\033[32m",
    ChangeType.REMOVED: "\033[31m",
    ChangeType.MODIFIED: "\033[33m",
    ChangeType.UNCHANGED: "",
}
_RESET = "\033[0m"


def _render_resource(rdiff, *, color: bool) -> str:
    sym = _SYMBOLS[rdiff.change_type]
    line = f"  {sym}  {rdiff.resource_type}: {rdiff.resource_id}"
    if rdiff.change_type == ChangeType.MODIFIED and rdiff.diff_details:
        detail_lines = []
        for key, (old_val, new_val) in rdiff.diff_details.items():
            detail_lines.append(f"       ~ {key}: {old_val!r} => {new_val!r}")
        line = "\n".join([line] + detail_lines)
    if color and rdiff.change_type in _COLORS and _COLORS[rdiff.change_type]:
        line = _COLORS[rdiff.change_type] + line + _RESET
    return line


def format_diff(result: DiffResult, *, color: bool = False) -> str:
    """Format *result* in a Pulumi-inspired preview style."""
    if not result.has_changes:
        return "Resources:\n    (no changes)"

    lines = ["Previewing update:\n"]
    for rdiff in result.changes:
        lines.append(_render_resource(rdiff, color=color))

    lines.append("")
    summary = result.summary
    parts = []
    if summary.added:
        part = f"{summary.added} to add"
        lines_part = ("\033[32m" + part + _RESET) if color else part
        parts.append(lines_part)
    if summary.removed:
        part = f"{summary.removed} to remove"
        lines_part = ("\033[31m" + part + _RESET) if color else part
        parts.append(lines_part)
    if summary.modified:
        part = f"{summary.modified} to change"
        lines_part = ("\033[33m" + part + _RESET) if color else part
        parts.append(lines_part)

    lines.append("Resources: " + ", ".join(parts))
    return "\n".join(lines)
