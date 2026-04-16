"""XML formatter for diff results."""
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

from stackdiff.diff import DiffResult, ChangeType


def _prettify(elem: Element) -> str:
    raw = tostring(elem, encoding="unicode")
    reparsed = minidom.parseString(raw)
    return reparsed.toprettyxml(indent="  ", encoding=None)


def format_diff(result: DiffResult) -> str:
    root = Element("diff")
    root.set("source", result.source_name)
    root.set("target", result.target_name)
    root.set("has_changes", str(result.has_changes).lower())

    summary_el = SubElement(root, "summary")
    s = result.summary()
    summary_el.set("added", str(s.get("added", 0)))
    summary_el.set("removed", str(s.get("removed", 0)))
    summary_el.set("modified", str(s.get("modified", 0)))
    summary_el.set("unchanged", str(s.get("unchanged", 0)))

    changes_el = SubElement(root, "changes")
    for rd in result.diffs:
        change_el = SubElement(changes_el, "change")
        change_el.set("type", rd.change_type.value)
        res = rd.source or rd.target
        change_el.set("resource_id", res.resource_id)
        change_el.set("resource_type", res.resource_type)

        if rd.source:
            src_el = SubElement(change_el, "source")
            for k, v in rd.source.attributes.items():
                attr = SubElement(src_el, "attr")
                attr.set("key", k)
                attr.text = str(v)

        if rd.target:
            tgt_el = SubElement(change_el, "target")
            for k, v in rd.target.attributes.items():
                attr = SubElement(tgt_el, "attr")
                attr.set("key", k)
                attr.text = str(v)

        if rd.attribute_diffs:
            diffs_el = SubElement(change_el, "attribute_diffs")
            for attr_name, (old_val, new_val) in rd.attribute_diffs.items():
                diff_el = SubElement(diffs_el, "attribute")
                diff_el.set("name", attr_name)
                SubElement(diff_el, "old").text = str(old_val) if old_val is not None else ""
                SubElement(diff_el, "new").text = str(new_val) if new_val is not None else ""

    return _prettify(root)
