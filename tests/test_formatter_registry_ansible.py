"""Verify the Ansible formatter is registered and callable."""
from __future__ import annotations

import json

from stackdiff.diff import DiffResult
from stackdiff.formatters.registry import available_formatters, get_formatter


def _empty_result() -> DiffResult:
    return DiffResult(diffs=[])


class TestAnsibleFormatterRegistered:
    def test_ansible_in_available(self):
        assert "ansible" in available_formatters()

    def test_get_ansible_formatter_returns_callable(self):
        fmt = get_formatter("ansible")
        assert callable(fmt)

    def test_ansible_formatter_produces_json(self):
        fmt = get_formatter("ansible")
        output = fmt(_empty_result())
        parsed = json.loads(output)
        assert "stackdiff" in parsed
        assert "changed" in parsed

    def test_ansible_formatter_no_changes_not_changed(self):
        fmt = get_formatter("ansible")
        output = fmt(_empty_result())
        parsed = json.loads(output)
        assert parsed["changed"] is False
