"""Tests for the webhook formatter."""
from __future__ import annotations

import json

import pytest

from stackdiff.diff import ChangeType, DiffResult, ResourceDiff
from stackdiff.formatters.webhook_fmt import format_diff
from stackdiff.providers.base import Resource


def _res(rid: str, rtype: str = "instance") -> Resource:
    return Resource(id=rid, type=rtype, properties={})


def _rdiff(
    rid: str,
    change: ChangeType,
    rtype: str = "instance",
    detail: str | None = None,
) -> ResourceDiff:
    return ResourceDiff(
        resource_id=rid,
        resource_type=rtype,
        change_type=change,
        before=None,
        after=None,
        diff_detail=detail,
    )


def _make_result(diffs: list[ResourceDiff]) -> DiffResult:
    return DiffResult(diffs=diffs)


class TestWebhookFormatter:
    def test_no_changes_has_changes_false(self):
        result = _make_result([])
        payload = json.loads(format_diff(result))
        assert payload["has_changes"] is False

    def test_no_changes_all_counts_zero(self):
        result = _make_result([])
        payload = json.loads(format_diff(result))
        s = payload["summary"]
        assert s["added"] == 0
        assert s["removed"] == 0
        assert s["modified"] == 0
        assert s["total"] == 0

    def test_added_resource_reflected(self):
        result = _make_result([_rdiff("i-1", ChangeType.ADDED)])
        payload = json.loads(format_diff(result))
        assert payload["has_changes"] is True
        assert payload["summary"]["added"] == 1
        assert payload["changes"][0]["change_type"] == "added"
        assert payload["changes"][0]["resource_id"] == "i-1"

    def test_removed_resource_reflected(self):
        result = _make_result([_rdiff("i-2", ChangeType.REMOVED)])
        payload = json.loads(format_diff(result))
        assert payload["summary"]["removed"] == 1

    def test_diff_detail_included_when_present(self):
        result = _make_result([_rdiff("i-3", ChangeType.MODIFIED, detail="cpu changed")])
        payload = json.loads(format_diff(result))
        assert payload["changes"][0]["detail"] == "cpu changed"

    def test_no_detail_key_when_absent(self):
        result = _make_result([_rdiff("i-4", ChangeType.ADDED)])
        payload = json.loads(format_diff(result))
        assert "detail" not in payload["changes"][0]

    def test_timestamp_present(self):
        result = _make_result([])
        payload = json.loads(format_diff(result))
        assert "timestamp" in payload
        assert payload["timestamp"].endswith("+00:00")

    def test_multiple_changes_counted_correctly(self):
        diffs = [
            _rdiff("a", ChangeType.ADDED),
            _rdiff("b", ChangeType.REMOVED),
            _rdiff("c", ChangeType.MODIFIED),
            _rdiff("d", ChangeType.UNCHANGED),
        ]
        payload = json.loads(format_diff(_make_result(diffs)))
        s = payload["summary"]
        assert s["added"] == 1
        assert s["removed"] == 1
        assert s["modified"] == 1
        assert s["unchanged"] == 1
        assert s["total"] == 4
