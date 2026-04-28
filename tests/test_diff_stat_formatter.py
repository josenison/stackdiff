"""Tests for the diff-stat formatter."""
from __future__ import annotations

import pytest

from stackdiff.diff import ChangeType, DiffResult, ResourceDiff
from stackdiff.providers.base import Resource
from stackdiff.formatters.diff_stat_fmt import format_diff


def _res(rid: str, rtype: str = "instance") -> Resource:
    return Resource(id=rid, type=rtype, properties={})


def _rdiff(
    rid: str,
    change_type: ChangeType,
    before: Resource | None = None,
    after: Resource | None = None,
) -> ResourceDiff:
    return ResourceDiff(
        resource_id=rid,
        change_type=change_type,
        before=before,
        after=after,
    )


def _make_result(*diffs: ResourceDiff) -> DiffResult:
    return DiffResult(diffs=list(diffs))


class TestDiffStatFormatter:
    def test_no_changes_returns_no_changes(self):
        result = _make_result(
            _rdiff("res-1", ChangeType.UNCHANGED, _res("res-1"), _res("res-1"))
        )
        out = format_diff(result)
        assert out == "(no changes)"

    def test_added_resource_shows_plus_symbol(self):
        r = _res("bucket-1")
        result = _make_result(_rdiff("bucket-1", ChangeType.ADDED, after=r))
        out = format_diff(result)
        assert "bucket-1" in out
        assert " | +" in out

    def test_removed_resource_shows_minus_symbol(self):
        r = _res("queue-1")
        result = _make_result(_rdiff("queue-1", ChangeType.REMOVED, before=r))
        out = format_diff(result)
        assert "queue-1" in out
        assert " | -" in out

    def test_modified_resource_shows_tilde_symbol(self):
        r = _res("fn-1")
        result = _make_result(_rdiff("fn-1", ChangeType.MODIFIED, before=r, after=r))
        out = format_diff(result)
        assert "fn-1" in out
        assert " | ~" in out

    def test_summary_line_counts_are_correct(self):
        result = _make_result(
            _rdiff("a", ChangeType.ADDED, after=_res("a")),
            _rdiff("b", ChangeType.ADDED, after=_res("b")),
            _rdiff("c", ChangeType.REMOVED, before=_res("c")),
            _rdiff("d", ChangeType.MODIFIED, before=_res("d"), after=_res("d")),
        )
        out = format_diff(result)
        assert "2 added" in out
        assert "1 modified" in out
        assert "1 removed" in out
        assert "4 resource(s) changed" in out

    def test_unchanged_resources_not_shown(self):
        result = _make_result(
            _rdiff("keep-me", ChangeType.UNCHANGED, _res("keep-me"), _res("keep-me")),
            _rdiff("new-one", ChangeType.ADDED, after=_res("new-one")),
        )
        out = format_diff(result)
        assert "keep-me" not in out
        assert "new-one" in out

    def test_resources_sorted_alphabetically(self):
        result = _make_result(
            _rdiff("z-res", ChangeType.ADDED, after=_res("z-res")),
            _rdiff("a-res", ChangeType.ADDED, after=_res("a-res")),
        )
        out = format_diff(result)
        lines = [l for l in out.splitlines() if " | " in l]
        names = [l.strip().split(" | ")[0].strip() for l in lines]
        assert names == sorted(names)
