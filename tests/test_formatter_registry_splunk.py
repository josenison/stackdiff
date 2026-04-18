import json
import pytest
from stackdiff.formatters.registry import available_formatters, get_formatter
from stackdiff.diff import DiffResult


def _empty_result():
    return DiffResult(diffs=[])


class TestSplunkFormatterRegistered:
    def test_splunk_in_available(self):
        assert "splunk" in available_formatters()

    def test_get_splunk_formatter_returns_callable(self):
        fmt = get_formatter("splunk")
        assert callable(fmt)

    def test_splunk_formatter_produces_json(self):
        fmt = get_formatter("splunk")
        output = fmt(_empty_result())
        data = json.loads(output)
        assert "event" in data
