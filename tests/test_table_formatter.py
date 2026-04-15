"""Tests for the fixed-width table formatter."""

import pytest

from stackdiff.diff import ChangeType, DiffResult, ResourceDiff
from stackdiff.providers.base import Resource
from stackdiff.formatters.table_fmt import format_diff


def _res(rid: str, rtype: str = "aws::s3::bucket", stack: str = "prod") -> Resource:
    return Resource(resource_id=rid, resource_type=rtype, stack_name=stack, attributes={})


def _rdiff(
    change: ChangeType,
    a: Resource | None = None,
    b: Resource | None = None,
) -> ResourceDiff:
    return ResourceDiff(change_type=change, resource_a=a, resource_b=b)


def _make_result(*diffs: ResourceDiff) -> DiffResult:
    return DiffResult(diffs=list(diffs))


class TestTableFormatter:
    def test_no_changes_returns_simple_message(self):
        result = _make_result()
        assert format_diff(result) == "No changes detected."

    def test_added_resource_appears_in_table(self):
        res = _res("bucket-new")
        result = _make_result(_rdiff(ChangeType.ADDED, b=res))
        out = format_diff(result)
        assert "bucket-new" in out
        assert ChangeType.ADDED.value in out

    def test_removed_resource_appears_in_table(self):
        res = _res("bucket-old")
        result = _make_result(_rdiff(ChangeType.REMOVED, a=res))
        out = format_diff(result)
        assert "bucket-old" in out
        assert ChangeType.REMOVED.value in out

    def test_modified_resource_appears_in_table(self):
        a = _res("queue-1")
        b = _res("queue-1")
        result = _make_result(_rdiff(ChangeType.MODIFIED, a=a, b=b))
        out = format_diff(result)
        assert "queue-1" in out
        assert ChangeType.MODIFIED.value in out

    def test_table_has_header_row(self):
        res = _res("fn-alpha", rtype="aws::lambda::function")
        result = _make_result(_rdiff(ChangeType.ADDED, b=res))
        out = format_diff(result)
        assert "Resource ID" in out
        assert "Type" in out
        assert "Stack" in out

    def test_summary_line_included(self):
        added = _res("r1")
        removed = _res("r2")
        result = _make_result(
            _rdiff(ChangeType.ADDED, b=added),
            _rdiff(ChangeType.REMOVED, a=removed),
        )
        out = format_diff(result)
        assert "1 added" in out
        assert "1 removed" in out

    def test_table_registered_in_formatter_registry(self):
        from stackdiff.formatters.registry import get_formatter
        fn = get_formatter("table")
        assert callable(fn)

    def test_long_resource_id_expands_column(self):
        long_id = "a" * 60
        res = _res(long_id)
        result = _make_result(_rdiff(ChangeType.ADDED, b=res))
        out = format_diff(result)
        assert long_id in out
        # Each data row should be the same width as the separator
        lines = [l for l in out.splitlines() if l.startswith("+")]
        row_lines = [l for l in out.splitlines() if l.startswith("|")]
        assert all(len(r) == len(lines[0]) for r in row_lines)
