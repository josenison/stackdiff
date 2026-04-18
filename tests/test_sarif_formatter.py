"""Tests for the SARIF formatter."""
from __future__ import annotations

import json

import pytest

from stackdiff.diff import ChangeType, DiffResult, ResourceDiff
from stackdiff.formatters.sarif_fmt import format_diff
from stackdiff.providers.base import Resource


def _res(rid: str, rtype: str = "aws::s3::bucket") -> Resource:
    return Resource(id=rid, type=rtype, properties={})


def _rdiff(rid: str, change: ChangeType, rtype: str = "aws::s3::bucket") -> ResourceDiff:
    r = _res(rid, rtype)
    return ResourceDiff(
        resource_id=rid,
        resource_type=rtype,
        change_type=change,
        source=r if change != ChangeType.ADDED else None,
        target=r if change != ChangeType.REMOVED else None,
    )


def _make_result(*diffs: ResourceDiff) -> DiffResult:
    return DiffResult(diffs=list(diffs))


class TestSARIFFormatter:
    def test_no_changes_produces_empty_results(self):
        r = _make_result(_rdiff("bucket-1", ChangeType.UNCHANGED))
        out = json.loads(format_diff(r))
        assert out["runs"][0]["results"] == []

    def test_schema_and_version_present(self):
        r = _make_result()
        out = json.loads(format_diff(r))
        assert out["version"] == "2.1.0"
        assert "$schema" in out

    def test_added_resource_produces_warning(self):
        r = _make_result(_rdiff("new-bucket", ChangeType.ADDED))
        out = json.loads(format_diff(r))
        results = out["runs"][0]["results"]
        assert len(results) == 1
        assert results[0]["level"] == "warning"
        assert results[0]["ruleId"] == "added"

    def test_removed_resource_produces_error(self):
        r = _make_result(_rdiff("old-bucket", ChangeType.REMOVED))
        out = json.loads(format_diff(r))
        results = out["runs"][0]["results"]
        assert results[0]["level"] == "error"

    def test_modified_resource_in_results(self):
        r = _make_result(_rdiff("mod-bucket", ChangeType.MODIFIED))
        out = json.loads(format_diff(r))
        results = out["runs"][0]["results"]
        assert len(results) == 1
        assert results[0]["ruleId"] == "modified"

    def test_logical_location_contains_resource_id(self):
        r = _make_result(_rdiff("my-bucket", ChangeType.ADDED))
        out = json.loads(format_diff(r))
        loc = out["runs"][0]["results"][0]["locations"][0]["logicalLocations"][0]
        assert loc["name"] == "my-bucket"
        assert loc["kind"] == "aws::s3::bucket"

    def test_tool_driver_name_is_stackdiff(self):
        r = _make_result()
        out = json.loads(format_diff(r))
        assert out["runs"][0]["tool"]["driver"]["name"] == "stackdiff"
