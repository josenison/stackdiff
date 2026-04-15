"""Registry mapping format names to formatter callables."""

from typing import Callable
from stackdiff.diff import DiffResult

_FORMATTERS: dict[str, Callable[[DiffResult], str]] = {}


def register_formatter(name: str, fn: Callable[[DiffResult], str]) -> None:
    """Register a formatter under *name*."""
    _FORMATTERS[name] = fn


def get_formatter(name: str) -> Callable[[DiffResult], str]:
    """Return the formatter for *name*, raising KeyError if unknown."""
    if name not in _FORMATTERS:
        available = ", ".join(sorted(_FORMATTERS))
        raise KeyError(
            f"Unknown formatter '{name}'. Available formatters: {available}"
        )
    return _FORMATTERS[name]


def available_formatters() -> list[str]:
    """Return a sorted list of registered formatter names."""
    return sorted(_FORMATTERS.keys())


# ---------------------------------------------------------------------------
# Register built-in formatters
# ---------------------------------------------------------------------------
from stackdiff.formatters import text as _text  # noqa: E402
from stackdiff.formatters import json_fmt as _json  # noqa: E402
from stackdiff.formatters import html_fmt as _html  # noqa: E402
from stackdiff.formatters import csv_fmt as _csv  # noqa: E402
from stackdiff.formatters import markdown_fmt as _md  # noqa: E402

register_formatter("text", _text.format_diff)
register_formatter("json", _json.format_diff)
register_formatter("html", _html.format_diff)
register_formatter("csv", _csv.format_diff)
register_formatter("markdown", _md.format_diff)
