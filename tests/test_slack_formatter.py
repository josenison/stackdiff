"""Tests for the Slack Block Kit formatter."""
import json
import pytest
from stackdiff.diff import DiffResult, ResourceDiff, ChangeType
from stackdiff.providers.base import Resource
from stackdiff.formatters.slack_fmt import format_diff


def _res(rid: str, rtype: str = "instance") -> Resource:
    return Resource(id=rid, type=rtype, properties={"name": rid})


def _rdiff(rid, rtype, change_type, diff_lines=None):
    return ResourceDiff(
        resource_id=rid,
        resource_type=rtype,
        change_type=change_type,
        diff_lines=diff_lines or [],
    )


def _make_result(diffs):
    return DiffResult(diffs=diffs)


class TestSlackFormatter:
    def test_no_changes_returns_notice(self):
        result = _make_result([])
        output = json.loads(format_diff(result))
        assert "blocks" in output
        texts = [b.get("text", {}).get("text", "") for b in output["blocks"]]
        assert any("No changes" in t for t in texts)

    def test_added_resource_shown(self):
        result = _make_result([_rdiff("i-123", "instance", ChangeType.ADDED)])
        output = json.loads(format_diff(result))
        full = json.dumps(output)
        assert "ADDED" in full
        assert "i-123" in full

    def test_removed_resource_shown(self):
        result = _make_result([_rdiff("i-456", "bucket", ChangeType.REMOVED)])
        output = json.loads(format_diff(result))
        full = json.dumps(output)
        assert "REMOVED" in full
        assert "i-456" in full

    def test_modified_resource_includes_diff(self):
        lines = ["+  size: large", "-  size: small"]
        result = _make_result([_rdiff("i-789", "vm", ChangeType.MODIFIED, lines)])
        output = json.loads(format_diff(result))
        full = json.dumps(output)
        assert "MODIFIED" in full
        assert "size: large" in full

    def test_header_block_present_when_changes(self):
        result = _make_result([_rdiff("r-1", "disk", ChangeType.ADDED)])
        output = json.loads(format_diff(result))
        types = [b["type"] for b in output["blocks"]]
        assert "header" in types

    def test_summary_block_present(self):
        result = _make_result([_rdiff("r-2", "disk", ChangeType.REMOVED)])
        output = json.loads(format_diff(result))
        full = json.dumps(output)
        assert "Summary" in full
