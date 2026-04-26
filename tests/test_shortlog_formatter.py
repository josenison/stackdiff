"""Tests for stackdiff.formatters.shortlog_fmt."""
from __future__ import annotations

import pytest

from stackdiff.diff import ChangeType, DiffResult, ResourceDiff
from stackdiff.formatters.shortlog_fmt import format_diff
from stackdiff.providers.base import Resource


def _res(rid: str, rtype: str = "aws::S3Bucket") -> Resource:
    return Resource(resource_id=rid, resource_type=rtype, properties={})


def _rdiff(
    rid: str,
    change: ChangeType,
    rtype: str = "aws::S3Bucket",
) -> ResourceDiff:
    r = _res(rid, rtype)
    return ResourceDiff(
        resource_id=rid,
        resource_type=rtype,
        change_type=change,
        before=None if change is ChangeType.ADDED else r,
        after=None if change is ChangeType.REMOVED else r,
    )


def _make_result(diffs: list[ResourceDiff]) -> DiffResult:
    return DiffResult(diffs=diffs)


class TestShortlogFormatter:
    def test_no_changes_returns_single_line(self) -> None:
        result = _make_result(
            [_rdiff("bucket-a", ChangeType.UNCHANGED)]
        )
        out = format_diff(result)
        assert "\n" not in out
        assert "No changes" in out
        assert "1 resource" in out

    def test_added_resource_shown_with_plus(self) -> None:
        result = _make_result([_rdiff("new-bucket", ChangeType.ADDED)])
        out = format_diff(result)
        assert "[+]" in out
        assert "new-bucket" in out

    def test_removed_resource_shown_with_minus(self) -> None:
        result = _make_result([_rdiff("old-bucket", ChangeType.REMOVED)])
        out = format_diff(result)
        assert "[-]" in out
        assert "old-bucket" in out

    def test_modified_resource_shown_with_tilde(self) -> None:
        result = _make_result([_rdiff("changed-bucket", ChangeType.MODIFIED)])
        out = format_diff(result)
        assert "[~]" in out
        assert "changed-bucket" in out

    def test_unchanged_resources_omitted_from_body(self) -> None:
        result = _make_result(
            [
                _rdiff("keep-me", ChangeType.UNCHANGED),
                _rdiff("new-one", ChangeType.ADDED),
            ]
        )
        out = format_diff(result)
        assert "keep-me" not in out
        assert "new-one" in out

    def test_summary_line_appended(self) -> None:
        result = _make_result(
            [
                _rdiff("a", ChangeType.ADDED),
                _rdiff("b", ChangeType.REMOVED),
                _rdiff("c", ChangeType.MODIFIED),
            ]
        )
        out = format_diff(result)
        assert "Summary:" in out
        assert "+1 added" in out
        assert "-1 removed" in out
        assert "~1 modified" in out

    def test_multiple_resources_sorted_by_type_then_id(self) -> None:
        result = _make_result(
            [
                _rdiff("z-bucket", ChangeType.ADDED, "aws::S3Bucket"),
                _rdiff("a-bucket", ChangeType.ADDED, "aws::S3Bucket"),
            ]
        )
        out = format_diff(result)
        lines = [ln for ln in out.splitlines() if "[+]" in ln]
        assert lines[0].strip().endswith("a-bucket")
        assert lines[1].strip().endswith("z-bucket")

    def test_resource_type_included_in_output(self) -> None:
        result = _make_result(
            [_rdiff("my-disk", ChangeType.ADDED, "gcp::Disk")]
        )
        out = format_diff(result)
        assert "gcp::Disk" in out
