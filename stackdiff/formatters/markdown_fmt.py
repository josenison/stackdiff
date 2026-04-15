"""Markdown formatter for diff results."""

from stackdiff.diff import DiffResult, ChangeType


def _change_emoji(change_type: ChangeType) -> str:
    return {
        ChangeType.ADDED: "✅",
        ChangeType.REMOVED: "❌",
        ChangeType.MODIFIED: "🔄",
        ChangeType.UNCHANGED: "➖",
    }.get(change_type, "❓")


def format_diff(result: DiffResult, show_unchanged: bool = False) -> str:
    """Render a DiffResult as a Markdown string."""
    lines: list[str] = []

    lines.append("# Stack Diff Report")
    lines.append("")
    lines.append(f"**Base stack:** `{result.base_stack}`  ")
    lines.append(f"**Target stack:** `{result.target_stack}`")
    lines.append("")

    if not result.has_changes():
        lines.append("> No changes detected between stacks.")
        return "\n".join(lines)

    summary = result.summary()
    lines.append("## Summary")
    lines.append("")
    lines.append(
        f"- Added: **{summary['added']}**  "
        f"Removed: **{summary['removed']}**  "
        f"Modified: **{summary['modified']}**"
    )
    lines.append("")

    lines.append("## Changes")
    lines.append("")
    lines.append("| Change | Type | ID |")
    lines.append("|--------|------|----|")

    for diff in result.diffs:
        if diff.change_type == ChangeType.UNCHANGED and not show_unchanged:
            continue
        emoji = _change_emoji(diff.change_type)
        resource = diff.target or diff.base
        lines.append(
            f"| {emoji} `{diff.change_type.value}` "
            f"| `{resource.resource_type}` "
            f"| `{resource.resource_id}` |"
        )

        if diff.change_type == ChangeType.MODIFIED and diff.attribute_diffs:
            lines.append("")
            lines.append("  **Attribute changes:**")
            for attr, (old_val, new_val) in diff.attribute_diffs.items():
                lines.append(f"  - `{attr}`: `{old_val}` → `{new_val}`")
            lines.append("")

    return "\n".join(lines)
