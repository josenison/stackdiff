"""Verify the badge formatter is registered in the formatter registry."""
from __future__ import annotations

import json

from stackdiff.formatters.registry import available_formatters, get_formatter
from stackdiff.diff import DiffResult


def _empty_result() -> DiffResult:
    return DiffResult(diffs=[])


class TestBadgeFormatterRegistered:
    def test_badge_in_available(self):
        assert "badge" in available_formatters()

    def test_get_badge_formatter_returns_callable(self):
        fmt = get_formatter("badge")
        assert callable(fmt)

    def test_badge_formatter_produces_json(self):
        fmt = get_formatter("badge")
        output = fmt(_empty_result())
        data = json.loads(output)
        assert "schemaVersion" in data
        assert "message" in data
        assert "color" in data
