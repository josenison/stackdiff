"""Tests for the TeamCity service messages formatter."""
import pytest

from stackdiff.diff import ChangeType, DiffResult, ResourceDiff
from stackdiff.formatters.teamcity_fmt import format_diff
from stackdiff.providers.base import Resource


def _res(rid: str, rtype: str = "aws::s3::bucket") -> Resource:
    return Resource(resource_id=rid, resource_type=rtype, properties={})


def _rdiff(rid: str, change: ChangeType, rtype: str = "aws::s3::bucket") -> ResourceDiff:
    r = _res(rid, rtype)
    return ResourceDiff(resource_id=rid, resource_type=rtype, change_type=change,
                        left=None if change == ChangeType.ADDED else r,
                        right=None if change == ChangeType.REMOVED else r)


def _make_result(diffs: list[ResourceDiff]) -> DiffResult:
    return DiffResult(diffs=diffs)


class TestTeamCityFormatter:
    def test_no_changes_contains_suite_markers(self):
        out = format_diff(_make_result([]))
        assert "##teamcity[testSuiteStarted name='stackdiff']" in out
        assert "##teamcity[testSuiteFinished name='stackdiff']" in out

    def test_no_changes_single_passing_test(self):
        out = format_diff(_make_result([]))
        assert "testStarted name='infrastructure-drift'" in out
        assert "testFinished name='infrastructure-drift'" in out
        assert "testFailed" not in out

    def test_added_resource_appears_as_test(self):
        out = format_diff(_make_result([_rdiff("bucket-1", ChangeType.ADDED)]))
        assert "bucket-1" in out
        assert "ADDED" in out

    def test_removed_resource_appears_as_test(self):
        out = format_diff(_make_result([_rdiff("bucket-2", ChangeType.REMOVED)]))
        assert "bucket-2" in out
        assert "REMOVED" in out

    def test_modified_resource_produces_test_failed(self):
        out = format_diff(_make_result([_rdiff("bucket-3", ChangeType.MODIFIED)]))
        assert "testFailed" in out
        assert "bucket-3" in out

    def test_build_status_line_present_when_changes(self):
        out = format_diff(_make_result([_rdiff("x", ChangeType.ADDED)]))
        assert "##teamcity[buildStatus" in out

    def test_escape_pipe_in_resource_id(self):
        out = format_diff(_make_result([_rdiff("pipe|name", ChangeType.ADDED)]))
        assert "pipe||name" in out

    def test_output_is_string(self):
        out = format_diff(_make_result([]))
        assert isinstance(out, str)
