"""Formatter registry — maps format names to callable formatters."""
from __future__ import annotations

from typing import Callable

from stackdiff.diff import DiffResult

FormatterFn = Callable[[DiffResult], str]

_registry: dict[str, FormatterFn] = {}
_builtins_registered = False


def register_formatter(name: str, fn: FormatterFn) -> None:
    """Register a formatter under *name*."""
    _registry[name] = fn


def get_formatter(name: str) -> FormatterFn:
    """Return the formatter registered under *name*.

    Raises KeyError if no formatter is found.
    """
    _ensure_builtins()
    if name not in _registry:
        available = ", ".join(sorted(_registry))
        raise KeyError(
            f"Unknown formatter {name!r}. Available: {available}"
        )
    return _registry[name]


def available_formatters() -> list[str]:
    """Return a sorted list of all registered formatter names."""
    _ensure_builtins()
    return sorted(_registry)


def _ensure_builtins() -> None:
    global _builtins_registered
    if not _builtins_registered:
        _register_builtins()
        _builtins_registered = True


def _register_builtins() -> None:  # noqa: PLR0915
    from stackdiff.formatters.text import format_diff as text_fmt
    from stackdiff.formatters.json_fmt import format_diff_to_str as json_fmt
    from stackdiff.formatters.yaml_fmt import format_diff as yaml_fmt
    from stackdiff.formatters.html_fmt import format_diff as html_fmt
    from stackdiff.formatters.csv_fmt import format_diff as csv_fmt
    from stackdiff.formatters.markdown_fmt import format_diff as md_fmt
    from stackdiff.formatters.table_fmt import format_diff as table_fmt
    from stackdiff.formatters.xml_fmt import format_diff as xml_fmt
    from stackdiff.formatters.toml_fmt import format_diff as toml_fmt
    from stackdiff.formatters.dot_fmt import format_diff as dot_fmt
    from stackdiff.formatters.junit_fmt import format_diff as junit_fmt
    from stackdiff.formatters.github_fmt import format_diff as github_fmt
    from stackdiff.formatters.color_fmt import format_diff as color_fmt
    from stackdiff.formatters.slack_fmt import format_diff as slack_fmt
    from stackdiff.formatters.opsgenie_fmt import format_diff as opsgenie_fmt
    from stackdiff.formatters.pagerduty_fmt import format_diff as pagerduty_fmt
    from stackdiff.formatters.prometheus_fmt import format_diff as prometheus_fmt
    from stackdiff.formatters.sonarqube_fmt import format_diff as sonarqube_fmt
    from stackdiff.formatters.sarif_fmt import format_diff as sarif_fmt
    from stackdiff.formatters.teamcity_fmt import format_diff as teamcity_fmt
    from stackdiff.formatters.splunk_fmt import format_diff as splunk_fmt
    from stackdiff.formatters.datadog_fmt import format_diff as datadog_fmt
    from stackdiff.formatters.grafana_fmt import format_diff as grafana_fmt
    from stackdiff.formatters.newrelic_fmt import format_diff as newrelic_fmt
    from stackdiff.formatters.webhook_fmt import format_diff as webhook_fmt
    from stackdiff.formatters.csv_summary_fmt import format_diff as csv_summary_fmt
    from stackdiff.formatters.junit_summary_fmt import format_diff as junit_summary_fmt
    from stackdiff.formatters.badge_fmt import format_diff as badge_fmt
    from stackdiff.formatters.timeline_fmt import format_diff as timeline_fmt
    from stackdiff.formatters.ndjson_fmt import format_diff as ndjson_fmt
    from stackdiff.formatters.excel_fmt import format_diff as excel_fmt
    from stackdiff.formatters.mermaid_fmt import format_diff as mermaid_fmt
    from stackdiff.formatters.ansible_fmt import format_diff as ansible_fmt
    from stackdiff.formatters.tap_fmt import format_diff as tap_fmt
    from stackdiff.formatters.checkstyle_fmt import format_diff as checkstyle_fmt
    from stackdiff.formatters.terraform_plan_fmt import format_diff as terraform_plan_fmt
    from stackdiff.formatters.cdktf_fmt import format_diff as cdktf_fmt
    from stackdiff.formatters.pulumi_fmt import format_diff as pulumi_fmt
    from stackdiff.formatters.cloudformation_fmt import format_diff as cfn_fmt
    from stackdiff.formatters.shortlog_fmt import format_diff as shortlog_fmt
    from stackdiff.formatters.html_summary_fmt import format_diff as html_summary_fmt
    from stackdiff.formatters.graphml_fmt import format_diff as graphml_fmt
    from stackdiff.formatters.diff_stat_fmt import format_diff as diff_stat_fmt

    _registry.update({
        "text": text_fmt,
        "json": json_fmt,
        "yaml": yaml_fmt,
        "html": html_fmt,
        "csv": csv_fmt,
        "markdown": md_fmt,
        "table": table_fmt,
        "xml": xml_fmt,
        "toml": toml_fmt,
        "dot": dot_fmt,
        "junit": junit_fmt,
        "github": github_fmt,
        "color": color_fmt,
        "slack": slack_fmt,
        "opsgenie": opsgenie_fmt,
        "pagerduty": pagerduty_fmt,
        "prometheus": prometheus_fmt,
        "sonarqube": sonarqube_fmt,
        "sarif": sarif_fmt,
        "teamcity": teamcity_fmt,
        "splunk": splunk_fmt,
        "datadog": datadog_fmt,
        "grafana": grafana_fmt,
        "newrelic": newrelic_fmt,
        "webhook": webhook_fmt,
        "csv-summary": csv_summary_fmt,
        "junit-summary": junit_summary_fmt,
        "badge": badge_fmt,
        "timeline": timeline_fmt,
        "ndjson": ndjson_fmt,
        "excel": excel_fmt,
        "mermaid": mermaid_fmt,
        "ansible": ansible_fmt,
        "tap": tap_fmt,
        "checkstyle": checkstyle_fmt,
        "terraform-plan": terraform_plan_fmt,
        "cdktf": cdktf_fmt,
        "pulumi": pulumi_fmt,
        "cloudformation": cfn_fmt,
        "shortlog": shortlog_fmt,
        "html-summary": html_summary_fmt,
        "graphml": graphml_fmt,
        "diff-stat": diff_stat_fmt,
    })
