"""Checkstyle XML formatter for stackdiff.

Produces output compatible with the Checkstyle XML schema, suitable
for consumption by CI tools such as Jenkins and GitHub Actions.
"""
from __future__ import annotations

import xml.etree.ElementTree as ET
from xml.dom import minidom

from stackdiff.diff import ChangeType, DiffResult


def _prettify(element: ET.Element) -> str:
    raw = ET.tostring(element, encoding="unicode")
    reparsed = minidom.parseString(raw)
    return reparsed.toprettyxml(indent="  ")


_SEVERITY: dict[ChangeType, str] = {
    ChangeType.ADDED: "warning",
    ChangeType.REMOVED: "error",
    ChangeType.MODIFIED: "warning",
    ChangeType.UNCHANGED: "info",
}

_MESSAGE: dict[ChangeType, str] = {
    ChangeType.ADDED: "Resource added",
    ChangeType.REMOVED: "Resource removed",
    ChangeType.MODIFIED: "Resource modified",
    ChangeType.UNCHANGED: "Resource unchanged",
}


def format_diff(result: DiffResult) -> str:
    """Return a Checkstyle-compatible XML string for *result*."""
    checkstyle = ET.Element("checkstyle", version="8.0")

    # Group diffs by resource type so each type becomes a <file> element.
    by_type: dict[str, list] = {}
    for diff in result.diffs:
        by_type.setdefault(diff.resource_type, []).append(diff)

    if not by_type:
        # Emit a single empty file element when there are no changes.
        ET.SubElement(checkstyle, "file", name="stackdiff")
        return _prettify(checkstyle)

    for resource_type, diffs in sorted(by_type.items()):
        file_el = ET.SubElement(checkstyle, "file", name=resource_type)
        for diff in diffs:
            if diff.change_type == ChangeType.UNCHANGED:
                continue
            ET.SubElement(
                file_el,
                "error",
                line="0",
                column="0",
                severity=_SEVERITY[diff.change_type],
                message=f"{_MESSAGE[diff.change_type]}: {diff.resource_id}",
                source="stackdiff",
            )

    return _prettify(checkstyle)
