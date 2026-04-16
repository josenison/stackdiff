"""GitHub Actions annotation formatter.

Emits workflow commands so diffs surface as annotations in pull-request
checks when the tool is run inside a GitHub Actions job.

https://docs.github.com/en/actions/using-workflows/workflow-commands-for-github-actions
"""
from stackdiff.diff import ChangeType, DiffResult

_LEVEL = {
    ChangeType.ADDED: "notice",
    ChangeType.REMOVED: "error",
    ChangeType.MODIFIED: "warning",
}


def format_diff(result: DiffResult) -> str:
    if not result.has_changes:
        return "::notice::stackdiff – no changes detected between environments"

    lines: list[str] = []
    for rd in result.diffs:
        level = _LEVEL.get(rd.change_type, "notice")
        res = rd.resource
        title = f"{rd.change_type.value.upper()}: {res.resource_type}/{res.resource_id}"

        details: list[str] = []
        if rd.change_type == ChangeType.MODIFIED and rd.attribute_diffs:
            for attr, (old, new) in rd.attribute_diffs.items():
                details.append(f"{attr}: {old!r} -> {new!r}")
        msg = " | ".join(details) if details else title

        lines.append(f"::{level} title={title}::{msg}")

    summary = result.summary
    lines.append(
        f"::notice title=stackdiff summary::"
        f"added={summary['added']} removed={summary['removed']} modified={summary['modified']}"
    )
    return "\n".join(lines)
