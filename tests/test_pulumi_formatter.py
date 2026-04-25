"""Tests for the Pulumi-style output formatter."""
from __future__ import annotations

import pytest

from stackdiff.diff import ChangeType, DiffResult, ResourceDiff
from stackdiff.formatters.pulumi_fmt import format_diff
from stackdiff.providers.base import Resource


def _res(rid: str, rtype: str = "aws:s3:Bucket") -> Resource:
    return Resource(resource_id=rid, resource_type=rtype, properties={})


def _rdiff(
    rid: str,
    change_type: ChangeType,
    rtype: str = "aws:s3:Bucket",
    diff_details: dict | None = None,
) -> ResourceDiff:
    return ResourceDiff(
        resource_id=rid,
        resource_type=rtype,
        change_type=change_type,
        source_resource=_res(rid, rtype) if change_type != ChangeType.ADDED else None,
        target_resource=_res(rid, rtype) if change_type != ChangeType.REMOVED else None,
        diff_details=diff_details or {},
    )


def _make_result(diffs: list[ResourceDiff]) -> DiffResult:
    return DiffResult(changes=diffs)


class TestPulumiFormatter:
    def test_no_changes_returns_no_changes_message(self):
        result = _make_result([])
        output = format_diff(result)
        assert "no changes" in output

    def test_added_resource_shows_plus_symbol(self):
        result = _make_result([_rdiff("bucket-1", ChangeType.ADDED)])
        output = format_diff(result)
        assert "+" in output
        assert "bucket-1" in output

    def test_removed_resource_shows_minus_symbol(self):
        result = _make_result([_rdiff("bucket-2", ChangeType.REMOVED)])
        output = format_diff(result)
        assert "-" in output
        assert "bucket-2" in output

    def test_modified_resource_shows_tilde_symbol(self):
        result = _make_result([_rdiff("bucket-3", ChangeType.MODIFIED)])
        output = format_diff(result)
        assert "~" in output
        assert "bucket-3" in output

    def test_modified_resource_shows_diff_details(self):
        diff = _rdiff(
            "bucket-3",
            ChangeType.MODIFIED,
            diff_details={"versioning": ("false", "true")},
        )
        output = format_diff(_make_result([diff]))
        assert "versioning" in output
        assert "false" in output
        assert "true" in output

    def test_summary_line_shows_counts(self):
        result = _make_result(
            [
                _rdiff("a", ChangeType.ADDED),
                _rdiff("b", ChangeType.REMOVED),
                _rdiff("c", ChangeType.MODIFIED),
            ]
        )
        output = format_diff(result)
        assert "1 to add" in output
        assert "1 to remove" in output
        assert "1 to change" in output

    def test_color_flag_injects_ansi_codes(self):
        result = _make_result([_rdiff("bucket-1", ChangeType.ADDED)])
        output = format_diff(result, color=True)
        assert "\033[" in output

    def test_no_color_flag_has_no_ansi_codes(self):
        result = _make_result([_rdiff("bucket-1", ChangeType.ADDED)])
        output = format_diff(result, color=False)
        assert "\033[" not in output

    def test_preview_header_present(self):
        result = _make_result([_rdiff("x", ChangeType.ADDED)])
        output = format_diff(result)
        assert "Previewing update" in output
