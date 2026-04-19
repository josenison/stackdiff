"""Ensure the webhook formatter is registered in the formatter registry."""
from __future__ import annotations

import json

from stackdiff.diff import DiffResult
from stackdiff.formatters.registry import available_formatters, get_formatter


def _empty_result() -> DiffResult:
    return DiffResult(diffs=[])


class TestWebhookFormatterRegistered:
    def test_webhook_in_available(self):
        assert "webhook" in available_formatters()

    def test_get_webhook_formatter_returns_callable(self):
        fmt = get_formatter("webhook")
        assert callable(fmt)

    def test_webhook_formatter_produces_json(self):
        fmt = get_formatter("webhook")
        output = fmt(_empty_result())
        parsed = json.loads(output)
        assert "has_changes" in parsed
        assert "summary" in parsed
        assert "changes" in parsed
