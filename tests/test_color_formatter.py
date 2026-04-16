"""Tests for the coloured terminal formatter."""
import pytest
from stackdiff.diff import ChangeType, DiffResult, ResourceDiff
from stackdiff.providers.base import Resource
from stackdiff.formatters.color_fmt import format_diff


def _res(rid: str, rtype: str = "Instance", **attrs) -> Resource:
    return Resource(resource_id=rid, resource_type=rtype, attributes=attrs)


def _rdiff(change: ChangeType, before=None, after=None, attr_diffs=None) -> ResourceDiff:
    return ResourceDiff(
        change_type=change,
        resource_before=before,
        resource_after=after,
        attribute_diffs=attr_diffs or {},
    )


def _make_result(*diffs) -> DiffResult:
    return DiffResult(diffs=list(diffs))


class TestColorFormatter:
    def test_no_changes_plain(self):
        result = _make_result()
        out = format_diff(result, color=False)
        assert out == "No changes detected."

    def test_no_changes_with_color_contains_reset(self):
        result = _make_result()
        out = format_diff(result)
        assert "\033[0m" in out
        assert "No changes detected." in out

    def test_added_resource_shown(self):
        r = _res("i-123")
        result = _make_result(_rdiff(ChangeType.ADDED, after=r))
        out = format_diff(result, color=False)
        assert "+" in out
        assert "i-123" in out

    def test_removed_resource_shown(self):
        r = _res("i-456")
        result = _make_result(_rdiff(ChangeType.REMOVED, before=r))
        out = format_diff(result, color=False)
        assert "-" in out
        assert "i-456" in out

    def test_modified_shows_attribute_diffs(self):
        before = _res("i-789", size="t2.micro")
        after = _res("i-789", size="t3.small")
        rd = _rdiff(
            ChangeType.MODIFIED,
            before=before,
            after=after,
            attr_diffs={"size": ("t2.micro", "t3.small")},
        )
        out = format_diff(_make_result(rd), color=False)
        assert "size" in out
        assert "t2.micro" in out
        assert "t3.small" in out

    def test_color_codes_present_for_added(self):
        r = _res("i-001")
        result = _make_result(_rdiff(ChangeType.ADDED, after=r))
        out = format_diff(result, color=True)
        assert "\033[32m" in out  # green for added

    def test_color_codes_present_for_removed(self):
        r = _res("i-002")
        result = _make_result(_rdiff(ChangeType.REMOVED, before=r))
        out = format_diff(result, color=True)
        assert "\033[31m" in out  # red for removed

    def test_summary_line_present(self):
        r = _res("i-003")
        result = _make_result(_rdiff(ChangeType.ADDED, after=r))
        out = format_diff(result, color=False)
        assert "Diff:" in out
