import json
import pytest

from stackdiff.diff import ChangeType, DiffResult, ResourceDiff
from stackdiff.providers.base import Resource
from stackdiff.formatters.scorecard_fmt import format_diff, _score, _grade


def _res(rid: str, rtype: str = "instance") -> Resource:
    return Resource(id=rid, type=rtype, name=rid, attributes={})


def _rdiff(change_type: ChangeType, rid: str = "r1") -> ResourceDiff:
    res = _res(rid)
    if change_type == ChangeType.ADDED:
        return ResourceDiff(change_type=change_type, resource_after=res)
    if change_type == ChangeType.REMOVED:
        return ResourceDiff(change_type=change_type, resource_before=res)
    return ResourceDiff(
        change_type=change_type, resource_before=res, resource_after=res
    )


def _make_result(*diffs: ResourceDiff) -> DiffResult:
    return DiffResult(diffs=list(diffs))


class TestScorecardFormatter:
    def test_no_changes_score_100(self):
        result = _make_result()
        data = json.loads(format_diff(result))
        assert data["score"] == 100

    def test_no_changes_grade_a_plus(self):
        result = _make_result()
        data = json.loads(format_diff(result))
        assert data["grade"] == "A+"

    def test_no_changes_has_changes_false(self):
        result = _make_result()
        data = json.loads(format_diff(result))
        assert data["has_changes"] is False

    def test_added_resource_reduces_score(self):
        result = _make_result(_rdiff(ChangeType.ADDED))
        data = json.loads(format_diff(result))
        assert data["score"] == 95

    def test_removed_resource_reduces_score_more(self):
        result = _make_result(_rdiff(ChangeType.REMOVED))
        data = json.loads(format_diff(result))
        assert data["score"] == 90

    def test_modified_resource_reduces_score(self):
        result = _make_result(_rdiff(ChangeType.MODIFIED))
        data = json.loads(format_diff(result))
        assert data["score"] == 97

    def test_score_never_below_zero(self):
        diffs = [_rdiff(ChangeType.REMOVED, f"r{i}") for i in range(20)]
        result = _make_result(*diffs)
        assert _score(result) == 0

    def test_change_counts_populated(self):
        result = _make_result(
            _rdiff(ChangeType.ADDED, "a1"),
            _rdiff(ChangeType.REMOVED, "r1"),
            _rdiff(ChangeType.MODIFIED, "m1"),
        )
        data = json.loads(format_diff(result))
        assert data["changes"]["added"] == 1
        assert data["changes"]["removed"] == 1
        assert data["changes"]["modified"] == 1

    def test_grade_f_for_zero_score(self):
        assert _grade(0) == "F"

    def test_grade_boundaries(self):
        assert _grade(100) == "A+"
        assert _grade(95) == "A"
        assert _grade(80) == "B"
        assert _grade(65) == "C"
        assert _grade(45) == "D"
        assert _grade(30) == "F"

    def test_summary_present(self):
        result = _make_result()
        data = json.loads(format_diff(result))
        assert "summary" in data
