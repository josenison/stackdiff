"""TAP (Test Anything Protocol) formatter for stackdiff."""
from __future__ import annotations

from stackdiff.diff import ChangeType, DiffResult


def format_diff(result: DiffResult) -> str:
    """Format a DiffResult as a TAP 13 document.

    Each resource diff becomes a TAP test point:
      - UNCHANGED  -> ok
      - ADDED      -> not ok  (new resource not in baseline)
      - REMOVED    -> not ok  (resource missing from target)
      - MODIFIED   -> not ok  (resource has drifted)
    """
    lines: list[str] = ["TAP version 13"]

    diffs = result.diffs
    total = len(diffs)

    if total == 0:
        lines.append("1..0")
        lines.append("# No resources to compare — stacks are identical")
        return "\n".join(lines)

    lines.append(f"1..{total}")

    for idx, rd in enumerate(diffs, start=1):
        resource_id = rd.resource_id
        change = rd.change_type

        if change == ChangeType.UNCHANGED:
            lines.append(f"ok {idx} - {resource_id} unchanged")
        elif change == ChangeType.ADDED:
            lines.append(f"not ok {idx} - {resource_id} added")
            lines.append("  ---")
            lines.append(f"  change: added")
            lines.append("  ...")
        elif change == ChangeType.REMOVED:
            lines.append(f"not ok {idx} - {resource_id} removed")
            lines.append("  ---")
            lines.append(f"  change: removed")
            lines.append("  ...")
        elif change == ChangeType.MODIFIED:
            lines.append(f"not ok {idx} - {resource_id} modified")
            lines.append("  ---")
            lines.append(f"  change: modified")
            if rd.diff_details:
                lines.append(f"  details: {rd.diff_details}")
            lines.append("  ...")
        else:
            lines.append(f"ok {idx} - {resource_id} (unknown change type)")

    passed = sum(1 for rd in diffs if rd.change_type == ChangeType.UNCHANGED)
    failed = total - passed
    lines.append(f"# passed: {passed}")
    lines.append(f"# failed: {failed}")

    return "\n".join(lines)
