"""Ensure the TeamCity formatter is registered."""
import pytest

from stackdiff.formatters.registry import available_formatters, get_formatter
from stackdiff.diff import DiffResult


class TestTeamCityFormatterRegistered:
    def test_teamcity_in_available(self):
        assert "teamcity" in available_formatters()

    def test_get_teamcity_formatter_returns_callable(self):
        fmt = get_formatter("teamcity")
        assert callable(fmt)

    def test_teamcity_formatter_produces_service_messages(self):
        fmt = get_formatter("teamcity")
        out = fmt(DiffResult(diffs=[]))
        assert "##teamcity" in out
