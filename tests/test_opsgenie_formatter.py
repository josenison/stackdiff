"""Tests for the OpsGenie alert payload formatter."""
import json
import pytest
from stackdiff.diff import DiffResult, ResourceDiff, ChangeType
from stackdiff.formatters.opsgenie_fmt import format_diff


def _rdiff(rid, rtype, change_type):
    return ResourceDiff(resource_id=rid, resource_type=rtype, change_type=change_type, diff_lines=[])


def _make_result(diffs):
    return DiffResult(diffs=diffs)


class TestOpsGenieFormatter:
    def test_no_changes_returns_p5(self):
        result = _make_result([])
        output = json.loads(format_diff(result))
        assert output["priority"] == "P5"
        assert "No infrastructure changes" in output["message"]

    def test_single_added_is_p4(self):
        result = _make_result([_rdiff("r-1", "instance", ChangeType.ADDED)])
        output = json.loads(format_diff(result))
        assert output["priority"] == "P4"

    def test_removed_resources_raise_priority(self):
        diffs = [_rdiff(f"r-{i}", "instance", ChangeType.REMOVED) for i in range(4)]
        result = _make_result(diffs)
        output = json.loads(format_diff(result))
        assert output["priority"] == "P1"

    def test_details_contains_resource_ids(self):
        result = _make_result([_rdiff("i-abc", "bucket", ChangeType.ADDED)])
        output = json.loads(format_diff(result))
        assert "i-abc" in output["details"]

    def test_tags_contain_resource_types(self):
        result = _make_result([
            _rdiff("r-1", "vm", ChangeType.ADDED),
            _rdiff("r-2", "disk", ChangeType.REMOVED),
        ])
        output = json.loads(format_diff(result))
        assert "vm" in output["tags"]
        assert "disk" in output["tags"]

    def test_message_contains_summary(self):
        result = _make_result([_rdiff("r-9", "lb", ChangeType.MODIFIED)])
        output = json.loads(format_diff(result))
        assert "diff" in output["message"].lower()
