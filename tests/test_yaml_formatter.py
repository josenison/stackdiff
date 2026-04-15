"""Tests for the YAML formatter."""
from __future__ import annotations

import pytest

try:
    import yaml
    _YAML_AVAILABLE = True
except ImportError:
    _YAML_AVAILABLE = False

from stackdiff.diff import ChangeType, DiffResult, ResourceDiff
from stackdiff.providers.base import Resource

pytestmark = pytest.mark.skipif(
    not _YAML_AVAILABLE, reason="PyYAML not installed"
)


def _res(rid: str, rtype: str = "instance", **attrs) -> Resource:
    return Resource(resource_id=rid, resource_type=rtype, attributes=attrs)


def _rdiff(
    rid: str,
    rtype: str,
    change: ChangeType,
    attribute_changes: dict | None = None,
) -> ResourceDiff:
    return ResourceDiff(
        resource_id=rid,
        resource_type=rtype,
        change_type=change,
        attribute_changes=attribute_changes,
    )


def _make_result(*diffs: ResourceDiff) -> DiffResult:
    from stackdiff.diff import compute_diff
    result = DiffResult(diffs=list(diffs))
    summary: dict = {
        ChangeType.ADDED: 0,
        ChangeType.REMOVED: 0,
        ChangeType.MODIFIED: 0,
        ChangeType.UNCHANGED: 0,
    }
    for d in diffs:
        summary[d.change_type] += 1
    result.summary = summary
    return result


class TestYAMLFormatter:
    def _fmt(self, result):
        from stackdiff.formatters.yaml_fmt import format_diff
        return format_diff(result)

    def _parse(self, text: str) -> dict:
        return yaml.safe_load(text)

    def test_no_changes_produces_valid_yaml(self):
        result = _make_result()
        parsed = self._parse(self._fmt(result))
        assert parsed["changes"] == []
        assert parsed["summary"]["added"] == 0

    def test_added_resource_appears_in_output(self):
        rd = _rdiff("i-123", "instance", ChangeType.ADDED)
        result = _make_result(rd)
        parsed = self._parse(self._fmt(result))
        assert len(parsed["changes"]) == 1
        assert parsed["changes"][0]["change"] == "added"
        assert parsed["changes"][0]["resource_id"] == "i-123"

    def test_removed_resource_appears_in_output(self):
        rd = _rdiff("i-456", "instance", ChangeType.REMOVED)
        result = _make_result(rd)
        parsed = self._parse(self._fmt(result))
        assert parsed["changes"][0]["change"] == "removed"
        assert parsed["summary"]["removed"] == 1

    def test_modified_resource_includes_attribute_changes(self):
        rd = _rdiff(
            "i-789",
            "instance",
            ChangeType.MODIFIED,
            attribute_changes={"size": ("t2.micro", "t3.small")},
        )
        result = _make_result(rd)
        parsed = self._parse(self._fmt(result))
        change = parsed["changes"][0]
        assert change["change"] == "modified"
        assert len(change["attribute_changes"]) == 1
        attr = change["attribute_changes"][0]
        assert attr["attribute"] == "size"
        assert attr["old"] == "t2.micro"
        assert attr["new"] == "t3.small"

    def test_summary_counts_are_correct(self):
        diffs = [
            _rdiff("a", "bucket", ChangeType.ADDED),
            _rdiff("b", "bucket", ChangeType.REMOVED),
            _rdiff("c", "bucket", ChangeType.MODIFIED, {"acl": ("private", "public")}),
            _rdiff("d", "bucket", ChangeType.UNCHANGED),
        ]
        result = _make_result(*diffs)
        parsed = self._parse(self._fmt(result))
        assert parsed["summary"]["added"] == 1
        assert parsed["summary"]["removed"] == 1
        assert parsed["summary"]["modified"] == 1
        assert parsed["summary"]["unchanged"] == 1
