"""Tests for the CloudFormation change-set formatter."""
from __future__ import annotations

import pytest

from stackdiff.diff import ChangeType, DiffResult, ResourceDiff
from stackdiff.providers.base import Resource
from stackdiff.formatters.cloudformation_fmt import format_diff
from stackdiff.formatters.registry import get_formatter, available_formatters


def _res(rid: str, rtype: str = "AWS::S3::Bucket") -> Resource:
    return Resource(resource_id=rid, resource_type=rtype, properties={"Name": rid})


def _rdiff(
    rid: str,
    change_type: ChangeType,
    rtype: str = "AWS::S3::Bucket",
) -> ResourceDiff:
    src = _res(rid, rtype) if change_type != ChangeType.ADDED else None
    tgt = _res(rid, rtype) if change_type != ChangeType.REMOVED else None
    return ResourceDiff(
        resource_id=rid,
        change_type=change_type,
        source=src,
        target=tgt,
    )


def _make_result(*diffs: ResourceDiff) -> DiffResult:
    return DiffResult(changes=list(diffs))


class TestCloudFormationFormatter:
    def test_no_changes_returns_no_changes_message(self):
        result = _make_result()
        out = format_diff(result)
        assert "No changes detected" in out

    def test_header_always_present(self):
        result = _make_result()
        out = format_diff(result)
        assert "CloudFormation Change Set" in out

    def test_added_resource_shows_add_action(self):
        result = _make_result(_rdiff("MyBucket", ChangeType.ADDED))
        out = format_diff(result)
        assert "Action            : Add" in out
        assert "MyBucket" in out

    def test_removed_resource_shows_remove_action(self):
        result = _make_result(_rdiff("OldQueue", ChangeType.REMOVED, "AWS::SQS::Queue"))
        out = format_diff(result)
        assert "Action            : Remove" in out
        assert "OldQueue" in out

    def test_modified_resource_shows_modify_action(self):
        result = _make_result(_rdiff("MyTable", ChangeType.MODIFIED, "AWS::DynamoDB::Table"))
        out = format_diff(result)
        assert "Action            : Modify" in out
        assert "Replacement       : Conditional" in out

    def test_unchanged_resource_not_shown(self):
        result = _make_result(
            _rdiff("StableResource", ChangeType.UNCHANGED),
            _rdiff("NewResource", ChangeType.ADDED),
        )
        out = format_diff(result)
        assert "StableResource" not in out
        assert "NewResource" in out

    def test_summary_line_present(self):
        result = _make_result(
            _rdiff("A", ChangeType.ADDED),
            _rdiff("B", ChangeType.REMOVED),
            _rdiff("C", ChangeType.MODIFIED),
        )
        out = format_diff(result)
        assert "+1 added" in out
        assert "~1 modified" in out
        assert "-1 removed" in out

    def test_resource_type_shown(self):
        result = _make_result(_rdiff("MyFunc", ChangeType.ADDED, "AWS::Lambda::Function"))
        out = format_diff(result)
        assert "AWS::Lambda::Function" in out

    def test_registered_in_formatter_registry(self):
        assert "cloudformation" in available_formatters()

    def test_get_formatter_returns_callable(self):
        fn = get_formatter("cloudformation")
        assert callable(fn)

    def test_formatter_via_registry_produces_output(self):
        fn = get_formatter("cloudformation")
        result = _make_result(_rdiff("Res", ChangeType.ADDED))
        out = fn(result)
        assert isinstance(out, str)
        assert "Add" in out
