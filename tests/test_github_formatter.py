"""Tests for the GitHub Actions annotation formatter."""
import pytest

from stackdiff.diff import ChangeType, DiffResult, ResourceDiff
from stackdiff.formatters.github_fmt import format_diff
from stackdiff.providers.base import Resource


def _res(rid: str, rtype: str = "instance", **attrs) -> Resource:
    return Resource(resource_id=rid, resource_type=rtype, attributes=attrs)


def _rdiff(
    resource: Resource,
    change_type: ChangeType,
    attribute_diffs: dict | None = None,
) -> ResourceDiff:
    return ResourceDiff(resource=resource, change_type=change_type, attribute_diffs=attribute_diffs or {})


def _make_result(diffs: list[ResourceDiff]) -> DiffResult:
    return DiffResult(diffs=diffs)


class TestGitHubFormatter:
    def test_no_changes_returns_notice(self):
        result = _make_result([])
        out = format_diff(result)
        assert out.startswith("::notice::")
        assert "no changes" in out

    def test_added_resource_uses_notice_level(self):
        rd = _rdiff(_res("i-123"), ChangeType.ADDED)
        out = format_diff(_make_result([rd]))
        assert "::notice title=ADDED: instance/i-123::" in out

    def test_removed_resource_uses_error_level(self):
        rd = _rdiff(_res("i-456"), ChangeType.REMOVED)
        out = format_diff(_make_result([rd]))
        assert "::error title=REMOVED: instance/i-456::" in out

    def test_modified_resource_uses_warning_level(self):
        rd = _rdiff(
            _res("i-789"),
            ChangeType.MODIFIED,
            attribute_diffs={"size": ("t2.micro", "t3.small")},
        )
        out = format_diff(_make_result([rd]))
        assert "::warning title=MODIFIED: instance/i-789::" in out
        assert "size: 't2.micro' -> 't3.small'" in out

    def test_summary_line_appended(self):
        diffs = [
            _rdiff(_res("a"), ChangeType.ADDED),
            _rdiff(_res("b"), ChangeType.REMOVED),
        ]
        out = format_diff(_make_result(diffs))
        assert "added=1 removed=1 modified=0" in out

    def test_github_formatter_registered(self):
        from stackdiff.formatters.registry import get_formatter
        fn = get_formatter("github")
        assert callable(fn)

    def test_github_in_available_formatters(self):
        from stackdiff.formatters.registry import available_formatters
        assert "github" in available_formatters()
