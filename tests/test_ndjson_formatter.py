"""Tests for the NDJSON formatter."""
from __future__ import annotations

import json
import pytest

from stackdiff.diff import ChangeType, DiffResult, ResourceDiff
from stackdiff.formatters.ndjson_fmt import format_diff


def _res(rid: str, rtype: str = "aws::s3::bucket"):
    from stackdiff.providers.base import Resource
    return Resource(resource_id=rid, resource_type=rtype, attributes={})


def _rdiff(
    change_type: ChangeType,
    rid: str = "res-1",
    rtype: str = "aws::s3::bucket",
    before=None,
    after=None,
    attribute_changes=None,
):
    return ResourceDiff(
        change_type=change_type,
        resource_id=rid,
        resource_type=rtype,
        before=before,
        after=after,
        attribute_changes=attribute_changes or {},
    )


def _make_result(diffs=None):
    diffs = diffs or []
    return DiffResult(diffs=diffs)


class TestNDJSONFormatter:
    def test_no_changes_returns_single_line(self):
        result = format_diff(_make_result())
        lines = [l for l in result.splitlines() if l.strip()]
        assert len(lines) == 1

    def test_no_changes_has_changes_false(self):
        data = json.loads(format_diff(_make_result()))
        assert data["has_changes"] is False

    def test_no_changes_counts_are_zero(self):
        data = json.loads(format_diff(_make_result()))
        assert data["added"] == 0
        assert data["removed"] == 0
        assert data["modified"] == 0

    def test_added_resource_produces_one_line(self):
        result = format_diff(_make_result([
            _rdiff(ChangeType.ADDED, rid="bucket-1"),
        ]))
        lines = [l for l in result.splitlines() if l.strip()]
        assert len(lines) == 1

    def test_added_resource_change_type(self):
        result = format_diff(_make_result([
            _rdiff(ChangeType.ADDED, rid="bucket-1"),
        ]))
        data = json.loads(result.splitlines()[0])
        assert data["change_type"] == "added"
        assert data["resource_id"] == "bucket-1"

    def test_multiple_diffs_produce_multiple_lines(self):
        result = format_diff(_make_result([
            _rdiff(ChangeType.ADDED, rid="r1"),
            _rdiff(ChangeType.REMOVED, rid="r2"),
            _rdiff(ChangeType.MODIFIED, rid="r3"),
        ]))
        lines = [l for l in result.splitlines() if l.strip()]
        assert len(lines) == 3

    def test_each_line_is_valid_json(self):
        result = format_diff(_make_result([
            _rdiff(ChangeType.ADDED, rid="r1"),
            _rdiff(ChangeType.REMOVED, rid="r2"),
        ]))
        for line in result.splitlines():
            json.loads(line)  # must not raise

    def test_attribute_changes_included(self):
        result = format_diff(_make_result([
            _rdiff(
                ChangeType.MODIFIED,
                rid="r1",
                attribute_changes={"size": {"before": "t2.micro", "after": "t3.small"}},
            )
        ]))
        data = json.loads(result.strip())
        assert "attribute_changes" in data
        assert data["attribute_changes"]["size"]["after"] == "t3.small"
