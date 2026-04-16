"""Verify the DOT formatter is registered in the formatter registry."""
import pytest
from stackdiff.formatters.registry import get_formatter, available_formatters


class TestDOTFormatterRegistered:
    def test_dot_formatter_in_available(self):
        assert "dot" in available_formatters()

    def test_get_dot_formatter_returns_callable(self):
        fmt = get_formatter("dot")
        assert callable(fmt)

    def test_dot_formatter_produces_digraph(self):
        from stackdiff.diff import DiffResult
        fmt = get_formatter("dot")
        result = DiffResult(diffs=[])
        out = fmt(result)
        assert "digraph" in out
