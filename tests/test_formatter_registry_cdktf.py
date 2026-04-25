"""Registry integration tests for the cdktf formatter."""
from __future__ import annotations

import pytest

from stackdiff.diff import DiffResult
from stackdiff.formatters.registry import available_formatters, get_formatter


def _empty_result() -> DiffResult:
    return DiffResult(changes=[])


class TestCDKTFFormatterRegistered:
    def test_cdktf_in_available(self):
        assert "cdktf" in available_formatters()

    def test_get_cdktf_formatter_returns_callable(self):
        fmt = get_formatter("cdktf")
        assert callable(fmt)

    def test_cdktf_formatter_produces_string(self):
        fmt = get_formatter("cdktf")
        out = fmt(_empty_result())
        assert isinstance(out, str)

    def test_cdktf_formatter_no_changes_message(self):
        fmt = get_formatter("cdktf")
        out = fmt(_empty_result())
        assert "up-to-date" in out
