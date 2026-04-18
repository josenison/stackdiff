"""Ensure the Grafana formatter is registered."""
from __future__ import annotations

import json

from stackdiff.diff import DiffResult
from stackdiff.formatters.registry import available_formatters, get_formatter


class TestGrafanaFormatterRegistered:
    def test_grafana_in_available(self):
        assert "grafana" in available_formatters()

    def test_get_grafana_formatter_returns_callable(self):
        fmt = get_formatter("grafana")
        assert callable(fmt)

    def test_grafana_formatter_produces_json(self):
        fmt = get_formatter("grafana")
        result = DiffResult(diffs=[])
        output = fmt(result)
        parsed = json.loads(output)
        assert "tags" in parsed
        assert "text" in parsed
