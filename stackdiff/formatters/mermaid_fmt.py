"""Mermaid diagram formatter for stackdiff diff results."""
from __future__ import annotations

from stackdiff.diff import ChangeType, DiffResult

_SHAPE: dict[ChangeType, tuple[str, str]] = {
    ChangeType.ADDED: ("[", "]"),
    ChangeType.REMOVED: ["[", "]"],
    ChangeType.MODIFIED: ("(", ")"),
    ChangeType.UNCHANGED: ("[", "]"),
}

_STYLE: dict[ChangeType, str] = {
    ChangeType.ADDED: "fill:#2da44e,color:#fff,stroke:#2da44e",
    ChangeType.REMOVED: "fill:#cf222e,color:#fff,stroke:#cf222e",
    ChangeType.MODIFIED: "fill:#bf8700,color:#fff,stroke:#bf8700",
    ChangeType.UNCHANGED: "fill:#6e7781,color:#fff,stroke:#6e7781",
}


def _node_id(index: int) -> str:
    return f"node{index}"


def _label(resource_type: str, resource_id: str, change: ChangeType) -> str:
    symbol = {ChangeType.ADDED: "+", ChangeType.REMOVED: "-", ChangeType.MODIFIED: "~"}.get(change, " ")
    return f"{symbol} {resource_type}/{resource_id}"


def format_diff(result: DiffResult) -> str:
    """Render a DiffResult as a Mermaid flowchart diagram string."""
    if not result.has_changes:
        return "graph LR\n    no_changes[\"No changes detected\"]\n"

    lines: list[str] = ["graph LR"]
    style_lines: list[str] = []

    changes = [rd for rd in result.diffs if rd.change_type != ChangeType.UNCHANGED]

    for idx, rd in enumerate(changes):
        nid = _node_id(idx)
        label = _label(rd.resource_type, rd.resource_id, rd.change_type)
        open_b, close_b = _SHAPE.get(rd.change_type, ("[", "]"))
        lines.append(f'    {nid}{open_b}"{label}"{close_b}')
        style_lines.append(f"    style {nid} {_STYLE[rd.change_type]}")

    lines.extend(style_lines)
    return "\n".join(lines) + "\n"
