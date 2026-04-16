"""JUnit XML formatter for stackdiff – useful for CI test-report integration."""
from xml.etree import ElementTree as ET
from xml.dom import minidom
from stackdiff.diff import DiffResult, ChangeType


def _prettify(element: ET.Element) -> str:
    raw = ET.tostring(element, encoding="unicode")
    return minidom.parseString(raw).toprettyxml(indent="  ")


def format_diff(result: DiffResult) -> str:
    diffs = result.diffs
    failures = [d for d in diffs if d.change_type != ChangeType.UNCHANGED]

    suite = ET.Element("testsuite")
    suite.set("name", "stackdiff")
    suite.set("tests", str(len(diffs)))
    suite.set("failures", str(len(failures)))
    suite.set("errors", "0")

    if not diffs:
        tc = ET.SubElement(suite, "testcase")
        tc.set("classname", "stackdiff")
        tc.set("name", "no_resources")
        return _prettify(suite)

    for d in diffs:
        tc = ET.SubElement(suite, "testcase")
        tc.set("classname", d.resource_type)
        tc.set("name", d.resource_id)
        if d.change_type != ChangeType.UNCHANGED:
            failure = ET.SubElement(tc, "failure")
            failure.set("message", f"{d.change_type.value}: {d.resource_id}")
            lines = [f"change_type : {d.change_type.value}"]
            if d.source:
                lines.append(f"source      : {d.source.attributes}")
            if d.target:
                lines.append(f"target      : {d.target.attributes}")
            failure.text = "\n".join(lines)

    return _prettify(suite)
