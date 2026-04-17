"""Slack Block Kit formatter for diff results."""
from __future__ import annotations
import json
from stackdiff.diff import DiffResult, ChangeType

_EMOJI = {
    ChangeType.ADDED: ":large_green_circle:",
    ChangeType.REMOVED: ":red_circle:",
    ChangeType.MODIFIED: ":large_yellow_circle:",
}


def format_diff(result: DiffResult) -> str:
    blocks: list[dict] = []

    if not result.has_changes:
        blocks.append({
            "type": "section",
            "text": {"type": "mrkdwn", "text": ":white_check_mark: No changes detected."},
        })
        return json.dumps({"blocks": blocks}, indent=2)

    blocks.append({
        "type": "header",
        "text": {"type": "plain_text", "text": "Stack Diff Results"},
    })

    summary = result.summary()
    blocks.append({
        "type": "section",
        "text": {"type": "mrkdwn", "text": f"*Summary:* {summary}"},
    })

    blocks.append({"type": "divider"})

    for rd in result.diffs:
        emoji = _EMOJI.get(rd.change_type, ":white_circle:")
        label = rd.change_type.value.upper()
        text = f"{emoji} *[{label}]* `{rd.resource_type}` — `{rd.resource_id}`"
        if rd.change_type == ChangeType.MODIFIED and rd.diff_lines:
            diff_block = "\n".join(rd.diff_lines[:10])
            text += f"\n```{diff_block}```"
        blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": text}})

    return json.dumps({"blocks": blocks}, indent=2)
