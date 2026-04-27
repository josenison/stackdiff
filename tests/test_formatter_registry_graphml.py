"""Verify that the GraphML formatter is registered in the formatter registry."""
from __future__ import annotations

from stackdiff.diff import DiffResult
from stackdiff.formatters.registry import available_formatters, get_formatter


def _empty_result() -> DiffResult:
    return DiffResult(diffs=[])


class TestGraphMLFormatterRegistered:
    def test_graphml_in_available(self):
        assert "graphml" in available_formatters()

    def test_get_graphml_formatter_returns_callable(self):
        fmt = get_formatter("graphml")
        assert callable(fmt)

    def test_graphml_formatter_produces_xml(self):
        fmt = get_formatter("graphml")
        output = fmt(_empty_result())
        assert isinstance(output, str)
        assert "graphml" in output.lower()

    def test_graphml_formatter_produces_key_elements(self):
        fmt = get_formatter("graphml")
        output = fmt(_empty_result())
        assert "key" in output
