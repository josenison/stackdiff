"""JUnit summary formatter — emits a single test-suite XML where each
change type (added / removed / modified / unchanged) is represented as
one test-case, making it easy to gate CI pipelines on drift.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from xml.dom import minidom

from stackdiff.diff import ChangeType, DiffResult


def _prettify(element: ET.Element) -> str:
    """Return a pretty-printed XML string for *element*."""
    raw = ET.tostring(element, encoding="unicode")
    reparsed = minidom.parseString(raw)
    return reparsed.toprettyxml(indent="  ")


def format_diff(result: DiffResult) -> str:
    """Render *result* as a JUnit XML summary.

    One ``<testsuite>`` is produced with up to four ``<testcase>`` elements —
    one per change type.  A change type with a non-zero count is marked as a
    ``<failure>`` so that CI systems surface drift as a test failure.

    Parameters
    ----------
    result:
        The diff result to format.

    Returns
    -------
    str
        Pretty-printed JUnit XML.
    """
    counts = {
        ChangeType.ADDED: 0,
        ChangeType.REMOVED: 0,
        ChangeType.MODIFIED: 0,
        ChangeType.UNCHANGED: 0,
    }
    for diff in result.diffs:
        counts[diff.change_type] += 1

    total = sum(counts.values())
    failures = counts[ChangeType.ADDED] + counts[ChangeType.REMOVED] + counts[ChangeType.MODIFIED]

    suite = ET.Element(
        "testsuite",
        name="stackdiff",
        tests=str(total),
        failures=str(failures),
        errors="0",
    )

    labels = {
        ChangeType.ADDED: "added",
        ChangeType.REMOVED: "removed",
        ChangeType.MODIFIED: "modified",
        ChangeType.UNCHANGED: "unchanged",
    }

    for change_type, label in labels.items():
        count = counts[change_type]
        case = ET.SubElement(
            suite,
            "testcase",
            name=f"resources_{label}",
            classname="stackdiff.summary",
        )
        if change_type != ChangeType.UNCHANGED and count > 0:
            failure = ET.SubElement(case, "failure", message=f"{count} resource(s) {label}")
            failure.text = "\n".join(
                d.resource_id
                for d in result.diffs
                if d.change_type == change_type
            )

    return _prettify(suite)
