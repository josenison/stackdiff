"""HTML formatter for diff results."""
from __future__ import annotations

from stackdiff.diff import ChangeType, DiffResult, ResourceDiff

_COLORS = {
    ChangeType.ADDED: "#d4edda",
    ChangeType.REMOVED: "#f8d7da",
    ChangeType.MODIFIED: "#fff3cd",
    ChangeType.UNCHANGED: "#ffffff",
}

_LABELS = {
    ChangeType.ADDED: "ADDED",
    ChangeType.REMOVED: "REMOVED",
    ChangeType.MODIFIED: "MODIFIED",
    ChangeType.UNCHANGED: "UNCHANGED",
}


def _render_row(rd: ResourceDiff) -> str:
    color = _COLORS[rd.change_type]
    label = _LABELS[rd.change_type]
    resource = rd.resource_after or rd.resource_before
    assert resource is not None
    attrs_html = ""
    if rd.change_type == ChangeType.MODIFIED and rd.resource_before and rd.resource_after:
        before_attrs = rd.resource_before.attributes
        after_attrs = rd.resource_after.attributes
        all_keys = sorted(set(before_attrs) | set(after_attrs))
        parts = []
        for k in all_keys:
            bv = before_attrs.get(k, "<em>absent</em>")
            av = after_attrs.get(k, "<em>absent</em>")
            if bv != av:
                parts.append(f"<li><strong>{k}</strong>: {bv} &rarr; {av}</li>")
        attrs_html = "<ul>" + "".join(parts) + "</ul>" if parts else ""
    return (
        f'<tr style="background:{color};">'
        f"<td>{label}</td>"
        f"<td>{resource.resource_type}</td>"
        f"<td>{resource.resource_id}</td>"
        f"<td>{attrs_html}</td>"
        f"</tr>\n"
    )


def format_diff(result: DiffResult) -> str:
    """Return an HTML string representing the diff result."""
    if not result.has_changes():
        return "<p>No changes detected between stacks.</p>\n"

    rows = "".join(_render_row(rd) for rd in result.diffs if rd.change_type != ChangeType.UNCHANGED)
    summary = result.summary()
    summary_html = (
        f"<p>Added: {summary['added']}, "
        f"Removed: {summary['removed']}, "
        f"Modified: {summary['modified']}</p>\n"
    )
    header = (
        "<table border='1' cellpadding='4' cellspacing='0'>\n"
        "<thead><tr><th>Change</th><th>Type</th><th>ID</th><th>Details</th></tr></thead>\n"
        "<tbody>\n"
    )
    return summary_html + header + rows + "</tbody></table>\n"
