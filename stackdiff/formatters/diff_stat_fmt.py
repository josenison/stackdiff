"""diff-stat formatter — git-style diffstat summary output."""
from __future__ import annotations

from stackdiff.diff import ChangeType, DiffResult

_SYMBOL: dict[ChangeType, str] = {
    ChangeType.ADDED: "+",
    ChangeType.REMOVED: "-",
    ChangeType.MODIFIED: "~",
    ChangeType.UNCHANGED: " ",
}

_BAR_WIDTH = 40


def _bar(added: int, removed: int, modified: int, total: int) -> str:
    """Build a proportional +/~/- bar capped at _BAR_WIDTH chars."""
    if total == 0:
        return ""
    scale = _BAR_WIDTH / total
    plus = round(added * scale)
    tilde = round(modified * scale)
    minus = _BAR_WIDTH - plus - tilde
    minus = max(minus, round(removed * scale))
    minus = min(minus, _BAR_WIDTH - plus - tilde)
    return "+" * plus + "~" * tilde + "-" * minus


def format_diff(result: DiffResult) -> str:
    if not result.has_changes:
        return "(no changes)"

    lines: list[str] = []
    counts: dict[ChangeType, int] = {
        ChangeType.ADDED: 0,
        ChangeType.REMOVED: 0,
        ChangeType.MODIFIED: 0,
    }

    interesting = [
        d for d in result.diffs if d.change_type != ChangeType.UNCHANGED
    ]

    max_name = max((len(d.resource_id) for d in interesting), default=0)

    for diff in sorted(interesting, key=lambda d: d.resource_id):
        ct = diff.change_type
        if ct in counts:
            counts[ct] += 1
        sym = _SYMBOL.get(ct, "?")
        name = diff.resource_id.ljust(max_name)
        lines.append(f" {name} | {sym}")

    total = sum(counts.values())
    bar = _bar(counts[ChangeType.ADDED], counts[ChangeType.REMOVED],
               counts[ChangeType.MODIFIED], total)
    summary = (
        f" {total} resource(s) changed: "
        f"{counts[ChangeType.ADDED]} added, "
        f"{counts[ChangeType.MODIFIED]} modified, "
        f"{counts[ChangeType.REMOVED]} removed"
    )
    lines.append(bar)
    lines.append(summary)
    return "\n".join(lines)
