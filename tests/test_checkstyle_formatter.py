"""Tests for the Checkstyle XML formatter."""
from __future__ import annotations

import xml.etree.ElementTree as ET

import pytest

from stackdiff.diff import ChangeType, DiffResult, ResourceDiff
from stackdiff.formatters.checkstyle_fmt import format_diff
from stackdiff.providers.base import Resource


def _res(rid: str, rtype: str = "aws::s3::bucket") -> Resource:
    return Resource(id=rid, type=rtype, properties={})


def _rdiff(
    rid: str,
    change: ChangeType,
    rtype: str = "aws::s3::bucket",
) -> ResourceDiff:
    r = _res(rid, rtype)
    return ResourceDiff(
        resource_id=rid,
        resource_type=rtype,
        change_type=change,
        before=None if change == ChangeType.ADDED else r,
        after=None if change == ChangeType.REMOVED else r,
    )


def _make_result(*diffs: ResourceDiff) -> DiffResult:
    return DiffResult(diffs=list(diffs))


class TestCheckstyleFormatter:
    def test_no_changes_returns_valid_xml(self):
        result = _make_result()
        output = format_diff(result)
        root = ET.fromstring(output)
        assert root.tag == "checkstyle"

    def test_no_changes_has_empty_file_element(self):
        result = _make_result()
        output = format_diff(result)
        root = ET.fromstring(output)
        files = root.findall("file")
        assert len(files) == 1
        assert files[0].get("name") == "stackdiff"

    def test_added_resource_produces_warning(self):
        result = _make_result(_rdiff("bucket-1", ChangeType.ADDED))
        root = ET.fromstring(format_diff(result))
        errors = root.findall(".//error")
        assert len(errors) == 1
        assert errors[0].get("severity") == "warning"
        assert "bucket-1" in errors[0].get("message", "")

    def test_removed_resource_produces_error_severity(self):
        result = _make_result(_rdiff("bucket-2", ChangeType.REMOVED))
        root = ET.fromstring(format_diff(result))
        errors = root.findall(".//error")
        assert errors[0].get("severity") == "error"

    def test_modified_resource_produces_warning(self):
        result = _make_result(_rdiff("bucket-3", ChangeType.MODIFIED))
        root = ET.fromstring(format_diff(result))
        errors = root.findall(".//error")
        assert errors[0].get("severity") == "warning"

    def test_unchanged_resources_omitted(self):
        result = _make_result(_rdiff("bucket-4", ChangeType.UNCHANGED))
        root = ET.fromstring(format_diff(result))
        errors = root.findall(".//error")
        assert len(errors) == 0

    def test_resources_grouped_by_type(self):
        result = _make_result(
            _rdiff("b1", ChangeType.ADDED, "aws::s3::bucket"),
            _rdiff("b2", ChangeType.REMOVED, "aws::s3::bucket"),
            _rdiff("fn1", ChangeType.MODIFIED, "aws::lambda::function"),
        )
        root = ET.fromstring(format_diff(result))
        files = root.findall("file")
        names = {f.get("name") for f in files}
        assert "aws::s3::bucket" in names
        assert "aws::lambda::function" in names

    def test_checkstyle_version_attribute(self):
        result = _make_result()
        root = ET.fromstring(format_diff(result))
        assert root.get("version") == "8.0"

    def test_source_attribute_is_stackdiff(self):
        result = _make_result(_rdiff("r1", ChangeType.ADDED))
        root = ET.fromstring(format_diff(result))
        for error in root.findall(".//error"):
            assert error.get("source") == "stackdiff"
