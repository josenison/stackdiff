"""Tests for the provider registry."""

import pytest

from stackdiff.providers.registry import register, get_provider, available_providers
from stackdiff.providers.aws import AWSProvider
from stackdiff.providers.gcp import GCPProvider
from stackdiff.providers.azure import AzureProvider
from stackdiff.providers.terraform import TerraformProvider


class TestRegistry:
    def test_aws_provider_registered(self):
        assert "aws" in available_providers()

    def test_gcp_provider_registered(self):
        assert "gcp" in available_providers()

    def test_azure_provider_registered(self):
        assert "azure" in available_providers()

    def test_terraform_provider_registered(self):
        assert "terraform" in available_providers()

    def test_get_aws_provider_returns_correct_type(self):
        cls = get_provider("aws")
        assert cls is AWSProvider

    def test_get_gcp_provider_returns_correct_type(self):
        cls = get_provider("gcp")
        assert cls is GCPProvider

    def test_get_azure_provider_returns_correct_type(self):
        cls = get_provider("azure")
        assert cls is AzureProvider

    def test_get_terraform_provider_returns_correct_type(self):
        cls = get_provider("terraform")
        assert cls is TerraformProvider

    def test_unknown_provider_raises_key_error(self):
        with pytest.raises(KeyError, match="unknown_cloud"):
            get_provider("unknown_cloud")

    def test_error_message_lists_available_providers(self):
        with pytest.raises(KeyError, match="aws"):
            get_provider("bogus")

    def test_available_providers_returns_sorted_list(self):
        providers = available_providers()
        assert providers == sorted(providers)

    def test_register_custom_provider(self):
        class MyProvider:
            pass

        register("myprovider", MyProvider)
        assert get_provider("myprovider") is MyProvider
        assert "myprovider" in available_providers()
