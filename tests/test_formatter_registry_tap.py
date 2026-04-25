"""Ensure the TAP formatter is registered in the formatter registry."""
from __future__ import annotations

import pytest

from stackdiff.diff import DiffResult
from stackdiff.formatters.registry import available_formatters, get_formatter


def _empty_result() -> DiffResult:
    return DiffResult(diffs=[])


class TestTAPFormatterRegistered:
    def test_tap_in_available(self):
        assert "tap" in available_formatters()

    def test_get_tap_formatter_returns_callable(self):
        fmt = get_formatter("tap")
        assert callable(fmt)

    def test_tap_formatter_produces_tap_version_line(self):
        fmt = get_formatter("tap")
        output = fmt(_empty_result())
        assert "TAP version 13" in output

    def test_tap_formatter_output_is_str(self):
        fmt = get_formatter("tap")
        result = fmt(_empty_result())
        assert isinstance(result, str)
