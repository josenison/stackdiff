"""Formatter registry — maps format names to callable formatters."""
from __future__ import annotations

from typing import Callable

from stackdiff.diff import DiffResult

_registry: dict[str, Callable[[DiffResult], str | bytes]] = {}
_builtins_registered = False


def register_formatter(
    name: str, fn: Callable[[DiffResult], str | bytes]
) -> None:
    """Register *fn* under *name*."""
    _registry[name] = fn


def get_formatter(name: str) -> Callable[[DiffResult], str | bytes]:
    """Return the formatter registered under *name*.

    Raises KeyError if not found.
    """
    _ensure_builtins()
    if name not in _registry:
        available = ", ".join(sorted(_registry))
        raise KeyError(
            f"Unknown formatter {name!r}. Available: {available}"
        )
    return _registry[name]


def available_formatters() -> list[str]:
    """Return sorted list of registered formatter names."""
    _ensure_builtins()
    return sorted(_registry)


def _ensure_builtins() -> None:
    global _builtins_registered
    if not _builtins_registered:
        _register_builtins()
        _builtins_registered = True


def _register_builtins() -> None:  # noqa: PLR0915
    from stackdiff.formatters import text as _text
    register_formatter("text", _text.format_diff)

    from stackdiff.formatters import json_fmt as _json
    register_formatter("json", _json.format_diff_to_str)

    from stackdiff.formatters import yaml_fmt as _yaml
    register_formatter("yaml", _yaml.format_diff)

    from stackdiff.formatters import csv_fmt as _csv
    register_formatter("csv", _csv.format_diff)

    from stackdiff.formatters import html_fmt as _html
    register_formatter("html", _html.format_diff)

    from stackdiff.formatters import markdown_fmt as _md
    register_formatter("markdown", _md.format_diff)

    from stackdiff.formatters import table_fmt as _table
    register_formatter("table", _table.format_diff)

    from stackdiff.formatters import xml_fmt as _xml
    register_formatter("xml", _xml.format_diff)

    from stackdiff.formatters import toml_fmt as _toml
    register_formatter("toml", _toml.format_diff)

    from stackdiff.formatters import dot_fmt as _dot
    register_formatter("dot", _dot.format_diff)

    from stackdiff.formatters import junit_fmt as _junit
    register_formatter("junit", _junit.format_diff)

    from stackdiff.formatters import github_fmt as _github
    register_formatter("github", _github.format_diff)

    from stackdiff.formatters import color_fmt as _color
    register_formatter("color", _color.format_diff)

    from stackdiff.formatters import slack_fmt as _slack
    register_formatter("slack", _slack.format_diff)

    from stackdiff.formatters import opsgenie_fmt as _opsgenie
    register_formatter("opsgenie", _opsgenie.format_diff)

    from stackdiff.formatters import pagerduty_fmt as _pagerduty
    register_formatter("pagerduty", _pagerduty.format_diff)

    from stackdiff.formatters import prometheus_fmt as _prom
    register_formatter("prometheus", _prom.format_diff)

    from stackdiff.formatters import sonarqube_fmt as _sq
    register_formatter("sonarqube", _sq.format_diff)

    from stackdiff.formatters import sarif_fmt as _sarif
    register_formatter("sarif", _sarif.format_diff)

    from stackdiff.formatters import teamcity_fmt as _tc
    register_formatter("teamcity", _tc.format_diff)

    from stackdiff.formatters import splunk_fmt as _splunk
    register_formatter("splunk", _splunk.format_diff)

    from stackdiff.formatters import datadog_fmt as _datadog
    register_formatter("datadog", _datadog.format_diff)

    from stackdiff.formatters import grafana_fmt as _grafana
    register_formatter("grafana", _grafana.format_diff)

    from stackdiff.formatters import newrelic_fmt as _newrelic
    register_formatter("newrelic", _newrelic.format_diff)

    from stackdiff.formatters import webhook_fmt as _webhook
    register_formatter("webhook", _webhook.format_diff)

    from stackdiff.formatters import csv_summary_fmt as _csv_sum
    register_formatter("csv-summary", _csv_sum.format_diff)

    from stackdiff.formatters import junit_summary_fmt as _junit_sum
    register_formatter("junit-summary", _junit_sum.format_diff)

    from stackdiff.formatters import badge_fmt as _badge
    register_formatter("badge", _badge.format_diff)

    from stackdiff.formatters import timeline_fmt as _timeline
    register_formatter("timeline", _timeline.format_diff)

    from stackdiff.formatters import ndjson_fmt as _ndjson
    register_formatter("ndjson", _ndjson.format_diff)

    from stackdiff.formatters import excel_fmt as _excel
    register_formatter("excel", _excel.format_diff)

    from stackdiff.formatters import mermaid_fmt as _mermaid
    register_formatter("mermaid", _mermaid.format_diff)

    from stackdiff.formatters import ansible_fmt as _ansible
    register_formatter("ansible", _ansible.format_diff)

    from stackdiff.formatters import tap_fmt as _tap
    register_formatter("tap", _tap.format_diff)

    from stackdiff.formatters import checkstyle_fmt as _checkstyle
    register_formatter("checkstyle", _checkstyle.format_diff)

    from stackdiff.formatters import terraform_plan_fmt as _tfplan
    register_formatter("terraform-plan", _tfplan.format_diff)
