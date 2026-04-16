"""Tests for the JUnit XML formatter."""
import xml.etree.ElementTree as ET
import pytest
from stackdiff.providers.base import Resource, StackState
from stackdiff.diff import DiffResult, ResourceDiff, ChangeType
from stackdiff.formatters.junit_fmt import format_diff


def _res(rid: str, rtype: str = "Instance", **attrs) -> Resource:
    return Resource(id=rid, type=rtype, attributes=attrs)


def _rdiff(change: ChangeType, rid="r1", rtype="VM", src=None, tgt=None) -> ResourceDiff:
    return ResourceDiff(resource_id=rid, resource_type=rtype, change_type=change,
                        source=src, target=tgt)


def _make_result(*diffs) -> DiffResult:
    return DiffResult(diffs=list(diffs))


class TestJUnitFormatter:
    def test_no_changes_returns_valid_xml(self):
        out = format_diff(_make_result())
        root = ET.fromstring(out)
        assert root.tag == "testsuite"
        assert root.attrib["tests"] == "0"
        assert root.attrib["failures"] == "0"

    def test_unchanged_resource_has_no_failure(self):
        r = _res("i-1")
        d = _rdiff(ChangeType.UNCHANGED, rid="i-1", src=r, tgt=r)
        out = format_diff(_make_result(d))
        root = ET.fromstring(out)
        assert root.attrib["failures"] == "0"
        tc = root.find("testcase")
        assert tc is not None
        assert tc.find("failure") is None

    def test_added_resource_produces_failure(self):
        r = _res("i-2")
        d = _rdiff(ChangeType.ADDED, rid="i-2", tgt=r)
        out = format_diff(_make_result(d))
        root = ET.fromstring(out)
        assert root.attrib["failures"] == "1"
        failure = root.find(".//failure")
        assert failure is not None
        assert "ADDED" in failure.attrib["message"]

    def test_removed_resource_produces_failure(self):
        r = _res("i-3")
        d = _rdiff(ChangeType.REMOVED, rid="i-3", src=r)
        out = format_diff(_make_result(d))
        root = ET.fromstring(out)
        assert root.attrib["failures"] == "1"

    def test_modified_resource_failure_contains_attributes(self):
        src = _res("i-4", size="small")
        tgt = _res("i-4", size="large")
        d = _rdiff(ChangeType.MODIFIED, rid="i-4", src=src, tgt=tgt)
        out = format_diff(_make_result(d))
        root = ET.fromstring(out)
        failure = root.find(".//failure")
        assert "small" in failure.text
        assert "large" in failure.text

    def test_testcase_classname_is_resource_type(self):
        r = _res("i-5", rtype="Bucket")
        d = _rdiff(ChangeType.ADDED, rid="i-5", rtype="Bucket", tgt=r)
        out = format_diff(_make_result(d))
        root = ET.fromstring(out)
        tc = root.find("testcase")
        assert tc.attrib["classname"] == "Bucket"
