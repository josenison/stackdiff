"""Tests that the SonarQube formatter is registered in the formatter registry."""
import json
import pytest
from stackdiff.formatters.registry import available_formatters, get_formatter
from stackdiff.providers.base import Resource
from stackdiff.diff import DiffResult, ResourceDiff, ChangeType


class TestSonarQubeFormatterRegistered:
    def test_sonarqube_in_available(self):
        assert "sonarqube" in available_formatters()

    def test_get_sonarqube_formatter_returns_callable(self):
        fmt = get_formatter("sonarqube")
        assert callable(fmt)

    def test_sonarqube_formatter_produces_json(self):
        fmt = get_formatter("sonarqube")
        r = Resource(resource_id="r1", resource_type="aws_instance", attributes={})
        result = DiffResult(diffs=[ResourceDiff(resource=r, change_type=ChangeType.ADDED)])
        out = fmt(result)
        parsed = json.loads(out)
        assert "issues" in parsed
