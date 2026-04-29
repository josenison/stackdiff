import json
import pytest

from stackdiff.diff import DiffResult
from stackdiff.formatters.registry import available_formatters, get_formatter


def _empty_result() -> DiffResult:
    return DiffResult(diffs=[])


class TestScorecardFormatterRegistered:
    def test_scorecard_in_available(self):
        assert "scorecard" in available_formatters()

    def test_get_scorecard_formatter_returns_callable(self):
        fmt = get_formatter("scorecard")
        assert callable(fmt)

    def test_scorecard_formatter_produces_json(self):
        fmt = get_formatter("scorecard")
        output = fmt(_empty_result())
        data = json.loads(output)
        assert "score" in data
        assert "grade" in data

    def test_scorecard_no_changes_score_100_via_registry(self):
        fmt = get_formatter("scorecard")
        data = json.loads(fmt(_empty_result()))
        assert data["score"] == 100
        assert data["grade"] == "A+"
