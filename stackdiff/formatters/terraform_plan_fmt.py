"""Formatter that renders a diff in Terraform plan-style output."""
from __future__ import annotations

from stackdiff.diff import ChangeType, DiffResult

_SYMBOLS = {
    ChangeType.ADDED: "+",
    ChangeType.REMOVED: "-",
    ChangeType.MODIFIED: "~",
    ChangeType.UNCHANGED: " ",
}

_COLORS = {
    ChangeType.ADDED: "\033[32m",
    ChangeType.REMOVED: "\033[31m",
    ChangeType.MODIFIED: "\033[33m",
    ChangeType.UNCHANGED: "",
}
_RESET = "\033[0m"


def _symbol(change_type: ChangeType) -> str:
    return _SYMBOLS.get(change_type, " ")


def _render_resource(rdiff, *, colorize: bool) -> str:
    sym = _symbol(rdiff.change_type)
    color = _COLORS.get(rdiff.change_type, "") if colorize else ""
    reset = _RESET if colorize else ""
    r = rdiff.resource_b or rdiff.resource_a
    header = f"{color}  {sym} resource \"{r.resource_type}\" \"{r.resource_id}\"{reset}"
    lines = [header]
    if rdiff.change_type == ChangeType.MODIFIED and rdiff.resource_a and rdiff.resource_b:
        old_attrs = rdiff.resource_a.attributes
        new_attrs = rdiff.resource_b.attributes
        all_keys = sorted(set(old_attrs) | set(new_attrs))
        for key in all_keys:
            old_val = old_attrs.get(key, "<unset>")
            new_val = new_attrs.get(key, "<unset>")
            if old_val != new_val:
                lines.append(f"{color}      {key}: \"{old_val}\" -> \"{new_val}\"{reset}")
    return "\n".join(lines)


def format_diff(result: DiffResult, *, colorize: bool = False) -> str:
    lines: list[str] = []
    lines.append("Terraform plan-style diff")
    lines.append("=" * 40)
    if not result.has_changes:
        lines.append("No changes. Infrastructure is up-to-date.")
        return "\n".join(lines)
    changes = [d for d in result.diffs if d.change_type != ChangeType.UNCHANGED]
    for rdiff in changes:
        lines.append(_render_resource(rdiff, colorize=colorize))
    lines.append("")
    s = result.summary
    lines.append(
        f"Plan: {s.get('added', 0)} to add, "
        f"{s.get('modified', 0)} to change, "
        f"{s.get('removed', 0)} to destroy."
    )
    return "\n".join(lines)
