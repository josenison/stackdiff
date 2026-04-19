"""Tests for the badge formatter."""
from __future__ import annotations

import json

import pytest

from stackdiff.diff import ChangeType, DiffResult, ResourceDiff
from stackdiff.providers.base import Resource
from stackdiff.formatters.badge_fmt import format_diff


def _res(rid: str) -> Resource:
    return Resource(id=rid, type="aws::s3::bucket", name=rid, attributes={})


def _rdiff(rid: str, change: ChangeType) -> ResourceDiff:
    r = _res(rid)
    before = r if change in (ChangeType.REMOVED, ChangeType.MODIFIED) else None
    after = r if change in (ChangeType.ADDED, ChangeType.MODIFIED) else None
    return ResourceDiff(resource_id=rid, change_type=change, before=before, after=after)


def _make_result(diffs: list[ResourceDiff]) -> DiffResult:
    return DiffResult(diffs=diffs)


class TestBadgeFormatter:
    def test_no_changes_color_brightgreen(self):
        result = _make_result([])
        data = json.loads(format_diff(result))
        assert data["color"] == "brightgreen"

    def test_no_changes_message_in_sync(self):
        result = _make_result([])
        data = json.loads(format_diff(result))
        assert data["message"] == "in sync"

    def test_no_changes_is_error_false(self):
        result = _make_result([])
        data = json.loads(format_diff(result))
        assert data["isError"] is False

    def test_added_only_color_yellow(self):
        result = _make_result([_rdiff("r1", ChangeType.ADDED)])
        data = json.loads(format_diff(result))
        assert data["color"] == "yellow"

    def test_removed_color_red(self):
        result = _make_result([_rdiff("r1", ChangeType.REMOVED)])
        data = json.loads(format_diff(result))
        assert data["color"] == "red"

    def test_modified_color_orange(self):
        result = _make_result([_rdiff("r1", ChangeType.MODIFIED)])
        data = json.loads(format_diff(result))
        assert data["color"] == "orange"

    def test_message_includes_counts(self):
        result = _make_result([
            _rdiff("r1", ChangeType.ADDED),
            _rdiff("r2", ChangeType.REMOVED),
        ])
        data = json.loads(format_diff(result))
        assert "1 added" in data["message"]
        assert "1 removed" in data["message"]

    def test_custom_label(self):
        result = _make_result([])
        data = json.loads(format_diff(result, label="infra"))
        assert data["label"] == "infra"

    def test_schema_version(self):
        result = _make_result([])
        data = json.loads(format_diff(result))
        assert data["schemaVersion"] == 1
