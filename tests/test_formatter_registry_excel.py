"""Verify the Excel formatter is registered in the formatter registry."""
from __future__ import annotations

import pytest

openpyxl = pytest.importorskip("openpyxl")

from stackdiff.formatters.registry import available_formatters, get_formatter  # noqa: E402
from stackdiff.diff import DiffResult  # noqa: E402


class TestExcelFormatterRegistered:
    def test_excel_in_available(self):
        assert "excel" in available_formatters()

    def test_get_excel_formatter_returns_callable(self):
        fmt = get_formatter("excel")
        assert callable(fmt)

    def test_excel_formatter_produces_bytes(self):
        fmt = get_formatter("excel")
        result = DiffResult(diffs=[])
        output = fmt(result)
        assert isinstance(output, bytes)
        # XLSX files start with PK (zip magic bytes)
        assert output[:2] == b"PK"
