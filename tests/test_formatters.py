"""Tests for the text and JSON formatters."""

import io
import json

import pytest

from stackdiff.diff import ChangeType, ResourceDiff, DiffResult
from stackdiff.formatters import text as text_fmt
from stackdiff.formatters import json_fmt


def _make_result(*diffs):
    return DiffResult(list(diffs))


def _rdiff(rid, rtype, change_type, attrs=None):
    return ResourceDiff(
        resource_id=rid,
        resource_type=rtype,
        change_type=change_type,
        attribute_diffs=attrs or {},
    )


class TestTextFormatter:
    def test_no_changes_message(self):
        out = io.StringIO()
        text_fmt.format_diff(_make_result(), out=out, color=False)
        assert "No changes detected" in out.getvalue()

    def test_added_resource_shown(self):
        diff = _rdiff("bucket-1", "S3::Bucket", ChangeType.ADDED)
        out = io.StringIO()
        text_fmt.format_diff(_make_result(diff), out=out, color=False)
        assert "+ [S3::Bucket] bucket-1" in out.getvalue()

    def test_removed_resource_shown(self):
        diff = _rdiff("queue-old", "SQS::Queue", ChangeType.REMOVED)
        out = io.StringIO()
        text_fmt.format_diff(_make_result(diff), out=out, color=False)
        assert "- [SQS::Queue] queue-old" in out.getvalue()

    def test_modified_attributes_shown(self):
        diff = _rdiff(
            "fn-1", "Lambda::Function", ChangeType.MODIFIED,
            attrs={"MemorySize": (128, 256)},
        )
        out = io.StringIO()
        text_fmt.format_diff(_make_result(diff), out=out, color=False)
        content = out.getvalue()
        assert "MemorySize" in content
        assert "128" in content
        assert "256" in content

    def test_summary_line_present(self):
        diff = _rdiff("tbl", "DynamoDB::Table", ChangeType.ADDED)
        out = io.StringIO()
        text_fmt.format_diff(_make_result(diff), out=out, color=False)
        assert "Summary:" in out.getvalue()


class TestJsonFormatter:
    def test_no_changes_payload(self):
        out = io.StringIO()
        json_fmt.format_diff(_make_result(), out=out)
        data = json.loads(out.getvalue())
        assert data["has_changes"] is False
        assert data["changes"] == []

    def test_added_resource_in_changes(self):
        diff = _rdiff("bucket-2", "S3::Bucket", ChangeType.ADDED)
        out = io.StringIO()
        json_fmt.format_diff(_make_result(diff), out=out)
        data = json.loads(out.getvalue())
        assert data["has_changes"] is True
        assert data["changes"][0]["resource_id"] == "bucket-2"
        assert data["changes"][0]["change_type"] == "added"

    def test_modified_attributes_in_json(self):
        diff = _rdiff(
            "fn-2", "Lambda::Function", ChangeType.MODIFIED,
            attrs={"Timeout": (30, 60)},
        )
        out = io.StringIO()
        json_fmt.format_diff(_make_result(diff), out=out)
        data = json.loads(out.getvalue())
        attrs = data["changes"][0]["attributes"]
        assert attrs["Timeout"]["old"] == 30
        assert attrs["Timeout"]["new"] == 60
