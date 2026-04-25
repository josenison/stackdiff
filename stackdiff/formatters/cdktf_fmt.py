"""CDK for Terraform (cdktf) plan-style formatter for diff results."""
from __future__ import annotations

from stackdiff.diff import ChangeType, DiffResult

_SYMBOL: dict[ChangeType, str] = {
    ChangeType.ADDED: "+",
    ChangeType.REMOVED: "-",
    ChangeType.MODIFIED: "~",
    ChangeType.UNCHANGED: " ",
}

_COLOR: dict[ChangeType, str] = {
    ChangeType.ADDED: "\033[32m",
    ChangeType.REMOVED: "\033[31m",
    ChangeType.MODIFIED: "\033[33m",
    ChangeType.UNCHANGED: "",
}

_RESET = "\033[0m"


def _render_block(rd, use_color: bool) -> str:
    sym = _SYMBOL[rd.change_type]
    color = _COLOR[rd.change_type] if use_color else ""
    reset = _RESET if use_color else ""
    res = rd.resource
    lines = [
        f"{color}{sym} {res.resource_type}.{res.resource_id}{reset}",
    ]
    if rd.change_type == ChangeType.MODIFIED and rd.diff_details:
        for key, val in rd.diff_details.items():
            before = val.get("before", "<none>")
            after = val.get("after", "<none>")
            lines.append(f"    {color}~ {key}: {before!r} -> {after!r}{reset}")
    return "\n".join(lines)


def format_diff(result: DiffResult, *, use_color: bool = False) -> str:
    """Return a cdktf-style plan string for *result*."""
    if not result.has_changes:
        return "No changes. Infrastructure is up-to-date."

    lines: list[str] = [
        "Terraform used the selected providers to generate the following",
        "execution plan. Resource actions are indicated with the following symbols:",
        "  + create",
        "  - destroy",
        "  ~ update in-place",
        "",
        "cdktf will perform the following actions:",
        "",
    ]
    for rd in result.changes:
        if rd.change_type == ChangeType.UNCHANGED:
            continue
        lines.append(_render_block(rd, use_color=use_color))
        lines.append("")

    summary = result.summary
    lines.append(
        f"Plan: {summary.added} to add, "
        f"{summary.modified} to change, "
        f"{summary.removed} to destroy."
    )
    return "\n".join(lines)
