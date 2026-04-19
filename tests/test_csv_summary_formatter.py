"""Tests for the CSV summary formatter."""
from __future__ import annotations

import csv
import io

import pytest

from stackdiff.diff import ChangeType, DiffResult, ResourceDiff
from stackdiff.providers.base import Resource
from stackdiff.formatters.csv_summary_fmt import format_diff


def _res(rid: str) -> Resource:
    return Resource(id=rid, type="aws::s3::bucket", properties={})


def _rdiff(rid: str, change: ChangeType) -> ResourceDiff:
    r = _res(rid)
    return ResourceDiff(
        resource_id=rid,
        change_type=change,
        source=r if change != ChangeType.ADDED else None,
        target=r if change != ChangeType.REMOVED else None,
    )


def _parse(text: str) -> list[dict]:
    return list(csv.DictReader(io.StringIO(text)))


def _make_result(*diffs: ResourceDiff) -> DiffResult:
    return DiffResult(diffs=list(diffs))


class TestCSVSummaryFormatter:
    def test_no_changes_single_none_row(self):
        result = _make_result()
        rows = _parse(format_diff(result))
        assert len(rows) == 1
        assert rows[0]["change_type"] == "none"
        assert rows[0]["count"] == "0"

    def test_added_resources_appear(self):
        result = _make_result(
            _rdiff("bucket-a", ChangeType.ADDED),
            _rdiff("bucket-b", ChangeType.ADDED),
        )
        rows = _parse(format_diff(result))
        added = next(r for r in rows if r["change_type"] == "added")
        assert added["count"] == "2"
        assert "bucket-a" in added["resource_ids"]
        assert "bucket-b" in added["resource_ids"]

    def test_removed_resources_appear(self):
        result = _make_result(_rdiff("old-bucket", ChangeType.REMOVED))
        rows = _parse(format_diff(result))
        removed = next(r for r in rows if r["change_type"] == "removed")
        assert removed["count"] == "1"
        assert "old-bucket" in removed["resource_ids"]

    def test_mixed_changes_separate_rows(self):
        result = _make_result(
            _rdiff("r1", ChangeType.ADDED),
            _rdiff("r2", ChangeType.REMOVED),
            _rdiff("r3", ChangeType.MODIFIED),
        )
        rows = _parse(format_diff(result))
        types = {r["change_type"] for r in rows}
        assert "added" in types
        assert "removed" in types
        assert "modified" in types

    def test_unchanged_resources_excluded(self):
        result = _make_result(_rdiff("stable", ChangeType.UNCHANGED))
        rows = _parse(format_diff(result))
        assert all(r["change_type"] != "unchanged" for r in rows)

    def test_output_has_header(self):
        text = format_diff(_make_result())
        assert text.startswith("change_type,count,resource_ids")
