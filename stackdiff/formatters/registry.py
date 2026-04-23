"""Formatter registry – maps format names to callables."""
from __future__ import annotations

from typing import Callable, Dict, List

from stackdiff.diff import DiffResult

_registry: Dict[str, Callable[[DiffResult], str]] = {}


def register_formatter(name: str, fn: Callable[[DiffResult], str]) -> None:
    """Register a formatter under *name*."""
    _registry[name] = fn


def get_formatter(name: str) -> Callable[[DiffResult], str]:
    """Return the formatter callable for *name*, raising KeyError if absent."""
    if name not in _registry:
        raise KeyError(f"Unknown formatter: {name!r}. Available: {available_formatters()}")
    return _registry[name]


def available_formatters() -> List[str]:
    """Return a sorted list of registered formatter names."""
    return sorted(_registry.keys())


def _register_builtins() -> None:
    from stackdiff.formatters import text as _text
    from stackdiff.formatters import json_fmt as _json
    from stackdiff.formatters import yaml_fmt as _yaml
    from stackdiff.formatters import html_fmt as _html
    from stackdiff.formatters import csv_fmt as _csv
    from stackdiff.formatters import markdown_fmt as _md
    from stackdiff.formatters import table_fmt as _table
    from stackdiff.formatters import xml_fmt as _xml
    from stackdiff.formatters import toml_fmt as _toml
    from stackdiff.formatters import dot_fmt as _dot
    from stackdiff.formatters import junit_fmt as _junit
    from stackdiff.formatters import github_fmt as _github
    from stackdiff.formatters import color_fmt as _color
    from stackdiff.formatters import slack_fmt as _slack
    from stackdiff.formatters import opsgenie_fmt as _opsgenie
    from stackdiff.formatters import pagerduty_fmt as _pagerduty
    from stackdiff.formatters import prometheus_fmt as _prometheus
    from stackdiff.formatters import sonarqube_fmt as _sonarqube
    from stackdiff.formatters import sarif_fmt as _sarif
    from stackdiff.formatters import teamcity_fmt as _teamcity
    from stackdiff.formatters import splunk_fmt as _splunk
    from stackdiff.formatters import datadog_fmt as _datadog
    from stackdiff.formatters import grafana_fmt as _grafana
    from stackdiff.formatters import newrelic_fmt as _newrelic
    from stackdiff.formatters import webhook_fmt as _webhook
    from stackdiff.formatters import csv_summary_fmt as _csv_summary
    from stackdiff.formatters import junit_summary_fmt as _junit_summary
    from stackdiff.formatters import badge_fmt as _badge
    from stackdiff.formatters import timeline_fmt as _timeline

    register_formatter("text", _text.format_diff)
    register_formatter("json", _json.format_diff)
    register_formatter("yaml", _yaml.format_diff)
    register_formatter("html", _html.format_diff)
    register_formatter("csv", _csv.format_diff)
    register_formatter("markdown", _md.format_diff)
    register_formatter("table", _table.format_diff)
    register_formatter("xml", _xml.format_diff)
    register_formatter("toml", _toml.format_diff)
    register_formatter("dot", _dot.format_diff)
    register_formatter("junit", _junit.format_diff)
    register_formatter("github", _github.format_diff)
    register_formatter("color", _color.format_diff)
    register_formatter("slack", _slack.format_diff)
    register_formatter("opsgenie", _opsgenie.format_diff)
    register_formatter("pagerduty", _pagerduty.format_diff)
    register_formatter("prometheus", _prometheus.format_diff)
    register_formatter("sonarqube", _sonarqube.format_diff)
    register_formatter("sarif", _sarif.format_diff)
    register_formatter("teamcity", _teamcity.format_diff)
    register_formatter("splunk", _splunk.format_diff)
    register_formatter("datadog", _datadog.format_diff)
    register_formatter("grafana", _grafana.format_diff)
    register_formatter("newrelic", _newrelic.format_diff)
    register_formatter("webhook", _webhook.format_diff)
    register_formatter("csv-summary", _csv_summary.format_diff)
    register_formatter("junit-summary", _junit_summary.format_diff)
    register_formatter("badge", _badge.format_diff)
    register_formatter("timeline", _timeline.format_diff)


_register_builtins()
