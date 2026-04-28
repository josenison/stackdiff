"""Registry integration tests for the diff-stat formatter."""
from __future__ import annotations

import pytest

from stackdiff.diff import ChangeType, DiffResult, ResourceDiff
from stackdiff.providers.base import Resource
from stackdiff.formatters.registry import available_formatters, get_formatter


def _empty_result() -> DiffResult:
    return DiffResult(diffs=[])


class TestDiffStatFormatterRegistered:
    def test_diff_stat_in_available(self):
        assert "diff-stat" in available_formatters()

    def test_get_diff_stat_formatter_returns_callable(self):
        fmt = get_formatter("diff-stat")
        assert callable(fmt)

    def test_diff_stat_formatter_produces_string(self):
        fmt = get_formatter("diff-stat")
        result = fmt(_empty_result())
        assert isinstance(result, str)

    def test_diff_stat_no_changes_message(self):
        fmt = get_formatter("diff-stat")
        result = fmt(_empty_result())
        assert "no changes" in result.lower() or result == "(no changes)"
