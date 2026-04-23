"""Registry integration tests for the timeline formatter."""
from __future__ import annotations

import pytest

from stackdiff.diff import ChangeType, DiffResult, ResourceDiff
from stackdiff.formatters.registry import available_formatters, get_formatter
from stackdiff.providers.base import Resource


def _empty_result() -> DiffResult:
    return DiffResult(left_name="dev", right_name="prod", diffs=[])


class TestTimelineFormatterRegistered:
    def test_timeline_in_available(self):
        assert "timeline" in available_formatters()

    def test_get_timeline_formatter_returns_callable(self):
        fmt = get_formatter("timeline")
        assert callable(fmt)

    def test_timeline_formatter_produces_header(self):
        fmt = get_formatter("timeline")
        output = fmt(_empty_result())
        assert "stackdiff timeline" in output

    def test_timeline_formatter_returns_string(self):
        fmt = get_formatter("timeline")
        result = fmt(_empty_result())
        assert isinstance(result, str)
