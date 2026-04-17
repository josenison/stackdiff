"""Prometheus text exposition format formatter."""
from __future__ import annotations

from stackdiff.diff import ChangeType, DiffResult

_METRIC_PREFIX = "stackdiff"


def format_diff(result: DiffResult, stack_a: str = "a", stack_b: str = "b") -> str:
    """Return Prometheus text exposition format metrics for a diff result."""
    lines: list[str] = []

    counts: dict[str, int] = {
        ChangeType.ADDED.value: 0,
        ChangeType.REMOVED.value: 0,
        ChangeType.MODIFIED.value: 0,
        ChangeType.UNCHANGED.value: 0,
    }

    for rd in result.diffs:
        counts[rd.change_type.value] += 1

    labels = f'stack_a="{stack_a}",stack_b="{stack_b}"'

    lines.append(f"# HELP {_METRIC_PREFIX}_resources_total Count of resources by change type")
    lines.append(f"# TYPE {_METRIC_PREFIX}_resources_total gauge")
    for change_type, count in counts.items():
        lines.append(
            f"{_METRIC_PREFIX}_resources_total{{{labels},change_type=\"{change_type}\"}} {count}"
        )

    has_changes = 1 if result.has_changes else 0
    lines.append(f"# HELP {_METRIC_PREFIX}_has_changes 1 if any changes exist between stacks")
    lines.append(f"# TYPE {_METRIC_PREFIX}_has_changes gauge")
    lines.append(f"{_METRIC_PREFIX}_has_changes{{{labels}}} {has_changes}")

    total = len(result.diffs)
    lines.append(f"# HELP {_METRIC_PREFIX}_diff_total Total number of resources compared")
    lines.append(f"# TYPE {_METRIC_PREFIX}_diff_total gauge")
    lines.append(f"{_METRIC_PREFIX}_diff_total{{{labels}}} {total}")

    return "\n".join(lines) + "\n"
