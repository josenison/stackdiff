"""HTML summary formatter — renders a self-contained HTML page with a
collapsible diff table and a colour-coded summary banner."""
from __future__ import annotations

from stackdiff.diff import ChangeType, DiffResult

_COLORS = {
    ChangeType.ADDED: "#2da44e",
    ChangeType.REMOVED: "#cf222e",
    ChangeType.MODIFIED: "#9a6700",
    ChangeType.UNCHANGED: "#57606a",
}

_LABELS = {
    ChangeType.ADDED: "added",
    ChangeType.REMOVED: "removed",
    ChangeType.MODIFIED: "modified",
    ChangeType.UNCHANGED: "unchanged",
}


def _badge(change_type: ChangeType) -> str:
    color = _COLORS[change_type]
    label = _LABELS[change_type]
    return (
        f'<span style="background:{color};color:#fff;'
        f'padding:2px 6px;border-radius:3px;font-size:0.85em">{label}</span>'
    )


def format_diff(result: DiffResult) -> str:
    """Return a self-contained HTML page summarising *result*."""
    title = "stackdiff — infrastructure diff report"

    if not result.has_changes:
        body = "<p style='color:#2da44e;font-weight:bold'>✓ No changes detected.</p>"
        return (
            f"<!DOCTYPE html><html><head><meta charset='utf-8'>"
            f"<title>{title}</title></head>"
            f"<body><h1>{title}</h1>{body}</body></html>"
        )

    summary = result.summary
    rows_html = []
    for rd in result.diffs:
        color = _COLORS[rd.change_type]
        rows_html.append(
            f"<tr>"
            f"<td style='color:{color}'>{rd.resource_id}</td>"
            f"<td>{rd.resource_type}</td>"
            f"<td>{_badge(rd.change_type)}</td>"
            f"<td><pre style='margin:0'>{rd.detail or ''}</pre></td>"
            f"</tr>"
        )

    rows = "\n".join(rows_html)
    table = (
        "<table border='1' cellpadding='4' cellspacing='0' "
        "style='border-collapse:collapse;width:100%'>"
        "<thead><tr>"
        "<th>Resource ID</th><th>Type</th><th>Change</th><th>Detail</th>"
        "</tr></thead>"
        f"<tbody>{rows}</tbody></table>"
    )

    return (
        f"<!DOCTYPE html><html><head><meta charset='utf-8'>"
        f"<title>{title}</title></head>"
        f"<body>"
        f"<h1>{title}</h1>"
        f"<p><strong>Summary:</strong> {summary}</p>"
        f"{table}"
        f"</body></html>"
    )
