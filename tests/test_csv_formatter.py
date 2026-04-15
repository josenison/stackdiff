"""Tests for the CSV formatter."""

import csv
import io
import pytest

from stackdiff.diff import ChangeType, DiffResult, ResourceDiff
from stackdiff.providers.base import Resource
from stackdiff.formatters.csv_fmt import format_diff


def _res(rid: str, rtype: str = "Instance", **attrs) -> Resource:
    return Resource(resource_id=rid, resource_type=rtype, attributes=attrs)


def _rdiff(change_type: ChangeType, a=None, b=None) -> ResourceDiff:
    return ResourceDiff(change_type=change_type, resource_a=a, resource_b=b)


def _make_result(*changes: ResourceDiff) -> DiffResult:
    return DiffResult(changes=list(changes))


def _parse_csv(text: str):
    return list(csv.DictReader(io.StringIO(text)))


class TestCSVFormatter:
    def test_no_changes_returns_header_only(self):
        result = _make_result()
        output = format_diff(result)
        rows = _parse_csv(output)
        assert rows == []
        assert "resource_id" in output
        assert "change_type" in output

    def test_added_resource_row(self):
        res = _res("i-123", "Instance")
        result = _make_result(_rdiff(ChangeType.ADDED, b=res))
        rows = _parse_csv(format_diff(result))
        assert len(rows) == 1
        assert rows[0]["resource_id"] == "i-123"
        assert rows[0]["change_type"] == "added"
        assert rows[0]["stack-a"] == ""
        assert rows[0]["stack-b"] == "i-123"

    def test_removed_resource_row(self):
        res = _res("i-456", "Instance")
        result = _make_result(_rdiff(ChangeType.REMOVED, a=res))
        rows = _parse_csv(format_diff(result))
        assert len(rows) == 1
        assert rows[0]["resource_id"] == "i-456"
        assert rows[0]["change_type"] == "removed"
        assert rows[0]["stack-a"] == "i-456"
        assert rows[0]["stack-b"] == ""

    def test_modified_resource_row(self):
        a = _res("i-789", "Instance", size="t2.micro")
        b = _res("i-789", "Instance", size="t3.medium")
        result = _make_result(_rdiff(ChangeType.MODIFIED, a=a, b=b))
        rows = _parse_csv(format_diff(result))
        assert len(rows) == 1
        assert rows[0]["change_type"] == "modified"
        assert "t2.micro" in rows[0]["stack-a"]
        assert "t3.medium" in rows[0]["stack-b"]

    def test_custom_stack_names_as_column_headers(self):
        result = _make_result()
        output = format_diff(result, stack_a="prod", stack_b="staging")
        assert "prod" in output
        assert "staging" in output

    def test_multiple_changes_produce_multiple_rows(self):
        added = _rdiff(ChangeType.ADDED, b=_res("r-1"))
        removed = _rdiff(ChangeType.REMOVED, a=_res("r-2"))
        modified = _rdiff(ChangeType.MODIFIED, a=_res("r-3", x="1"), b=_res("r-3", x="2"))
        result = _make_result(added, removed, modified)
        rows = _parse_csv(format_diff(result))
        assert len(rows) == 3
        change_types = {r["change_type"] for r in rows}
        assert change_types == {"added", "removed", "modified"}
