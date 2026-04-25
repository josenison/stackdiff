"""Tests for the cdktf plan-style formatter."""
from __future__ import annotations

import pytest

from stackdiff.diff import ChangeType, DiffResult, ResourceDiff
from stackdiff.formatters.cdktf_fmt import format_diff
from stackdiff.providers.base import Resource, StackState


def _res(rid: str, rtype: str = "aws_instance") -> Resource:
    return Resource(resource_id=rid, resource_type=rtype, properties={})


def _rdiff(
    rid: str,
    change_type: ChangeType,
    rtype: str = "aws_instance",
    diff_details: dict | None = None,
) -> ResourceDiff:
    return ResourceDiff(
        resource=_res(rid, rtype),
        change_type=change_type,
        diff_details=diff_details or {},
    )


def _make_result(*diffs: ResourceDiff) -> DiffResult:
    return DiffResult(changes=list(diffs))


class TestCDKTFFormatter:
    def test_no_changes_returns_up_to_date_message(self):
        result = _make_result()
        out = format_diff(result)
        assert "up-to-date" in out

    def test_added_resource_shows_plus_symbol(self):
        result = _make_result(_rdiff("i-123", ChangeType.ADDED))
        out = format_diff(result)
        assert "+ aws_instance.i-123" in out

    def test_removed_resource_shows_minus_symbol(self):
        result = _make_result(_rdiff("i-456", ChangeType.REMOVED))
        out = format_diff(result)
        assert "- aws_instance.i-456" in out

    def test_modified_resource_shows_tilde_symbol(self):
        result = _make_result(_rdiff("i-789", ChangeType.MODIFIED))
        out = format_diff(result)
        assert "~ aws_instance.i-789" in out

    def test_modified_resource_shows_diff_details(self):
        details = {"instance_type": {"before": "t2.micro", "after": "t3.small"}}
        result = _make_result(_rdiff("i-abc", ChangeType.MODIFIED, diff_details=details))
        out = format_diff(result)
        assert "instance_type" in out
        assert "t2.micro" in out
        assert "t3.small" in out

    def test_plan_summary_line_present(self):
        result = _make_result(
            _rdiff("i-1", ChangeType.ADDED),
            _rdiff("i-2", ChangeType.REMOVED),
        )
        out = format_diff(result)
        assert "Plan:" in out
        assert "1 to add" in out
        assert "1 to destroy" in out

    def test_unchanged_resources_not_rendered(self):
        result = _make_result(_rdiff("i-unchanged", ChangeType.UNCHANGED))
        out = format_diff(result)
        assert "up-to-date" in out

    def test_use_color_flag_injects_ansi_codes(self):
        result = _make_result(_rdiff("i-colored", ChangeType.ADDED))
        out = format_diff(result, use_color=True)
        assert "\033[32m" in out

    def test_no_color_by_default(self):
        result = _make_result(_rdiff("i-plain", ChangeType.ADDED))
        out = format_diff(result)
        assert "\033[" not in out
