"""Tests for the Terraform plan-style formatter."""
from __future__ import annotations

import pytest

from stackdiff.diff import ChangeType, DiffResult, ResourceDiff
from stackdiff.providers.base import Resource
from stackdiff.formatters.terraform_plan_fmt import format_diff


def _res(rid: str, rtype: str = "aws_instance", **attrs) -> Resource:
    return Resource(resource_id=rid, resource_type=rtype, attributes=attrs)


def _rdiff(
    change_type: ChangeType,
    resource_a: Resource | None = None,
    resource_b: Resource | None = None,
) -> ResourceDiff:
    return ResourceDiff(change_type=change_type, resource_a=resource_a, resource_b=resource_b)


def _make_result(diffs: list[ResourceDiff]) -> DiffResult:
    return DiffResult(diffs=diffs)


class TestTerraformPlanFormatter:
    def test_no_changes_returns_up_to_date_message(self):
        result = _make_result([])
        out = format_diff(result)
        assert "No changes" in out
        assert "up-to-date" in out

    def test_header_always_present(self):
        result = _make_result([])
        out = format_diff(result)
        assert "Terraform plan-style diff" in out

    def test_added_resource_shown_with_plus(self):
        r = _res("i-123", "aws_instance", ami="ami-abc")
        result = _make_result([_rdiff(ChangeType.ADDED, resource_b=r)])
        out = format_diff(result)
        assert "+ resource" in out
        assert "i-123" in out

    def test_removed_resource_shown_with_minus(self):
        r = _res("i-456", "aws_instance")
        result = _make_result([_rdiff(ChangeType.REMOVED, resource_a=r)])
        out = format_diff(result)
        assert "- resource" in out
        assert "i-456" in out

    def test_modified_resource_shows_attribute_diff(self):
        old = _res("i-789", "aws_instance", instance_type="t2.micro")
        new = _res("i-789", "aws_instance", instance_type="t3.small")
        result = _make_result([_rdiff(ChangeType.MODIFIED, resource_a=old, resource_b=new)])
        out = format_diff(result)
        assert "~ resource" in out
        assert "t2.micro" in out
        assert "t3.small" in out

    def test_plan_summary_line_present(self):
        r = _res("i-001")
        result = _make_result([_rdiff(ChangeType.ADDED, resource_b=r)])
        out = format_diff(result)
        assert "Plan:" in out
        assert "1 to add" in out

    def test_colorize_injects_ansi_codes(self):
        r = _res("i-002")
        result = _make_result([_rdiff(ChangeType.ADDED, resource_b=r)])
        out = format_diff(result, colorize=True)
        assert "\033[32m" in out

    def test_unchanged_resources_not_shown(self):
        r = _res("i-003")
        result = _make_result([_rdiff(ChangeType.UNCHANGED, resource_a=r, resource_b=r)])
        out = format_diff(result)
        # unchanged => no changes overall
        assert "No changes" in out
