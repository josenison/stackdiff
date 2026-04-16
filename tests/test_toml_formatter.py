"""Tests for the TOML formatter."""
from __future__ import annotations

import sys
import pytest

from stackdiff.diff import DiffResult, ResourceDiff, ChangeType
from stackdiff.providers.base import Resource


def _res(rid: str, rtype: str = "instance", **props) -> Resource:
    return Resource(id=rid, type=rtype, properties=props)


def _rdiff(change_type: ChangeType, before=None, after=None) -> ResourceDiff:
    rid = (after or before).id
    return ResourceDiff(resource_id=rid, change_type=change_type, before=before, after=after)


def _make_result(*diffs: ResourceDiff) -> DiffResult:
    return DiffResult(changes=list(diffs))


tomli_w = pytest.importorskip("tomli_w", reason="tomli_w not installed")

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore

from stackdiff.formatters.toml_fmt import format_diff, _diff_to_dict


class TestTOMLFormatter:
    def test_no_changes_has_changes_false(self):
        result = _make_result()
        output = format_diff(result)
        data = tomllib.loads(output)
        assert data["has_changes"] is False
        assert data["changes"] == []

    def test_added_resource(self):
        r = _res("i-123", "ec2", region="us-east-1")
        result = _make_result(_rdiff(ChangeType.ADDED, after=r))
        data = tomllib.loads(format_diff(result))
        assert data["has_changes"] is True
        assert len(data["changes"]) == 1
        ch = data["changes"][0]
        assert ch["change_type"] == "added"
        assert ch["resource_id"] == "i-123"
        assert "before" not in ch
        assert ch["after"]["id"] == "i-123"

    def test_removed_resource(self):
        r = _res("i-456", "ec2")
        result = _make_result(_rdiff(ChangeType.REMOVED, before=r))
        data = tomllib.loads(format_diff(result))
        ch = data["changes"][0]
        assert ch["change_type"] == "removed"
        assert "after" not in ch
        assert ch["before"]["id"] == "i-456"

    def test_modified_resource(self):
        before = _res("i-789", "ec2", size="t2.micro")
        after = _res("i-789", "ec2", size="t3.small")
        result = _make_result(_rdiff(ChangeType.MODIFIED, before=before, after=after))
        data = tomllib.loads(format_diff(result))
        ch = data["changes"][0]
        assert ch["change_type"] == "modified"
        assert ch["before"]["properties"]["size"] == "t2.micro"
        assert ch["after"]["properties"]["size"] == "t3.small"

    def test_summary_included(self):
        r = _res("r-1", "bucket")
        result = _make_result(_rdiff(ChangeType.ADDED, after=r))
        data = tomllib.loads(format_diff(result))
        assert "summary" in data
        assert isinstance(data["summary"], str)
