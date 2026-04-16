"""Tests for the formatter registry."""
from __future__ import annotations

import pytest

from stackdiff.formatters.registry import (
    register_formatter,
    get_formatter,
    available_formatters,
)
from stackdiff.diff import DiffResult


def _empty_result() -> DiffResult:
    return DiffResult(changes=[])


class TestFormatterRegistry:
    def test_builtin_formatters_registered(self):
        names = available_formatters()
        for expected in ("text", "json", "yaml", "csv", "html", "markdown", "table", "xml", "toml"):
            assert expected in names

    def test_available_formatters_sorted(self):
        names = available_formatters()
        assert names == sorted(names)

    def test_get_unknown_formatter_raises(self):
        with pytest.raises(KeyError, match="Unknown formatter"):
            get_formatter("nonexistent")

    def test_register_custom_formatter(self):
        def my_fmt(result: DiffResult) -> str:
            return "custom"

        register_formatter("custom_test", my_fmt)
        assert "custom_test" in available_formatters()
        fn = get_formatter("custom_test")
        assert fn(_empty_result()) == "custom"

    def test_get_text_formatter_callable(self):
        fn = get_formatter("text")
        assert callable(fn)

    def test_get_json_formatter_returns_valid_json(self):
        import json
        fn = get_formatter("json")
        output = fn(_empty_result())
        data = json.loads(output)
        assert "has_changes" in data

    def test_get_yaml_formatter_returns_yaml(self):
        import yaml
        fn = get_formatter("yaml")
        output = fn(_empty_result())
        data = yaml.safe_load(output)
        assert "has_changes" in data
