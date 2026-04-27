"""Tests for the HTML summary formatter."""
from __future__ import annotations

from html.parser import HTMLParser
from stackdiff.diff import ChangeType, DiffResult, ResourceDiff
from stackdiff.formatters.html_summary_fmt import format_diff


class _TagCollector(HTMLParser):
    """Minimal parser that collects tag names to verify valid HTML structure."""

    def __init__(self) -> None:
        super().__init__()
        self.tags: list[str] = []

    def handle_starttag(self, tag: str, attrs: object) -> None:  # noqa: ARG002
        self.tags.append(tag)


def _res(rid: str, rtype: str = "aws::ec2::instance") -> ResourceDiff:
    return ResourceDiff(
        resource_id=rid,
        resource_type=rtype,
        change_type=ChangeType.ADDED,
        detail=None,
    )


def _rdiff(
    rid: str,
    change: ChangeType = ChangeType.ADDED,
    detail: str | None = None,
) -> ResourceDiff:
    return ResourceDiff(
        resource_id=rid,
        resource_type="aws::s3::bucket",
        change_type=change,
        detail=detail,
    )


def _make_result(diffs: list[ResourceDiff]) -> DiffResult:
    return DiffResult(diffs=diffs)


class TestHTMLSummaryFormatter:
    def test_no_changes_returns_no_changes_message(self) -> None:
        result = _make_result([])
        html = format_diff(result)
        assert "No changes detected" in html

    def test_no_changes_is_valid_html(self) -> None:
        result = _make_result([])
        html = format_diff(result)
        collector = _TagCollector()
        collector.feed(html)  # must not raise
        assert "html" in collector.tags

    def test_added_resource_shown(self) -> None:
        result = _make_result([_rdiff("bucket-1", ChangeType.ADDED)])
        html = format_diff(result)
        assert "bucket-1" in html
        assert "added" in html

    def test_removed_resource_shown(self) -> None:
        result = _make_result([_rdiff("old-vm", ChangeType.REMOVED)])
        html = format_diff(result)
        assert "old-vm" in html
        assert "removed" in html

    def test_modified_resource_shown(self) -> None:
        result = _make_result([_rdiff("queue-1", ChangeType.MODIFIED, detail="size changed")])
        html = format_diff(result)
        assert "queue-1" in html
        assert "modified" in html
        assert "size changed" in html

    def test_multiple_resources_all_present(self) -> None:
        diffs = [
            _rdiff("res-a", ChangeType.ADDED),
            _rdiff("res-b", ChangeType.REMOVED),
            _rdiff("res-c", ChangeType.MODIFIED),
        ]
        html = format_diff(_make_result(diffs))
        for rid in ("res-a", "res-b", "res-c"):
            assert rid in html

    def test_output_contains_table(self) -> None:
        result = _make_result([_rdiff("x", ChangeType.ADDED)])
        html = format_diff(result)
        assert "<table" in html
        assert "<tbody>" in html

    def test_summary_line_present(self) -> None:
        result = _make_result([_rdiff("x", ChangeType.ADDED)])
        html = format_diff(result)
        assert "Summary" in html
