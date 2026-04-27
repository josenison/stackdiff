"""GraphML formatter – renders a diff as a GraphML XML graph.

Nodes represent resources; edges connect resources that share the same
resource type.  Each node carries ``change`` and ``resource_type``
attributes so downstream tools (e.g. yEd) can colour-code the graph.
"""
from __future__ import annotations

import xml.etree.ElementTree as ET
from xml.dom import minidom

from stackdiff.diff import DiffResult

_NS = "http://graphml.graphdrawing.org/graphml"


def _prettify(element: ET.Element) -> str:
    raw = ET.tostring(element, encoding="unicode")
    return minidom.parseString(raw).toprettyxml(indent="  ")


def format_diff(result: DiffResult) -> str:
    """Return a GraphML document string representing *result*."""
    root = ET.Element("graphml", xmlns=_NS)

    # Key declarations
    for attr_id, attr_name, domain in (
        ("d0", "change", "node"),
        ("d1", "resource_type", "node"),
        ("d2", "resource_id", "node"),
    ):
        key = ET.SubElement(root, "key")
        key.set("id", attr_id)
        key.set("for", domain)
        key.set("attr.name", attr_name)
        key.set("attr.type", "string")

    graph = ET.SubElement(root, "graph", id="G", edgedefault="undirected")

    seen_types: dict[str, list[str]] = {}

    for idx, diff in enumerate(result.diffs):
        node_id = f"n{idx}"
        node = ET.SubElement(graph, "node", id=node_id)

        for key_id, value in (
            ("d0", diff.change_type.value),
            ("d1", diff.resource_type),
            ("d2", diff.resource_id),
        ):
            data = ET.SubElement(node, "data", key=key_id)
            data.text = value

        seen_types.setdefault(diff.resource_type, []).append(node_id)

    # Add edges between nodes that share a resource type
    edge_idx = 0
    for siblings in seen_types.values():
        for i in range(len(siblings)):
            for j in range(i + 1, len(siblings)):
                ET.SubElement(
                    graph,
                    "edge",
                    id=f"e{edge_idx}",
                    source=siblings[i],
                    target=siblings[j],
                )
                edge_idx += 1

    return _prettify(root)
