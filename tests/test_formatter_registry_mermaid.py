"""Tests that the Mermaid formatter is registered in the formatter registry."""
from __future__ import annotations

import pytest

from stackdiff.diff import DiffResult
from stackdiff.formatters.registry import available_formatters, get_formatter


def _empty_result() -> DiffResult:
    return DiffResult(diffs=[])


class TestMermaidFormatterRegistered:
    def test_mermaid_in_available(self):
        assert "mermaid" in available_formatters()

    def test_get_mermaid_formatter_returns_callable(self):
        fmt = get_formatter("mermaid")
        assert callable(fmt)

    def test_mermaid_formatter_produces_graph(self):
        fmt = get_formatter("mermaid")
        output = fmt(_empty_result())
        assert "graph LR" in output

    def test_mermaid_formatter_no_changes_message(self):
        fmt = get_formatter("mermaid")
        output = fmt(_empty_result())
        assert "No changes detected" in output
