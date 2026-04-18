"""Tests for the Datadog formatter."""
from __future__ import annotations

import json
import pytest

from stackdiff.diff import ChangeType, DiffResult, ResourceDiff
from stackdiff.providers.base import Resource
from stackdiff.formatters.datadog_fmt import format_diff


def _res(rid: str, rtype: str = "instance") -> Resource:
    return Resource(resource_id=rid, resource_type=rtype, attributes={})


def _rdiff(rid: str, change: ChangeType, rtype: str = "instance") -> ResourceDiff:
    r = _res(rid, rtype)
    return ResourceDiff(
        resource_id=rid,
        resource_type=rtype,
        change_type=change,
        left=None if change == ChangeType.ADDED else r,
        right=None if change == ChangeType.REMOVED else r,
    )


def _make_result(diffs: list[ResourceDiff]) -> DiffResult:
    return DiffResult(diffs=diffs)


class TestDatadogFormatter:
    def test_no_changes_alert_type_success(self):
        payload = json.loads(format_diff(_make_result([])))
        assert payload["alert_type"] == "success"

    def test_no_changes_title(self):
        payload = json.loads(format_diff(_make_result([])))
        assert "no changes" in payload["title"]

    def test_added_resource_alert_type_info(self):
        result = _make_result([_rdiff("i-1", ChangeType.ADDED)])
        payload = json.loads(format_diff(result))
        assert payload["alert_type"] == "info"

    def test_removed_resource_alert_type_error(self):
        result = _make_result([_rdiff("i-1", ChangeType.REMOVED)])
        payload = json.loads(format_diff(result))
        assert payload["alert_type"] == "error"

    def test_modified_resource_alert_type_warning(self):
        result = _make_result([_rdiff("i-1", ChangeType.MODIFIED)])
        payload = json.loads(format_diff(result))
        assert payload["alert_type"] == "warning"

    def test_tags_contain_counts(self):
        result = _make_result([
            _rdiff("i-1", ChangeType.ADDED),
            _rdiff("i-2", ChangeType.REMOVED),
        ])
        payload = json.loads(format_diff(result))
        assert "added:1" in payload["tags"]
        assert "removed:1" in payload["tags"]

    def test_text_contains_resource_id(self):
        result = _make_result([_rdiff("i-abc", ChangeType.ADDED)])
        payload = json.loads(format_diff(result))
        assert "i-abc" in payload["text"]

    def test_source_type_name(self):
        payload = json.loads(format_diff(_make_result([])))
        assert payload["source_type_name"] == "stackdiff"
