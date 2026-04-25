"""Tests for the TAP formatter."""
from __future__ import annotations

import pytest

from stackdiff.diff import ChangeType, DiffResult, ResourceDiff
from stackdiff.formatters.tap_fmt import format_diff
from stackdiff.providers.base import Resource


def _res(rid: str, rtype: str = "aws::s3::bucket") -> Resource:
    return Resource(id=rid, type=rtype, properties={})


def _rdiff(
    rid: str,
    change: ChangeType,
    details: str | None = None,
) -> ResourceDiff:
    return ResourceDiff(resource_id=rid, change_type=change, diff_details=details)


def _make_result(*diffs: ResourceDiff) -> DiffResult:
    return DiffResult(diffs=list(diffs))


class TestTAPFormatter:
    def test_no_changes_returns_tap_header(self):
        result = _make_result()
        output = format_diff(result)
        assert output.startswith("TAP version 13")
        assert "1..0" in output
        assert "No resources" in output

    def test_unchanged_resource_is_ok(self):
        result = _make_result(_rdiff("bucket-1", ChangeType.UNCHANGED))
        output = format_diff(result)
        assert "ok 1 - bucket-1 unchanged" in output

    def test_added_resource_is_not_ok(self):
        result = _make_result(_rdiff("bucket-new", ChangeType.ADDED))
        output = format_diff(result)
        assert "not ok 1 - bucket-new added" in output
        assert "change: added" in output

    def test_removed_resource_is_not_ok(self):
        result = _make_result(_rdiff("bucket-old", ChangeType.REMOVED))
        output = format_diff(result)
        assert "not ok 1 - bucket-old removed" in output
        assert "change: removed" in output

    def test_modified_resource_is_not_ok(self):
        result = _make_result(_rdiff("bucket-mod", ChangeType.MODIFIED, "size changed"))
        output = format_diff(result)
        assert "not ok 1 - bucket-mod modified" in output
        assert "change: modified" in output
        assert "details: size changed" in output

    def test_plan_line_reflects_total_count(self):
        result = _make_result(
            _rdiff("r1", ChangeType.UNCHANGED),
            _rdiff("r2", ChangeType.ADDED),
            _rdiff("r3", ChangeType.REMOVED),
        )
        output = format_diff(result)
        assert "1..3" in output

    def test_summary_counts_correct(self):
        result = _make_result(
            _rdiff("r1", ChangeType.UNCHANGED),
            _rdiff("r2", ChangeType.UNCHANGED),
            _rdiff("r3", ChangeType.ADDED),
        )
        output = format_diff(result)
        assert "# passed: 2" in output
        assert "# failed: 1" in output

    def test_modified_without_details_omits_details_line(self):
        result = _make_result(_rdiff("r1", ChangeType.MODIFIED, None))
        output = format_diff(result)
        assert "details:" not in output
        assert "not ok 1 - r1 modified" in output
