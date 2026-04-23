"""Timeline formatter – renders a chronological ASCII timeline of changes."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import List

from stackdiff.diff import ChangeType, DiffResult, ResourceDiff

_SYMBOL: dict[ChangeType, str] = {
    ChangeType.ADDED: "+",
    ChangeType.REMOVED: "-",
    ChangeType.MODIFIED: "~",
    ChangeType.UNCHANGED: " ",
}

_LABEL: dict[ChangeType, str] = {
    ChangeType.ADDED: "ADDED",
    ChangeType.REMOVED: "REMOVED",
    ChangeType.MODIFIED: "MODIFIED",
    ChangeType.UNCHANGED: "UNCHANGED",
}


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _render_entry(rd: ResourceDiff, index: int) -> str:
    sym = _SYMBOL[rd.change_type]
    label = _LABEL[rd.change_type]
    rid = rd.resource_id
    rtype = rd.resource_type
    return f"  [{index:>3}] {sym} {label:<10}  {rtype:<30}  {rid}"


def format_diff(result: DiffResult) -> str:
    lines: List[str] = []
    ts = _timestamp()
    lines.append(f"# stackdiff timeline  {ts}")
    lines.append(f"# left={result.left_name}  right={result.right_name}")
    lines.append("#" + "-" * 70)

    changes = [rd for rd in result.diffs if rd.change_type != ChangeType.UNCHANGED]

    if not changes:
        lines.append("  (no changes detected)")
    else:
        for i, rd in enumerate(changes, start=1):
            lines.append(_render_entry(rd, i))

    lines.append("#" + "-" * 70)
    summary = result.summary()
    lines.append(
        f"# summary: +{summary['added']} added  "
        f"-{summary['removed']} removed  "
        f"~{summary['modified']} modified"
    )
    return "\n".join(lines) + "\n"
