"""Scorecard formatter – emits a numeric health score alongside a summary.

Score formula:
  100  (no changes)
  max(0, 100 - added*5 - removed*10 - modified*3)
"""
from __future__ import annotations

import json
from typing import Union

from stackdiff.diff import ChangeType, DiffResult


def _score(result: DiffResult) -> int:
    added = sum(
        1 for d in result.diffs if d.change_type == ChangeType.ADDED
    )
    removed = sum(
        1 for d in result.diffs if d.change_type == ChangeType.REMOVED
    )
    modified = sum(
        1 for d in result.diffs if d.change_type == ChangeType.MODIFIED
    )
    return max(0, 100 - added * 5 - removed * 10 - modified * 3)


def _grade(score: int) -> str:
    if score == 100:
        return "A+"
    if score >= 90:
        return "A"
    if score >= 75:
        return "B"
    if score >= 60:
        return "C"
    if score >= 40:
        return "D"
    return "F"


def format_diff(result: DiffResult) -> Union[str, bytes]:
    """Return a JSON scorecard for *result*."""
    score = _score(result)
    grade = _grade(score)

    change_counts: dict[str, int] = {
        "added": 0,
        "removed": 0,
        "modified": 0,
    }
    for d in result.diffs:
        key = d.change_type.value.lower()
        if key in change_counts:
            change_counts[key] += 1

    payload = {
        "score": score,
        "grade": grade,
        "has_changes": result.has_changes,
        "summary": result.summary,
        "changes": change_counts,
    }
    return json.dumps(payload, indent=2)
