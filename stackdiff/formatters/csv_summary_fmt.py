"""CSV summary formatter – one row per change type with counts."""
from __future__ import annotations

import csv
import io
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from stackdiff.diff import DiffResult

from stackdiff.diff import ChangeType

_HEADERS = ["change_type", "count", "resource_ids"]


def format_diff(result: "DiffResult") -> str:
    """Return a CSV string summarising changes grouped by change type."""
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=_HEADERS, lineterminator="\n")
    writer.writeheader()

    if not result.has_changes:
        writer.writerow({"change_type": "none", "count": 0, "resource_ids": ""})
        return buf.getvalue()

    buckets: dict[str, list[str]] = {
        ct.value: [] for ct in ChangeType if ct != ChangeType.UNCHANGED
    }

    for rd in result.diffs:
        if rd.change_type == ChangeType.UNCHANGED:
            continue
        buckets[rd.change_type.value].append(rd.resource_id)

    for change_type, ids in buckets.items():
        if not ids:
            continue
        writer.writerow({
            "change_type": change_type,
            "count": len(ids),
            "resource_ids": "|".join(ids),
        })

    return buf.getvalue()
