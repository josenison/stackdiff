"""Unit tests for the Azure provider."""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from stackdiff.providers.azure import AzureProvider
from stackdiff.providers.base import StackState


def _make_azure_resource(
    rid: str,
    name: str,
    rtype: str,
    location: str = "eastus",
    stack_tag: str | None = "my-stack",
    sku=None,
    kind: str | None = None,
) -> SimpleNamespace:
    return SimpleNamespace(
        id=rid,
        name=name,
        type=rtype,
        location=location,
        tags={"stack": stack_tag} if stack_tag else {},
        sku=sku,
        kind=kind,
    )


@pytest.fixture()
def provider() -> AzureProvider:
    return AzureProvider(subscription_id="sub-123", resource_group="rg-prod")


@pytest.fixture()
def _mock_client(provider: AzureProvider):
    client = MagicMock()
    provider._client = client
    return client


class TestAzureProvider:
    def test_name(self, provider: AzureProvider) -> None:
        assert provider.name == "azure"

    def test_fetch_state_returns_stack_state(
        self, provider: AzureProvider, _mock_client: MagicMock
    ) -> None:
        _mock_client.resources.list_by_resource_group.return_value = [
            _make_azure_resource("id-1", "storage1", "Microsoft.Storage/storageAccounts"),
        ]
        state = provider.fetch_state("my-stack")
        assert isinstance(state, StackState)
        assert state.stack_name == "my-stack"
        assert state.provider == "azure"

    def test_fetch_state_filters_by_stack_tag(
        self, provider: AzureProvider, _mock_client: MagicMock
    ) -> None:
        _mock_client.resources.list_by_resource_group.return_value = [
            _make_azure_resource("id-1", "storage1", "Microsoft.Storage/storageAccounts", stack_tag="my-stack"),
            _make_azure_resource("id-2", "storage2", "Microsoft.Storage/storageAccounts", stack_tag="other-stack"),
            _make_azure_resource("id-3", "vm1", "Microsoft.Compute/virtualMachines", stack_tag=None),
        ]
        state = provider.fetch_state("my-stack")
        assert len(state.resources) == 1
        assert state.resources[0].name == "storage1"

    def test_fetch_state_resource_properties(
        self, provider: AzureProvider, _mock_client: MagicMock
    ) -> None:
        _mock_client.resources.list_by_resource_group.return_value = [
            _make_azure_resource(
                "id-1", "storage1", "Microsoft.Storage/storageAccounts",
                location="westeurope", kind="StorageV2",
            ),
        ]
        state = provider.fetch_state("my-stack")
        props = state.resources[0].properties
        assert props["location"] == "westeurope"
        assert props["kind"] == "StorageV2"

    def test_fetch_state_empty_when_no_matching_tags(
        self, provider: AzureProvider, _mock_client: MagicMock
    ) -> None:
        _mock_client.resources.list_by_resource_group.return_value = [
            _make_azure_resource("id-1", "vm1", "Microsoft.Compute/virtualMachines", stack_tag="other"),
        ]
        state = provider.fetch_state("my-stack")
        assert state.resources == []

    def test_azure_provider_in_registry(self) -> None:
        from stackdiff.providers.registry import available_providers
        assert "azure" in available_providers()
