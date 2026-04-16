"""Formatter registry – maps format names to callables."""
from __future__ import annotations

from typing import Callable

from stackdiff.diff import DiffResult

_REGISTRY: dict[str, Callable[[DiffResult], str]] = {}


def register_formatter(name: str, fn: Callable[[DiffResult], str]) -> None:
    _REGISTRY[name] = fn


def get_formatter(name: str) -> Callable[[DiffResult], str]:
    if name not in _REGISTRY:
        raise KeyError(f"Unknown formatter: {name!r}. Available: {available_formatters()}")
    return _REGISTRY[name]


def available_formatters() -> list[str]:
    return sorted(_REGISTRY.keys())


def _register_builtins() -> None:
    from stackdiff.formatters import (
        text,
        json_fmt,
        yaml_fmt,
        toml_fmt,
        csv_fmt,
        html_fmt,
        markdown_fmt,
        table_fmt,
        xml_fmt,
        dot_fmt,
        junit_fmt,
        github_fmt,
    )

    register_formatter("text", text.format_diff)
    register_formatter("json", json_fmt.format_diff)
    register_formatter("yaml", yaml_fmt.format_diff)
    register_formatter("toml", toml_fmt.format_diff)
    register_formatter("csv", csv_fmt.format_diff)
    register_formatter("html", html_fmt.format_diff)
    register_formatter("markdown", markdown_fmt.format_diff)
    register_formatter("table", table_fmt.format_diff)
    register_formatter("xml", xml_fmt.format_diff)
    register_formatter("dot", dot_fmt.format_diff)
    register_formatter("junit", junit_fmt.format_diff)
    register_formatter("github", github_fmt.format_diff)


_register_builtins()
