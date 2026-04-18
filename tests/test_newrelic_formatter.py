"""Tests for the New Relic custom event formatter."""
from __future__ import annotations

import json

from stackdiff.diff import ChangeType, DiffResult, ResourceDiff
from stackdiff.formatters.newrelic_fmt import format_diff
from stackdiff.providers.base import Resource


def _res(rid: str) -> Resource:
    return Resource(resource_id=rid, resource_type="vm", attributes={})


def _rdiff(rid: str, change: ChangeType) -> ResourceDiff:
    r = _res(rid)
    return ResourceDiff(
        resource_id=rid,
        resource_type="vm",
        change_type=change,
        left=None if change == ChangeType.ADDED else r,
        right=None if change == ChangeType.REMOVED else r,
    )


def _make_result(diffs: list[ResourceDiff]) -> DiffResult:
    return DiffResult(diffs=diffs)


class TestNewRelicFormatter:
    def _parse(self, result: DiffResult) -> dict:
        return json.loads(format_diff(result))[0]

    def test_no_changes_severity_info(self):
        event = self._parse(_make_result([]))
        assert event["severity"] == "INFO"

    def test_no_changes_has_changes_false(self):
        event = self._parse(_make_result([]))
        assert event["hasChanges"] is False

    def test_removed_resource_severity_critical(self):
        event = self._parse(_make_result([_rdiff("i-1", ChangeType.REMOVED)]))
        assert event["severity"] == "CRITICAL"

    def test_modified_resource_severity_warning(self):
        event = self._parse(_make_result([_rdiff("i-1", ChangeType.MODIFIED)]))
        assert event["severity"] == "WARNING"

    def test_added_only_severity_info(self):
        event = self._parse(_make_result([_rdiff("i-1", ChangeType.ADDED)]))
        assert event["severity"] == "INFO"

    def test_total_changes_count(self):
        result = _make_result([
            _rdiff("i-1", ChangeType.ADDED),
            _rdiff("i-2", ChangeType.REMOVED),
        ])
        event = self._parse(result)
        assert event["totalChanges"] == 2

    def test_event_type_field(self):
        event = self._parse(_make_result([]))
        assert event["eventType"] == "StackDiffEvent"

    def test_output_is_list(self):
        raw = format_diff(_make_result([]))
        assert isinstance(json.loads(raw), list)
