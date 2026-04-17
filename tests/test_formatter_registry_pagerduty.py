"""Ensure the PagerDuty formatter is registered in the formatter registry."""
from __future__ import annotations

from stackdiff.diff import DiffResult
from stackdiff.formatters.registry import available_formatters, get_formatter


class TestPagerDutyFormatterRegistered:
    def test_pagerduty_in_available(self):
        assert "pagerduty" in available_formatters()

    def test_get_pagerduty_formatter_returns_callable(self):
        fmt = get_formatter("pagerduty")
        assert callable(fmt)

    def test_pagerduty_formatter_produces_json(self):
        import json
        fmt = get_formatter("pagerduty")
        result = DiffResult(diffs=[])
        output = fmt(result)
        data = json.loads(output)
        assert "payload" in data
        assert "event_action" in data
