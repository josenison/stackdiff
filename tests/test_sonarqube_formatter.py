"""Tests for the SonarQube formatter."""
import json
import pytest
from stackdiff.providers.base import Resource, StackState
from stackdiff.diff import DiffResult, ResourceDiff, ChangeType
from stackdiff.formatters.sonarqube_fmt import format_diff


def _res(rid: str, rtype: str = "aws_s3_bucket") -> Resource:
    return Resource(resource_id=rid, resource_type=rtype, attributes={})


def _rdiff(res, change_type, detail=None):
    return ResourceDiff(resource=res, change_type=change_type, diff_detail=detail)


def _make_result(*diffs):
    return DiffResult(diffs=list(diffs))


class TestSonarQubeFormatter:
    def test_no_changes_returns_empty_issues(self):
        r = _res("bucket-1")
        result = _make_result(_rdiff(r, ChangeType.UNCHANGED))
        out = json.loads(format_diff(result))
        assert out["issues"] == []

    def test_added_resource_is_code_smell(self):
        r = _res("bucket-new")
        result = _make_result(_rdiff(r, ChangeType.ADDED))
        out = json.loads(format_diff(result))
        assert len(out["issues"]) == 1
        issue = out["issues"][0]
        assert issue["type"] == "CODE_SMELL"
        assert issue["severity"] == "MINOR"
        assert "bucket-new" in issue["primaryLocation"]["message"]

    def test_removed_resource_is_bug(self):
        r = _res("bucket-old")
        result = _make_result(_rdiff(r, ChangeType.REMOVED))
        out = json.loads(format_diff(result))
        issue = out["issues"][0]
        assert issue["type"] == "BUG"
        assert issue["severity"] == "MAJOR"

    def test_modified_resource_includes_detail(self):
        r = _res("bucket-x")
        result = _make_result(_rdiff(r, ChangeType.MODIFIED, detail="tags changed"))
        out = json.loads(format_diff(result))
        msg = out["issues"][0]["primaryLocation"]["message"]
        assert "tags changed" in msg

    def test_custom_file_path_propagated(self):
        r = _res("bucket-y")
        result = _make_result(_rdiff(r, ChangeType.ADDED))
        out = json.loads(format_diff(result, file_path="infra/main.tf"))
        assert out["issues"][0]["primaryLocation"]["filePath"] == "infra/main.tf"

    def test_rule_id_matches_change_type(self):
        r = _res("res-1")
        result = _make_result(_rdiff(r, ChangeType.MODIFIED))
        out = json.loads(format_diff(result))
        assert out["issues"][0]["ruleId"] == "stackdiff:modified"

    def test_engine_id_is_stackdiff(self):
        r = _res("res-2")
        result = _make_result(_rdiff(r, ChangeType.ADDED))
        out = json.loads(format_diff(result))
        assert out["issues"][0]["engineId"] == "stackdiff"
