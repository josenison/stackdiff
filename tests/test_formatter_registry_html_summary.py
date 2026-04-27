"""Registry integration tests for the HTML summary formatter."""
from __future__ import annotations

from stackdiff.diff import ChangeType, DiffResult, ResourceDiff
from stackdiff.formatters.registry import available_formatters, get_formatter


def _empty_result() -> DiffResult:
    return DiffResult(diffs=[])


class TestHTMLSummaryFormatterRegistered:
    def test_html_summary_in_available(self) -> None:
        assert "html-summary" in available_formatters()

    def test_get_html_summary_formatter_returns_callable(self) -> None:
        fmt = get_formatter("html-summary")
        assert callable(fmt)

    def test_html_summary_formatter_produces_html(self) -> None:
        fmt = get_formatter("html-summary")
        output = fmt(_empty_result())
        assert isinstance(output, str)
        assert "<!DOCTYPE html>" in output

    def test_html_summary_formatter_with_changes_produces_table(self) -> None:
        fmt = get_formatter("html-summary")
        result = DiffResult(
            diffs=[
                ResourceDiff(
                    resource_id="my-bucket",
                    resource_type="aws::s3::bucket",
                    change_type=ChangeType.ADDED,
                    detail=None,
                )
            ]
        )
        output = fmt(result)
        assert "<table" in output
        assert "my-bucket" in output
