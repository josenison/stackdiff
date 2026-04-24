"""Verify the NDJSON formatter is registered in the formatter registry."""
from __future__ import annotations

import json

from stackdiff.diff import DiffResult
from stackdiff.formatters.registry import available_formatters, get_formatter


def _empty_result() -> DiffResult:
    return DiffResult(diffs=[])


class TestNDJSONFormatterRegistered:
    def test_ndjson_in_available(self):
        assert "ndjson" in available_formatters()

    def test_get_ndjson_formatter_returns_callable(self):
        fmt = get_formatter("ndjson")
        assert callable(fmt)

    def test_ndjson_formatter_produces_valid_json_line(self):
        fmt = get_formatter("ndjson")
        output = fmt(_empty_result())
        # Must be a single valid JSON line for the no-changes case
        line = output.strip().splitlines()[0]
        data = json.loads(line)
        assert "has_changes" in data
