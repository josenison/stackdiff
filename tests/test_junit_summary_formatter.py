import xml.etree.ElementTree as ET
import pytest

from stackdiff.providers.base import Resource, StackState
from stackdiff.diff import DiffResult, ResourceDiff, ChangeType
from stackdiff.formatters.junit_summary_fmt import format_diff


def _res(rid, rtype="AWS::S3::Bucket", props=None):
    return Resource(resource_id=rid, resource_type=rtype, properties=props or {})


def _rdiff(rid, change_type, old=None, new=None):
    return ResourceDiff(resource_id=rid, change_type=change_type, old_resource=old, new_resource=new)


def _make_result(*diffs):
    return DiffResult(diffs=list(diffs))


class TestJUnitSummaryFormatter:
    def test_no_changes_returns_valid_xml(self):
        result = _make_result()
        out = format_diff(result)
        root = ET.fromstring(out)
        assert root.tag == "testsuite"
        assert root.attrib["tests"] == "0"
        assert root.attrib["failures"] == "0"

    def test_no_changes_has_no_change_testcase(self):
        result = _make_result()
        out = format_diff(result)
        root = ET.fromstring(out)
        cases = root.findall("testcase")
        assert any(tc.attrib["name"] == "no_changes" for tc in cases)

    def test_added_resource_is_failure(self):
        r = _res("bucket-1")
        diff = _rdiff("bucket-1", ChangeType.ADDED, new=r)
        out = format_diff(_make_result(diff))
        root = ET.fromstring(out)
        tc = root.find("testcase[@name='bucket-1']")
        assert tc is not None
        assert tc.find("failure") is not None

    def test_unchanged_resource_has_no_failure(self):
        r = _res("bucket-2")
        diff = _rdiff("bucket-2", ChangeType.UNCHANGED, old=r, new=r)
        out = format_diff(_make_result(diff))
        root = ET.fromstring(out)
        tc = root.find("testcase[@name='bucket-2']")
        assert tc is not None
        assert tc.find("failure") is None

    def test_failures_count_matches(self):
        r = _res("x")
        diffs = [
            _rdiff("x", ChangeType.ADDED, new=r),
            _rdiff("y", ChangeType.REMOVED, old=r),
            _rdiff("z", ChangeType.UNCHANGED, old=r, new=r),
        ]
        out = format_diff(_make_result(*diffs))
        root = ET.fromstring(out)
        assert root.attrib["failures"] == "2"
        assert root.attrib["tests"] == "3"

    def test_failure_message_contains_change_type(self):
        r = _res("bucket-3")
        diff = _rdiff("bucket-3", ChangeType.REMOVED, old=r)
        out = format_diff(_make_result(diff))
        root = ET.fromstring(out)
        tc = root.find("testcase[@name='bucket-3']")
        failure = tc.find("failure")
        assert "removed" in failure.attrib["message"]
