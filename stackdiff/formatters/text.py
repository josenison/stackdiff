"""Plain-text formatter for diff results."""

from typing import TextIO
import sys

from stackdiff.diff import DiffResult, ChangeType

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


def format_diff(result: DiffResult, out: TextIO = sys.stdout, color: bool = True) -> None:
    """Write a human-readable diff to *out*."""
    if not result.has_changes():
        out.write("No changes detected.\n")
        return

    summary = result.summary()
    out.write(
        f"Summary: +{summary['added']} added, "
        f"-{summary['removed']} removed, "
        f"~{summary['modified']} modified\n"
    )
    out.write("\n")

    for diff in result.diffs:
        symbol = _SYMBOLS[diff.change_type]
        prefix = _COLORS[diff.change_type] if color else ""
        suffix = _RESET if color and prefix else ""
        out.write(f"{prefix}{symbol} [{diff.resource_type}] {diff.resource_id}{suffix}\n")

        if diff.change_type == ChangeType.MODIFIED and diff.attribute_diffs:
            for attr, (old_val, new_val) in diff.attribute_diffs.items():
                if color:
                    out.write(f"  \033[31m  - {attr}: {old_val}\033[0m\n")
                    out.write(f"  \033[32m  + {attr}: {new_val}\033[0m\n")
                else:
                    out.write(f"    - {attr}: {old_val}\n")
                    out.write(f"    + {attr}: {new_val}\n")
