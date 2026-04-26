"""Short log formatter — one line per changed resource."""
from __future__ import annotations

from stackdiff.diff import ChangeType, DiffResult

_SYMBOLS: dict[ChangeType, str] = {
    ChangeType.ADDED: "+",
    ChangeType.REMOVED: "-",
    ChangeType.MODIFIED: "~",
    ChangeType.UNCHANGED: " ",
}


def format_diff(result: DiffResult) -> str:
    """Return a compact, one-line-per-resource summary of *result*.

    Each line has the form::

        [+] aws::S3Bucket  my-bucket
        [-] aws::Instance  old-server
        [~] gcp::Disk      data-disk

    If there are no changes a single summary line is returned.
    """
    if not result.has_changes:
        total = len(result.diffs)
        return f"No changes. {total} resource(s) unchanged."

    lines: list[str] = []
    for rd in sorted(
        result.diffs,
        key=lambda r: (r.change_type.value, r.resource_type, r.resource_id),
    ):
        if rd.change_type is ChangeType.UNCHANGED:
            continue
        symbol = _SYMBOLS[rd.change_type]
        lines.append(f"[{symbol}] {rd.resource_type:<30}  {rd.resource_id}")

    summary = result.summary()
    lines.append("")
    lines.append(
        f"Summary: +{summary.added} added, "
        f"-{summary.removed} removed, "
        f"~{summary.modified} modified"
    )
    return "\n".join(lines)
