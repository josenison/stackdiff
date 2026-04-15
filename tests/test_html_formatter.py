"""Tests for the HTML formatter."""
from __future__ import annotations

import pytest

from stackdiff.diff import ChangeType, DiffResult, ResourceDiff
from stackdiff.formatters.html_fmt import format_diff
from stackdiff.providers.base import Resource


def _res(rid: str, rtype: str = "instance", **attrs) -> Resource:
    return Resource(resource_id=rid, resource_type=rtype, attributes=attrs)


def _rdiff(
    change_type: ChangeType,
    before: Resource | None = None,
    after: Resource | None = None,
) -> ResourceDiff:
    return ResourceDiff(change_type=change_type, resource_before=before, resource_after=after)


def _make_result(*diffs: ResourceDiff) -> DiffResult:
    return DiffResult(diffs=list(diffs))


class TestHTMLFormatter:
    def test_no_changes_returns_simple_message(self):
        result = _make_result()
        html = format_diff(result)
        assert "No changes" in html
        assert "<table" not in html

    def test_added_resource_shown(self):
        r = _res("i-123", "ec2")
        result = _make_result(_rdiff(ChangeType.ADDED, after=r))
        html = format_diff(result)
        assert "ADDED" in html
        assert "i-123" in html
        assert "ec2" in html

    def test_removed_resource_shown(self):
        r = _res("i-456", "s3bucket")
        result = _make_result(_rdiff(ChangeType.REMOVED, before=r))
        html = format_diff(result)
        assert "REMOVED" in html
        assert "i-456" in html

    def test_modified_resource_shows_diff(self):
        before = _res("i-789", "vm", size="small")
        after = _res("i-789", "vm", size="large")
        result = _make_result(_rdiff(ChangeType.MODIFIED, before=before, after=after))
        html = format_diff(result)
        assert "MODIFIED" in html
        assert "small" in html
        assert "large" in html
        assert "size" in html

    def test_unchanged_resources_not_rendered(self):
        r = _res("i-000", "vm")
        result = _make_result(_rdiff(ChangeType.UNCHANGED, before=r, after=r))
        html = format_diff(result)
        assert "No changes" in html
        assert "UNCHANGED" not in html

    def test_summary_counts_shown(self):
        added = _rdiff(ChangeType.ADDED, after=_res("a1"))
        removed = _rdiff(ChangeType.REMOVED, before=_res("r1"))
        result = _make_result(added, removed)
        html = format_diff(result)
        assert "Added: 1" in html
        assert "Removed: 1" in html

    def test_html_contains_table_structure(self):
        r = _res("x1", "bucket")
        result = _make_result(_rdiff(ChangeType.ADDED, after=r))
        html = format_diff(result)
        assert "<table" in html
        assert "<thead>" in html
        assert "<tbody>" in html
        assert "</table>" in html
