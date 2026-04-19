import json
import xml.etree.ElementTree as ET

from stackdiff.formatters.registry import get_formatter, available_formatters
from stackdiff.diff import DiffResult


def _empty_result():
    return DiffResult(diffs=[])


class TestJUnitSummaryFormatterRegistered:
    def test_junit_summary_in_available(self):
        assert "junit-summary" in available_formatters()

    def test_get_junit_summary_formatter_returns_callable(self):
        fmt = get_formatter("junit-summary")
        assert callable(fmt)

    def test_junit_summary_formatter_produces_xml(self):
        fmt = get_formatter("junit-summary")
        out = fmt(_empty_result())
        root = ET.fromstring(out)
        assert root.tag == "testsuite"
