"""Tests for the Ansible formatter."""
from __future__ import annotations

import json

import pytest

from stackdiff.diff import ChangeType, DiffResult, ResourceDiff
from stackdiff.formatters.ansible_fmt import format_diff
from stackdiff.providers.base import Resource


def _res(rid: str, rtype: str = "aws_instance", **attrs) -> Resource:
    return Resource(id=rid, type=rtype, attributes=attrs)


def _rdiff(
    rid: str,
    change_type: ChangeType,
    left: Resource | None = None,
    right: Resource | None = None,
) -> ResourceDiff:
    return ResourceDiff(
        resource_id=rid,
        resource_type=left.type if left else (right.type if right else "unknown"),
        change_type=change_type,
        left=left,
        right=right,
    )


def _make_result(*diffs: ResourceDiff) -> DiffResult:
    return DiffResult(diffs=list(diffs))


class TestAnsibleFormatter:
    def test_no_changes_changed_false(self):
        result = _make_result()
        data = json.loads(format_diff(result))
        assert data["changed"] is False

    def test_no_changes_failed_false(self):
        result = _make_result()
        data = json.loads(format_diff(result))
        assert data["failed"] is False

    def test_no_changes_empty_changes_list(self):
        result = _make_result()
        data = json.loads(format_diff(result))
        assert data["stackdiff"]["changes"] == []

    def test_no_changes_msg_contains_no_changes(self):
        result = _make_result()
        data = json.loads(format_diff(result))
        assert "No infrastructure changes" in data["msg"]

    def test_added_resource_changed_true(self):
        r = _res("i-123")
        result = _make_result(_rdiff("i-123", ChangeType.ADDED, right=r))
        data = json.loads(format_diff(result))
        assert data["changed"] is True

    def test_added_resource_in_changes(self):
        r = _res("i-123")
        result = _make_result(_rdiff("i-123", ChangeType.ADDED, right=r))
        data = json.loads(format_diff(result))
        assert len(data["stackdiff"]["changes"]) == 1
        assert data["stackdiff"]["changes"][0]["change_type"] == "added"

    def test_removed_resource_counts(self):
        r = _res("i-456")
        result = _make_result(_rdiff("i-456", ChangeType.REMOVED, left=r))
        data = json.loads(format_diff(result))
        assert data["stackdiff"]["counts"]["removed"] == 1

    def test_unchanged_resource_not_in_changes(self):
        r = _res("i-789")
        result = _make_result(_rdiff("i-789", ChangeType.UNCHANGED, left=r, right=r))
        data = json.loads(format_diff(result))
        assert data["stackdiff"]["changes"] == []
        assert data["changed"] is False

    def test_modified_resource_has_left_and_right(self):
        left = _res("i-999", size="small")
        right = _res("i-999", size="large")
        result = _make_result(_rdiff("i-999", ChangeType.MODIFIED, left=left, right=right))
        data = json.loads(format_diff(result))
        change = data["stackdiff"]["changes"][0]
        assert change["left"]["attributes"]["size"] == "small"
        assert change["right"]["attributes"]["size"] == "large"

    def test_output_is_valid_json(self):
        r = _res("i-abc")
        result = _make_result(_rdiff("i-abc", ChangeType.ADDED, right=r))
        output = format_diff(result)
        parsed = json.loads(output)  # must not raise
        assert isinstance(parsed, dict)
