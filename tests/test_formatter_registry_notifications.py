"""Ensure notification formatters (slack, opsgenie) are registered."""
import pytest
from stackdiff.formatters.registry import get_formatter, available_formatters
from stackdiff.diff import DiffResult


class TestNotificationFormattersRegistered:
    def test_slack_in_available(self):
        assert "slack" in available_formatters()

    def test_opsgenie_in_available(self):
        assert "opsgenie" in available_formatters()

    def test_get_slack_formatter_returns_callable(self):
        fmt = get_formatter("slack")
        assert callable(fmt)

    def test_get_opsgenie_formatter_returns_callable(self):
        fmt = get_formatter("opsgenie")
        assert callable(fmt)

    def test_slack_formatter_produces_json(self):
        import json
        fmt = get_formatter("slack")
        output = fmt(DiffResult(diffs=[]))
        parsed = json.loads(output)
        assert "blocks" in parsed

    def test_opsgenie_formatter_produces_json(self):
        import json
        fmt = get_formatter("opsgenie")
        output = fmt(DiffResult(diffs=[]))
        parsed = json.loads(output)
        assert "priority" in parsed
