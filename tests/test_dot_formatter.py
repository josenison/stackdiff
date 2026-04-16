import pytest
from stackdiff.formatters.dot_fmt import format_diff
from stackdiff.diff import DiffResult, ResourceDiff, ChangeType
from stackdiff.providers.base import Resource


def _res(rid, rtype="aws::s3::bucket"):
    return Resource(resource_id=rid, resource_type=rtype, attributes={})


def _rdiff(rid, change_type, rtype="aws::s3::bucket", attr_changes=None):
    before = None if change_type == ChangeType.ADDED else _res(rid, rtype)
    after = None if change_type == ChangeType.REMOVED else _res(rid, rtype)
    return ResourceDiff(
        resource_id=rid,
        resource_type=rtype,
        change_type=change_type,
        before=before,
        after=after,
        attribute_changes=attr_changes or {},
    )


def _make_result(diffs):
    return DiffResult(diffs=diffs)


class TestDOTFormatter:
    def test_no_changes_returns_simple_graph(self):
        result = _make_result([])
        out = format_diff(result)
        assert "digraph" in out
        assert "No changes detected" in out

    def test_added_resource_green(self):
        result = _make_result([_rdiff("bucket-1", ChangeType.ADDED)])
        out = format_diff(result)
        assert "green" in out
        assert "bucket-1" in out

    def test_removed_resource_red(self):
        result = _make_result([_rdiff("bucket-2", ChangeType.REMOVED)])
        out = format_diff(result)
        assert "red" in out

    def test_modified_resource_shows_attrs(self):
        rd = _rdiff("bucket-3", ChangeType.MODIFIED, attr_changes={"versioning": ("off", "on")})
        result = _make_result([rd])
        out = format_diff(result)
        assert "orange" in out
        assert "versioning" in out

    def test_custom_graph_name(self):
        result = _make_result([])
        out = format_diff(result, graph_name="mygraph")
        assert "digraph mygraph" in out

    def test_output_starts_with_digraph(self):
        result = _make_result([_rdiff("r1", ChangeType.ADDED)])
        out = format_diff(result)
        assert out.startswith("digraph")

    def test_output_ends_with_closing_brace(self):
        result = _make_result([_rdiff("r1", ChangeType.ADDED)])
        out = format_diff(result)
        assert out.strip().endswith("}")
