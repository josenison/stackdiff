"""Tests for the PagerDuty formatter."""
from __future__ import annotations

import json

import pytest

from stackdiff.diff import ChangeType, DiffResult, ResourceDiff
from stackdiff.formatters.pagerduty_fmt import format_diff, _severity
from stackdiff.providers.base import Resource


def _res(rid: str, rtype: str = "aws::s3::bucket") -> Resource:
    return Resource(resource_id=rid, resource_type=rtype, properties={})


def _rdiff(rid: str, ct: ChangeType, rtype: str = "aws::s3::bucket") -> ResourceDiff:
    return ResourceDiff(
        resource_id=rid,
        resource_type=rtype,
        change_type=ct,
        source=_res(rid, rtype) if ct != ChangeType.ADDED else None,
        target=_res(rid, rtype) if ct != ChangeType.REMOVED else None,
    )


def _make_result(diffs: list[ResourceDiff]) -> DiffResult:
    return DiffResult(diffs=diffs)


class TestPagerDutyFormatter:
    def test_no_changes_event_action_resolve(self):
        result = _make_result([])
        data = json.loads(format_diff(result))
        assert data["event_action"] == "resolve"

    def test_no_changes_severity_info(self):
        result = _make_result([])
        data = json.loads(format_diff(result))
        assert data["payload"]["severity"] == "info"

    def test_added_resource_severity_warning(self):
        result = _make_result([_rdiff("bucket-1", ChangeType.ADDED)])
        data = json.loads(format_diff(result))
        assert data["payload"]["severity"] == "warning"

    def test_removed_resource_severity_critical(self):
        result = _make_result([_rdiff("bucket-1", ChangeType.REMOVED)])
        data = json.loads(format_diff(result))
        assert data["payload"]["severity"] == "critical"

    def test_modified_resource_severity_error(self):
        result = _make_result([_rdiff("bucket-1", ChangeType.MODIFIED)])
        data = json.loads(format_diff(result))
        assert data["payload"]["severity"] == "error"

    def test_changes_event_action_trigger(self):
        result = _make_result([_rdiff("bucket-1", ChangeType.ADDED)])
        data = json.loads(format_diff(result))
        assert data["event_action"] == "trigger"

    def test_routing_key_passed_through(self):
        result = _make_result([])
        data = json.loads(format_diff(result, routing_key="abc123"))
        assert data["routing_key"] == "abc123"

    def test_custom_details_contains_changes(self):
        result = _make_result([
            _rdiff("bucket-1", ChangeType.ADDED),
            _rdiff("bucket-2", ChangeType.REMOVED),
        ])
        data = json.loads(format_diff(result))
        changes = data["payload"]["custom_details"]["changes"]
        assert len(changes) == 2
        ids = {c["resource_id"] for c in changes}
        assert ids == {"bucket-1", "bucket-2"}

    def test_summary_includes_counts(self):
        result = _make_result([
            _rdiff("b1", ChangeType.ADDED),
            _rdiff("b2", ChangeType.REMOVED),
        ])
        data = json.loads(format_diff(result))
        summary = data["payload"]["summary"]
        assert "1" in summary
        assert "added" in summary.lower() or "removed" in summary.lower()


class TestSeverityHelper:
    """Unit tests for the internal _severity helper function."""

    def test_severity_no_diffs(self):
        assert _severity([]) == "info"

    def test_severity_added_only(self):
        diffs = [_rdiff("r1", ChangeType.ADDED)]
        assert _severity(diffs) == "warning"

    def test_severity_removed_only(self):
        diffs = [_rdiff("r1", ChangeType.REMOVED)]
        assert _severity(diffs) == "critical"

    def test_severity_modified_only(self):
        diffs = [_rdiff("r1", ChangeType.MODIFIED)]
        assert _severity(diffs) == "error"

    def test_severity_removed_dominates_added(self):
        """REMOVED should produce the highest severity even when mixed with ADDED."""
        diffs = [
            _rdiff("r1", ChangeType.ADDED),
            _rdiff("r2", ChangeType.REMOVED),
        ]
        assert _severity(diffs) == "critical"
