"""JUnit summary formatter — one test-case per resource diff."""
from xml.dom import minidom
import xml.etree.ElementTree as ET

from stackdiff.diff import DiffResult, ChangeType


def _prettify(elem: ET.Element) -> str:
    raw = ET.tostring(elem, encoding="unicode")
    return minidom.parseString(raw).toprettyxml(indent="  ")


def format_diff(result: DiffResult) -> str:
    suite = ET.Element("testsuite")
    suite.set("name", "stackdiff")
    suite.set("tests", str(len(result.diffs)))

    failures = sum(
        1 for d in result.diffs if d.change_type != ChangeType.UNCHANGED
    )
    suite.set("failures", str(failures))

    if not result.diffs:
        tc = ET.SubElement(suite, "testcase")
        tc.set("name", "no_changes")
        tc.set("classname", "stackdiff.summary")
        return _prettify(suite)

    for diff in result.diffs:
        tc = ET.SubElement(suite, "testcase")
        tc.set("name", diff.resource_id)
        tc.set("classname", f"stackdiff.{diff.change_type.value}")
        if diff.change_type != ChangeType.UNCHANGED:
            failure = ET.SubElement(tc, "failure")
            failure.set("message", f"{diff.change_type.value}: {diff.resource_id}")
            lines = []
            if diff.old_resource:
                lines.append(f"  old type: {diff.old_resource.resource_type}")
            if diff.new_resource:
                lines.append(f"  new type: {diff.new_resource.resource_type}")
            failure.text = "\n".join(lines)

    return _prettify(suite)
