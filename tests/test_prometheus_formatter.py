"""Tests for the Prometheus text exposition format formatter."""
from __future__ import annotations

import pytest

from stackdiff.diff import ChangeType, DiffResult, ResourceDiff
from stackdiff.formatters.prometheus_fmt import format_diff
from stackdiff.providers.base import Resource


def _res(rid: str, rtype: str = "instance") -> Resource:
    return Resource(id=rid, type=rtype, name=rid, attributes={})


def _rdiff(rid: str, change_type: ChangeType) -> ResourceDiff:
    r = _res(rid)
    return ResourceDiff(
        resource_id=rid,
        change_type=change_type,
        resource_a=r if change_type != ChangeType.ADDED else None,
        resource_b=r if change_type != ChangeType.REMOVED else None,
        attribute_diffs={},
    )


def _make_result(*diffs: ResourceDiff) -> DiffResult:
    return DiffResult(diffs=list(diffs))


class TestPrometheusFormatter:
    def test_no_changes_has_changes_zero(self):
        result = _make_result()
        output = format_diff(result)
        assert "stackdiff_has_changes" in output
        assert "} 0" in output

    def test_added_resource_increments_added_count(self):
        result = _make_result(_rdiff("r1", ChangeType.ADDED))
        output = format_diff(result)
        assert 'change_type="added"} 1' in output

    def test_removed_resource_increments_removed_count(self):
        result = _make_result(_rdiff("r1", ChangeType.REMOVED))
        output = format_diff(result)
        assert 'change_type="removed"} 1' in output

    def test_has_changes_one_when_diffs_exist(self):
        result = _make_result(_rdiff("r1", ChangeType.ADDED))
        output = format_diff(result)
        assert "stackdiff_has_changes" in output
        lines = [l for l in output.splitlines() if "has_changes" in l and not l.startswith("#")]
        assert lines
        assert lines[0].endswith("} 1")

    def test_diff_total_reflects_resource_count(self):
        result = _make_result(
            _rdiff("r1", ChangeType.ADDED),
            _rdiff("r2", ChangeType.REMOVED),
            _rdiff("r3", ChangeType.UNCHANGED),
        )
        output = format_diff(result)
        lines = [l for l in output.splitlines() if "diff_total" in l and not l.startswith("#")]
        assert lines
        assert lines[0].endswith("} 3")

    def test_custom_stack_labels_appear_in_output(self):
        result = _make_result()
        output = format_diff(result, stack_a="prod", stack_b="staging")
        assert 'stack_a="prod"' in output
        assert 'stack_b="staging"' in output

    def test_output_ends_with_newline(self):
        result = _make_result()
        output = format_diff(result)
        assert output.endswith("\n")

    def test_help_and_type_lines_present(self):
        result = _make_result()
        output = format_diff(result)
        assert "# HELP" in output
        assert "# TYPE" in output
