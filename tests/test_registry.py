"""Unit tests for the provider registry."""
import pytest
from stackdiff.providers.registry import (
    get_provider,
    register,
    available_providers,
)
from stackdiff.providers.aws import AWSProvider
from stackdiff.providers.gcp import GCPProvider


class TestRegistry:
    def test_aws_provider_registered(self):
        assert "aws" in available_providers()

    def test_gcp_provider_registered(self):
        assert "gcp" in available_providers()

    def test_get_aws_provider_returns_correct_type(self):
        p = get_provider("aws", region="eu-west-1")
        assert isinstance(p, AWSProvider)

    def test_get_gcp_provider_returns_correct_type(self):
        p = get_provider("gcp", project="test-project")
        assert isinstance(p, GCPProvider)
        assert p.project == "test-project"

    def test_unknown_provider_raises_key_error(self):
        with pytest.raises(KeyError, match="Unknown provider 'azure'"):
            get_provider("azure")

    def test_error_message_lists_available_providers(self):
        with pytest.raises(KeyError) as exc_info:
            get_provider("nonexistent")
        assert "aws" in str(exc_info.value)
        assert "gcp" in str(exc_info.value)

    def test_custom_provider_registration(self):
        from stackdiff.providers.base import StackProvider, StackState

        class DummyProvider(StackProvider):
            @property
            def name(self):
                return "dummy"

            def fetch_state(self, stack_name: str) -> StackState:
                return StackState(stack_name=stack_name, resources=[])

        register("dummy", lambda **kw: DummyProvider())
        p = get_provider("dummy")
        assert isinstance(p, DummyProvider)
        assert "dummy" in available_providers()
