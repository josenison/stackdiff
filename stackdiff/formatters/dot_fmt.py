"""Graphviz DOT formatter for stackdiff diff results."""
from stackdiff.diff import DiffResult, ChangeType

_COLORS = {
    ChangeType.ADDED: "green",
    ChangeType.REMOVED: "red",
    ChangeType.MODIFIED: "orange",
    ChangeType.UNCHANGED: "gray",
}


def _node_id(s: str) -> str:
    return '"' + s.replace('"', '\\"') + '"'


def format_diff(result: DiffResult, graph_name: str = "stackdiff") -> str:
    if not result.has_changes:
        return f'digraph {graph_name} {{\n  label="No changes detected";\n}}\n'

    lines = [f"digraph {graph_name} {{"]
    lines.append('  rankdir=LR;')
    lines.append('  node [shape=box fontname="Helvetica"];')
    lines.append('')

    for rd in result.diffs:
        nid = _node_id(rd.resource_id)
        color = _COLORS.get(rd.change_type, "black")
        label_parts = [rd.resource_id, rd.resource_type]
        if rd.change_type == ChangeType.MODIFIED and rd.attribute_changes:
            changed_attrs = ", ".join(rd.attribute_changes.keys())
            label_parts.append(f"changed: {changed_attrs}")
        label = "\\n".join(label_parts)
        change_label = rd.change_type.value.upper()
        lines.append(
            f'  {nid} [label="{label}" color={color} fontcolor={color} '
            f'tooltip="{change_label}"];'
        )

    lines.append("}")
    return "\n".join(lines) + "\n"
