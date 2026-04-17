"""Coloured terminal formatter for diff results."""
from stackdiff.diff import ChangeType, DiffResult

_RESET = "\033[0m"
_BOLD = "\033[1m"

_COLORS = {
    ChangeType.ADDED: "\033[32m",      # green
    ChangeType.REMOVED: "\033[31m",    # red
    ChangeType.MODIFIED: "\033[33m",   # yellow
    ChangeType.UNCHANGED: "\033[37m",  # light grey
}

_SYMBOLS = {
    ChangeType.ADDED: "+",
    ChangeType.REMOVED: "-",
    ChangeType.MODIFIED: "~",
    ChangeType.UNCHANGED: " ",
}


def _colorize(text: str, color: str, *, bold: bool = False) -> str:
    """Wrap *text* with ANSI *color* (and optionally bold) escape codes."""
    prefix = _BOLD + color if bold else color
    return f"{prefix}{text}{_RESET}"


def format_diff(result: DiffResult, *, color: bool = True) -> str:
    """Return a human-readable, optionally coloured string for *result*."""
    if not result.has_changes():
        msg = "No changes detected."
        return _colorize(msg, "", bold=True) if color else msg

    lines: list[str] = []
    header = f"Diff: {result.summary()}"
    lines.append(_colorize(header, "", bold=True) if color else header)
    lines.append("")

    for rd in result.diffs:
        sym = _SYMBOLS[rd.change_type]
        col = _COLORS[rd.change_type] if color else ""
        rst = _RESET if color else ""
        res = rd.resource_after or rd.resource_before
        lines.append(f"{col}{sym} [{res.resource_type}] {res.resource_id}{rst}")

        if rd.change_type == ChangeType.MODIFIED and rd.attribute_diffs:
            for attr, (old, new) in rd.attribute_diffs.items():
                old_col = _COLORS[ChangeType.REMOVED] if color else ""
                new_col = _COLORS[ChangeType.ADDED] if color else ""
                lines.append(f"    {attr}:")
                lines.append(f"  {old_col}  - {old}{rst}")
                lines.append(f"  {new_col}  + {new}{rst}")

    return "\n".join(lines)
