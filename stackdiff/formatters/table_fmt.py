"""Table formatter for diff results using fixed-width columns."""

from stackdiff.diff import DiffResult, ChangeType

_HEADERS = ("Change", "Resource ID", "Type", "Stack")
_COL_MIN = (8, 20, 20, 16)


def _col_widths(result: DiffResult) -> tuple[int, int, int, int]:
    w_change = max(_COL_MIN[0], len(_HEADERS[0]))
    w_id = max(_COL_MIN[1], len(_HEADERS[1]))
    w_type = max(_COL_MIN[2], len(_HEADERS[2]))
    w_stack = max(_COL_MIN[3], len(_HEADERS[3]))

    for rd in result.diffs:
        res = rd.resource_a or rd.resource_b
        if res:
            w_id = max(w_id, len(res.resource_id))
            w_type = max(w_type, len(res.resource_type))
            w_stack = max(w_stack, len(res.stack_name))
        w_change = max(w_change, len(rd.change_type.value))

    return w_change, w_id, w_type, w_stack


def _separator(widths: tuple[int, int, int, int]) -> str:
    return "+" + "+".join("-" * (w + 2) for w in widths) + "+"


def _row(values: tuple[str, str, str, str], widths: tuple[int, int, int, int]) -> str:
    cells = " | ".join(v.ljust(w) for v, w in zip(values, widths))
    return f"| {cells} |"


def _summary_line(summary: dict) -> str:
    """Format the summary counts line shown below the table."""
    parts = []
    if summary.get("added"):
        parts.append(f"{summary['added']} added")
    if summary.get("removed"):
        parts.append(f"{summary['removed']} removed")
    if summary.get("modified"):
        parts.append(f"{summary['modified']} modified")
    return "  " + ", ".join(parts) if parts else "  No changes"


def format_diff(result: DiffResult) -> str:
    if not result.has_changes():
        return "No changes detected."

    widths = _col_widths(result)
    sep = _separator(widths)
    lines = [sep, _row(_HEADERS, widths), sep]

    for rd in result.diffs:
        res = rd.resource_a or rd.resource_b
        if res is None:
            continue
        row = (
            rd.change_type.value,
            res.resource_id,
            res.resource_type,
            res.stack_name,
        )
        lines.append(_row(row, widths))

    lines.append(sep)
    lines.append(_summary_line(result.summary()))
    return "\n".join(lines)
