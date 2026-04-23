"""Tests for the timeline formatter."""
from __future__ import annotations

import pytest

from stackdiff.diff import ChangeType, DiffResult, ResourceDiff
from stackdiff.formatters.timeline_fmt import format_diff
from stackdiff.providers.base import Resource


def _res(rid: str, rtype: str = "aws::s3::bucket") -> Resource:
    return Resource(resource_id=rid, resource_type=rtype, properties={})


def _rdiff(
    rid: str,
    change: ChangeType,
    rtype: str = "aws::s3::bucket",
) -> ResourceDiff:
    r = _res(rid, rtype)
    return ResourceDiff(
        resource_id=rid,
        resource_type=rtype,
        change_type=change,
        left=None if change == ChangeType.ADDED else r,
        right=None if change == ChangeType.REMOVED else r,
    )


def _make_result(diffs: list[ResourceDiff]) -> DiffResult:
    return DiffResult(left_name="staging", right_name="production", diffs=diffs)


class TestTimelineFormatter:
    def test_no_changes_returns_no_changes_message(self):
        result = _make_result([])
        output = format_diff(result)
        assert "no changes detected" in output

    def test_header_contains_env_names(self):
        result = _make_result([])
        output = format_diff(result)
        assert "staging" in output
        assert "production" in output

    def test_added_resource_shown_with_plus(self):
        result = _make_result([_rdiff("bucket-new", ChangeType.ADDED)])
        output = format_diff(result)
        assert "+" in output
        assert "ADDED" in output
        assert "bucket-new" in output

    def test_removed_resource_shown_with_minus(self):
        result = _make_result([_rdiff("old-bucket", ChangeType.REMOVED)])
        output = format_diff(result)
        assert "-" in output
        assert "REMOVED" in output
        assert "old-bucket" in output

    def test_modified_resource_shown_with_tilde(self):
        result = _make_result([_rdiff("mod-bucket", ChangeType.MODIFIED)])
        output = format_diff(result)
        assert "~" in output
        assert "MODIFIED" in output

    def test_unchanged_resources_excluded_from_timeline(self):
        result = _make_result([
            _rdiff("unchanged", ChangeType.UNCHANGED),
            _rdiff("added", ChangeType.ADDED),
        ])
        output = format_diff(result)
        assert "unchanged" not in output
        assert "added" in output

    def test_summary_line_present(self):
        result = _make_result([
            _rdiff("a", ChangeType.ADDED),
            _rdiff("b", ChangeType.REMOVED),
        ])
        output = format_diff(result)
        assert "summary" in output
        assert "+1" in output
        assert "-1" in output

    def test_entries_are_numbered(self):
        result = _make_result([
            _rdiff("r1", ChangeType.ADDED),
            _rdiff("r2", ChangeType.REMOVED),
        ])
        output = format_diff(result)
        assert "[  1]" in output
        assert "[  2]" in output

    def test_timestamp_header_present(self):
        result = _make_result([])
        output = format_diff(result)
        assert "stackdiff timeline" in output
