"""Registry integration tests for the terraform-plan formatter."""
from __future__ import annotations

import pytest

from stackdiff.formatters.registry import available_formatters, get_formatter
from stackdiff.diff import DiffResult


def _empty_result() -> DiffResult:
    return DiffResult(diffs=[])


class TestTerraformPlanFormatterRegistered:
    def test_terraform_plan_in_available(self):
        assert "terraform-plan" in available_formatters()

    def test_get_terraform_plan_formatter_returns_callable(self):
        fmt = get_formatter("terraform-plan")
        assert callable(fmt)

    def test_terraform_plan_formatter_produces_string(self):
        fmt = get_formatter("terraform-plan")
        out = fmt(_empty_result())
        assert isinstance(out, str)

    def test_terraform_plan_formatter_contains_header(self):
        fmt = get_formatter("terraform-plan")
        out = fmt(_empty_result())
        assert "Terraform plan-style diff" in out
