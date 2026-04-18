"""Tests for the Grafana annotation formatter."""
from __future__ import annotations

import json

import pytest

from stackdiff.diff import ChangeType, DiffResult, ResourceDiff
from stackdiff.formatters.grafana_fmt import format_diff
from stackdiff.providers.base import Resource


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


class TestGrafanaFormatter:
    def test_no_changes_returns_clean_tag(self):
        result = _make_result([])
        payload = json.loads(format_diff(result))
        assert "clean" in payload["tags"]
        assert "drift" not in payload["tags"]

    def test_no_changes_text(self):
        result = _make_result([])
        payload = json.loads(format_diff(result))
        assert "No infrastructure changes" in payload["text"]

    def test_changes_returns_drift_tag(self):
        result = _make_result([_rdiff("i-1", ChangeType.ADDED)])
        payload = json.loads(format_diff(result))
        assert "drift" in payload["tags"]
        assert "clean" not in payload["tags"]

    def test_added_resource_in_text(self):
        result = _make_result([_rdiff("i-1", ChangeType.ADDED)])
        payload = json.loads(format_diff(result))
        assert "i-1" in payload["text"]
        assert ChangeType.ADDED.value in payload["text"]

    def test_multiple_diffs_all_in_text(self):
        result = _make_result([
            _rdiff("i-1", ChangeType.ADDED),
            _rdiff("i-2", ChangeType.REMOVED),
        ])
        payload = json.loads(format_diff(result))
        assert "i-1" in payload["text"]
        assert "i-2" in payload["text"]

    def test_payload_has_time_field(self):
        result = _make_result([])
        payload = json.loads(format_diff(result))
        assert isinstance(payload["time"], int)
        assert payload["time"] > 0

    def test_stackdiff_tag_always_present(self):
        for diffs in [[], [_rdiff("x", ChangeType.ADDED)]]:
            payload = json.loads(format_diff(_make_result(diffs)))
            assert "stackdiff" in payload["tags"]
