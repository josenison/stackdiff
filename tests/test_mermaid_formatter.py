"""Tests for the Mermaid diagram formatter."""
from __future__ import annotations

import pytest

from stackdiff.diff import ChangeType, DiffResult, ResourceDiff
from stackdiff.formatters.mermaid_fmt import format_diff
from stackdiff.providers.base import Resource


def _res(rtype: str, rid: str) -> Resource:
    return Resource(resource_type=rtype, resource_id=rid, attributes={})


def _rdiff(
    rtype: str,
    rid: str,
    change: ChangeType,
    before: Resource | None = None,
    after: Resource | None = None,
) -> ResourceDiff:
    return ResourceDiff(
        resource_type=rtype,
        resource_id=rid,
        change_type=change,
        before=before,
        after=after,
    )


def _make_result(*diffs: ResourceDiff) -> DiffResult:
    return DiffResult(diffs=list(diffs))


class TestMermaidFormatter:
    def test_no_changes_returns_simple_graph(self):
        result = _make_result()
        output = format_diff(result)
        assert "graph LR" in output
        assert "No changes detected" in output

    def test_added_resource_shown(self):
        r = _res("aws_s3_bucket", "my-bucket")
        result = _make_result(_rdiff("aws_s3_bucket", "my-bucket", ChangeType.ADDED, after=r))
        output = format_diff(result)
        assert "graph LR" in output
        assert "+ aws_s3_bucket/my-bucket" in output

    def test_removed_resource_shown(self):
        r = _res("aws_lambda_function", "fn-old")
        result = _make_result(_rdiff("aws_lambda_function", "fn-old", ChangeType.REMOVED, before=r))
        output = format_diff(result)
        assert "- aws_lambda_function/fn-old" in output

    def test_modified_resource_shown(self):
        r = _res("aws_iam_role", "my-role")
        result = _make_result(_rdiff("aws_iam_role", "my-role", ChangeType.MODIFIED, before=r, after=r))
        output = format_diff(result)
        assert "~ aws_iam_role/my-role" in output

    def test_unchanged_resources_excluded(self):
        r = _res("aws_vpc", "vpc-123")
        result = _make_result(_rdiff("aws_vpc", "vpc-123", ChangeType.UNCHANGED, before=r, after=r))
        output = format_diff(result)
        assert "No changes detected" in output

    def test_style_lines_present_for_changes(self):
        r = _res("aws_s3_bucket", "bucket-1")
        result = _make_result(_rdiff("aws_s3_bucket", "bucket-1", ChangeType.ADDED, after=r))
        output = format_diff(result)
        assert "style node0" in output
        assert "fill:#2da44e" in output

    def test_multiple_changes_all_present(self):
        r1 = _res("aws_s3_bucket", "b1")
        r2 = _res("aws_ec2_instance", "i-001")
        result = _make_result(
            _rdiff("aws_s3_bucket", "b1", ChangeType.ADDED, after=r1),
            _rdiff("aws_ec2_instance", "i-001", ChangeType.REMOVED, before=r2),
        )
        output = format_diff(result)
        assert "node0" in output
        assert "node1" in output
        assert "+ aws_s3_bucket/b1" in output
        assert "- aws_ec2_instance/i-001" in output
