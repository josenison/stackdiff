"""Tests for the XML formatter."""
import xml.etree.ElementTree as ET
import pytest

from stackdiff.diff import DiffResult, ResourceDiff, ChangeType
from stackdiff.providers.base import Resource, StackState
from stackdiff.formatters.xml_fmt import format_diff


def _res(rid, rtype, **attrs):
    return Resource(resource_id=rid, resource_type=rtype, attributes=attrs)


def _rdiff(change_type, source=None, target=None, attribute_diffs=None):
    return ResourceDiff(
        change_type=change_type,
        source=source,
        target=target,
        attribute_diffs=attribute_diffs or {},
    )


def _make_result(diffs):
    return DiffResult(source_name="prod", target_name="staging", diffs=diffs)


class TestXMLFormatter:
    def test_no_changes_returns_valid_xml(self):
        result = _make_result([])
        output = format_diff(result)
        root = ET.fromstring(output)
        assert root.tag == "diff"
        assert root.get("has_changes") == "false"

    def test_source_and_target_names_in_attributes(self):
        result = _make_result([])
        output = format_diff(result)
        root = ET.fromstring(output)
        assert root.get("source") == "prod"
        assert root.get("target") == "staging"

    def test_added_resource_appears_in_xml(self):
        r = _res("i-123", "instance", size="t2.micro")
        result = _make_result([_rdiff(ChangeType.ADDED, target=r)])
        output = format_diff(result)
        root = ET.fromstring(output)
        changes = root.find("changes")
        assert changes is not None
        change = changes.find("change")
        assert change.get("type") == "added"
        assert change.get("resource_id") == "i-123"

    def test_removed_resource_change_type(self):
        r = _res("i-456", "instance", size="t3.large")
        result = _make_result([_rdiff(ChangeType.REMOVED, source=r)])
        output = format_diff(result)
        root = ET.fromstring(output)
        change = root.find("changes/change")
        assert change.get("type") == "removed"

    def test_modified_resource_includes_attribute_diffs(self):
        src = _res("i-789", "instance", size="t2.micro")
        tgt = _res("i-789", "instance", size="t3.large")
        rd = _rdiff(ChangeType.MODIFIED, source=src, target=tgt,
                    attribute_diffs={"size": ("t2.micro", "t3.large")})
        result = _make_result([rd])
        output = format_diff(result)
        root = ET.fromstring(output)
        attr_diffs = root.find("changes/change/attribute_diffs")
        assert attr_diffs is not None
        attr = attr_diffs.find("attribute")
        assert attr.get("name") == "size"
        assert attr.find("old").text == "t2.micro"
        assert attr.find("new").text == "t3.large"

    def test_summary_counts(self):
        r1 = _res("a", "bucket")
        r2 = _res("b", "bucket")
        result = _make_result([
            _rdiff(ChangeType.ADDED, target=r1),
            _rdiff(ChangeType.REMOVED, source=r2),
        ])
        output = format_diff(result)
        root = ET.fromstring(output)
        summary = root.find("summary")
        assert summary.get("added") == "1"
        assert summary.get("removed") == "1"
