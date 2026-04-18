import json
import pytest
from stackdiff.diff import ChangeType, DiffResult, ResourceDiff
from stackdiff.formatters.splunk_fmt import format_diff


def _res(rid, rtype="AWS::S3::Bucket"):
    from stackdiff.providers.base import Resource
    return Resource(id=rid, type=rtype, properties={"name": rid})


def _rdiff(rid, change_type, before=None, after=None):
    return ResourceDiff(
        resource_id=rid,
        resource_type="AWS::S3::Bucket",
        change_type=change_type,
        before=before,
        after=after,
    )


def _make_result(diffs):
    return DiffResult(diffs=diffs)


class TestSplunkFormatter:
    def test_no_changes_returns_single_event(self):
        result = _make_result([])
        output = format_diff(result)
        lines = output.strip().splitlines()
        assert len(lines) == 1
        data = json.loads(lines[0])
        assert data["event"]["has_changes"] is False

    def test_no_changes_event_has_summary(self):
        result = _make_result([])
        data = json.loads(format_diff(result))
        assert "summary" in data["event"]

    def test_added_resource_produces_event(self):
        result = _make_result([_rdiff("bucket-1", ChangeType.ADDED, after={"name": "bucket-1"})])
        lines = format_diff(result).strip().splitlines()
        assert len(lines) == 1
        data = json.loads(lines[0])
        assert data["event"]["change_type"] == "added"
        assert data["event"]["resource_id"] == "bucket-1"

    def test_multiple_diffs_produce_multiple_lines(self):
        diffs = [
            _rdiff("b1", ChangeType.ADDED, after={"x": 1}),
            _rdiff("b2", ChangeType.REMOVED, before={"x": 2}),
        ]
        result = _make_result(diffs)
        lines = format_diff(result).strip().splitlines()
        assert len(lines) == 2

    def test_each_line_is_valid_json(self):
        diffs = [_rdiff(f"r{i}", ChangeType.ADDED, after={}) for i in range(5)]
        result = _make_result(diffs)
        for line in format_diff(result).strip().splitlines():
            json.loads(line)  # must not raise

    def test_sourcetype_is_stackdiff(self):
        result = _make_result([_rdiff("x", ChangeType.MODIFIED, before={}, after={"k": "v"})])
        data = json.loads(format_diff(result).splitlines()[0])
        assert data["sourcetype"] == "stackdiff"

    def test_custom_source(self):
        result = _make_result([])
        data = json.loads(format_diff(result, source="my-pipeline"))
        assert data["source"] == "my-pipeline"
