"""Registry integration tests for the Pulumi formatter."""
from __future__ import annotations

import pytest

from stackdiff.diff import ChangeType, DiffResult, ResourceDiff
from stackdiff.formatters.registry import available_formatters, get_formatter
from stackdiff.providers.base import Resource


def _empty_result() -> DiffResult:
    return DiffResult(changes=[])


class TestPulumiFormatterRegistered:
    def test_pulumi_in_available(self):
        assert "pulumi" in available_formatters()

    def test_get_pulumi_formatter_returns_callable(self):
        fmt = get_formatter("pulumi")
        assert callable(fmt)

    def test_pulumi_formatter_produces_string(self):
        fmt = get_formatter("pulumi")
        result = fmt(_empty_result())
        assert isinstance(result, str)

    def test_pulumi_formatter_no_changes_message(self):
        fmt = get_formatter("pulumi")
        output = fmt(_empty_result())
        assert "no changes" in output
