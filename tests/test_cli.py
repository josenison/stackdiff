"""Tests for the stackdiff CLI entry point."""
import pytest
from unittest.mock import MagicMock, patch

from stackdiff.cli import build_parser, run
from stackdiff.providers.base import Resource, StackState
from stackdiff.diff import DiffResult, ResourceDiff, ChangeType


def _make_state(name, resources=None):
    state = StackState(name=name)
    for r in (resources or []):
        state.add(r)
    return state


def _empty_result():
    return DiffResult(diffs=[])


def _result_with_change():
    r = Resource(id="r1", type="Instance", attributes={})
    diff = ResourceDiff(resource=r, change_type=ChangeType.ADDED)
    return DiffResult(diffs=[diff])


@pytest.fixture()
def mock_provider():
    provider = MagicMock()
    provider.fetch_state.side_effect = lambda name: _make_state(name)
    return provider


class TestBuildParser:
    def test_required_args_present(self):
        parser = build_parser()
        args = parser.parse_args(
            ["--provider", "aws", "--source", "dev", "--target", "prod"]
        )
        assert args.provider == "aws"
        assert args.source == "dev"
        assert args.target == "prod"

    def test_default_format_is_text(self):
        parser = build_parser()
        args = parser.parse_args(
            ["--provider", "aws", "--source", "dev", "--target", "prod"]
        )
        assert args.fmt == "text"

    def test_exit_code_flag_defaults_false(self):
        parser = build_parser()
        args = parser.parse_args(
            ["--provider", "aws", "--source", "dev", "--target", "prod"]
        )
        assert args.exit_code is False


class TestRun:
    def test_returns_zero_when_no_changes(self, mock_provider):
        with patch("stackdiff.cli.get_provider", return_value=mock_provider), \
             patch("stackdiff.cli.compute_diff", return_value=_empty_result()):
            code = run(["--provider", "aws", "--source", "dev", "--target", "prod"])
        assert code == 0

    def test_returns_zero_with_changes_when_exit_code_not_set(self, mock_provider):
        with patch("stackdiff.cli.get_provider", return_value=mock_provider), \
             patch("stackdiff.cli.compute_diff", return_value=_result_with_change()):
            code = run(["--provider", "aws", "--source", "dev", "--target", "prod"])
        assert code == 0

    def test_returns_one_with_changes_when_exit_code_set(self, mock_provider):
        with patch("stackdiff.cli.get_provider", return_value=mock_provider), \
             patch("stackdiff.cli.compute_diff", return_value=_result_with_change()):
            code = run(
                ["--provider", "aws", "--source", "dev", "--target", "prod", "--exit-code"]
            )
        assert code == 1

    def test_json_format_accepted(self, mock_provider):
        with patch("stackdiff.cli.get_provider", return_value=mock_provider), \
             patch("stackdiff.cli.compute_diff", return_value=_empty_result()):
            code = run(
                ["--provider", "aws", "--source", "dev", "--target", "prod", "--format", "json"]
            )
        assert code == 0
