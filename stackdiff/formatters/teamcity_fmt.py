"""TeamCity service messages formatter."""
from __future__ import annotations

from stackdiff.diff import ChangeType, DiffResult


def _escape(value: str) -> str:
    """Escape special characters for TeamCity service messages."""
    return (
        value
        .replace("|", "||")
        .replace("'", "|'")
        .replace("\n", "|n")
        .replace("\r", "|r")
        .replace("[", "|[")
        .replace("]", "|]")
    )


def format_diff(result: DiffResult) -> str:
    lines: list[str] = []

    lines.append("##teamcity[testSuiteStarted name='stackdiff']")

    if not result.has_changes:
        lines.append("##teamcity[testStarted name='infrastructure-drift']")
        lines.append("##teamcity[testFinished name='infrastructure-drift']")
        lines.append("##teamcity[testSuiteFinished name='stackdiff']")
        return "\n".join(lines)

    _change_label = {
        ChangeType.ADDED: "ADDED",
        ChangeType.REMOVED: "REMOVED",
        ChangeType.MODIFIED: "MODIFIED",
    }

    for diff in result.diffs:
        label = _change_label.get(diff.change_type, "UNKNOWN")
        name = _escape(f"{diff.resource_id} [{label}]")
        lines.append(f"##teamcity[testStarted name='{name}']")
        detail = _escape(
            f"type={diff.resource_type} change={label}"
        )
        if diff.change_type != ChangeType.ADDED and diff.change_type != ChangeType.REMOVED:
            lines.append(
                f"##teamcity[testFailed name='{name}' message='Resource drift detected' details='{detail}']"
            )
        lines.append(f"##teamcity[testFinished name='{name}']")

    summary = _escape(result.summary)
    lines.append(f"##teamcity[buildStatus text='{summary}']")
    lines.append("##teamcity[testSuiteFinished name='stackdiff']")
    return "\n".join(lines)
