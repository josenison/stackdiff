"""Tests for the GraphML formatter."""
from __future__ import annotations

import xml.etree.ElementTree as ET

import pytest

from stackdiff.diff import ChangeType, DiffResult, ResourceDiff
from stackdiff.formatters.graphml_fmt import format_diff
from stackdiff.providers.base import Resource

_NS = "http://graphml.graphdrawing.org/graphml"


def _res(rid: str, rtype: str = "aws_instance") -> Resource:
    return Resource(resource_id=rid, resource_type=rtype, properties={})


def _rdiff(
    rid: str,
    change: ChangeType,
    rtype: str = "aws_instance",
) -> ResourceDiff:
    r = _res(rid, rtype)
    return ResourceDiff(
        resource_id=rid,
        resource_type=rtype,
        change_type=change,
        left=None if change == ChangeType.ADDED else r,
        right=None if change == ChangeType.REMOVED else r,
    )


def _make_result(*diffs: ResourceDiff) -> DiffResult:
    return DiffResult(diffs=list(diffs))


class TestGraphMLFormatter:
    def test_no_changes_returns_valid_xml(self):
        result = _make_result()
        output = format_diff(result)
        root = ET.fromstring(output)
        assert root.tag == f"{{{_NS}}}graphml" or "graphml" in root.tag

    def test_no_changes_graph_has_no_nodes(self):
        result = _make_result()
        output = format_diff(result)
        root = ET.fromstring(output)
        nodes = root.findall(".//{%s}node" % _NS) or root.findall(".//node")
        assert nodes == []

    def test_single_added_resource_produces_one_node(self):
        result = _make_result(_rdiff("i-1", ChangeType.ADDED))
        output = format_diff(result)
        root = ET.fromstring(output)
        nodes = root.findall(".//node") or root.findall(".//{%s}node" % _NS)
        assert len(nodes) == 1

    def test_node_contains_change_type_data(self):
        result = _make_result(_rdiff("i-1", ChangeType.ADDED))
        output = format_diff(result)
        assert ChangeType.ADDED.value in output

    def test_node_contains_resource_id(self):
        result = _make_result(_rdiff("i-abc", ChangeType.REMOVED))
        output = format_diff(result)
        assert "i-abc" in output

    def test_two_same_type_nodes_produce_edge(self):
        result = _make_result(
            _rdiff("i-1", ChangeType.ADDED, "aws_instance"),
            _rdiff("i-2", ChangeType.REMOVED, "aws_instance"),
        )
        output = format_diff(result)
        assert "edge" in output

    def test_two_different_type_nodes_produce_no_edge(self):
        result = _make_result(
            _rdiff("i-1", ChangeType.ADDED, "aws_instance"),
            _rdiff("b-1", ChangeType.ADDED, "aws_s3_bucket"),
        )
        output = format_diff(result)
        # edge element should not appear
        root = ET.fromstring(output)
        edges = root.findall(".//edge") or root.findall(".//{%s}edge" % _NS)
        assert edges == []

    def test_output_contains_graphml_declaration(self):
        result = _make_result()
        output = format_diff(result)
        assert "graphml" in output.lower()
