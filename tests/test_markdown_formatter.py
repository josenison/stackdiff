"""Tests for the Markdown formatter and formatter registry."""

import pytest
from stackdiff.diff import ChangeType, DiffResult, ResourceDiff
from stackdiff.providers.base import Resource
from stackdiff.formatters.markdown_fmt import format_diff
from stackdiff.formatters.registry import (
    get_formatter,
    available_formatters,
    register_formatter,
)


def _res(rid: str, rtype: str = "instance", **attrs) -> Resource:
    return Resource(resource_id=rid, resource_type=rtype, attributes=attrs)


def _rdiff(change_type: ChangeType, base=None, target=None, attr_diffs=None):
    return ResourceDiff(
        change_type=change_type,
        base=base,
        target=target,
        attribute_diffs=attr_diffs or {},
    )


def _make_result(diffs):
    return DiffResult(base_stack="prod", target_stack="staging", diffs=diffs)


class TestMarkdownFormatter:
    def test_no_changes_returns_no_changes_message(self):
        result = _make_result([])
        output = format_diff(result)
        assert "No changes detected" in output

    def test_headers_present(self):
        result = _make_result([])
        output = format_diff(result)
        assert "# Stack Diff Report" in output
        assert "`prod`" in output
        assert "`staging`" in output

    def test_added_resource_shown(self):
        diff = _rdiff(ChangeType.ADDED, target=_res("i-123", "ec2"))
        output = format_diff(_make_result([diff]))
        assert "added" in output
        assert "i-123" in output
        assert "✅" in output

    def test_removed_resource_shown(self):
        diff = _rdiff(ChangeType.REMOVED, base=_res("i-999", "ec2"))
        output = format_diff(_make_result([diff]))
        assert "removed" in output
        assert "i-999" in output
        assert "❌" in output

    def test_modified_resource_shows_attribute_diffs(self):
        diff = _rdiff(
            ChangeType.MODIFIED,
            base=_res("i-abc", "ec2", size="t2.micro"),
            target=_res("i-abc", "ec2", size="t3.small"),
            attr_diffs={"size": ("t2.micro", "t3.small")},
        )
        output = format_diff(_make_result([diff]))
        assert "size" in output
        assert "t2.micro" in output
        assert "t3.small" in output

    def test_unchanged_hidden_by_default(self):
        diff = _rdiff(ChangeType.UNCHANGED, base=_res("i-000"), target=_res("i-000"))
        output = format_diff(_make_result([diff]))
        assert "i-000" not in output

    def test_unchanged_shown_when_flag_set(self):
        diff = _rdiff(ChangeType.UNCHANGED, base=_res("i-000"), target=_res("i-000"))
        output = format_diff(_make_result([diff]), show_unchanged=True)
        assert "i-000" in output


class TestFormatterRegistry:
    def test_builtin_formatters_registered(self):
        names = available_formatters()
        assert "text" in names
        assert "json" in names
        assert "html" in names
        assert "csv" in names
        assert "markdown" in names

    def test_get_known_formatter_returns_callable(self):
        fn = get_formatter("markdown")
        assert callable(fn)

    def test_get_unknown_formatter_raises(self):
        with pytest.raises(KeyError, match="Unknown formatter"):
            get_formatter("nonexistent")

    def test_register_custom_formatter(self):
        register_formatter("custom", lambda r: "custom output")
        fn = get_formatter("custom")
        assert fn(None) == "custom output"
