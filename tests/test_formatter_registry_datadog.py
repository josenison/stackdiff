"""Ensure the Datadog formatter is registered in the formatter registry."""
from __future__ import annotations

import json

from stackdiff.formatters.registry import available_formatters, get_formatter
from stackdiff.diff import DiffResult


class TestDatadogFormatterRegistered:
    def test_datadog_in_available(self):
        assert "datadog" in available_formatters()

    def test_get_datadog_formatter_returns_callable(self):
        fmt = get_formatter("datadog")
        assert callable(fmt)

    def test_datadog_formatter_produces_json(self):
        fmt = get_formatter("datadog")
        result = DiffResult(diffs=[])
        output = fmt(result)
        parsed = json.loads(output)
        assert "title" in parsed
        assert "alert_type" in parsed
