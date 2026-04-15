from __future__ import annotations

from typing import Any

from stackdiff.providers.base import Resource, StackProvider, StackState


class AzureProvider(StackProvider):
    """Fetch stack state from Azure Resource Manager."""

    def __init__(self, subscription_id: str, resource_group: str) -> None:
        self._subscription_id = subscription_id
        self._resource_group = resource_group
        self._client: Any = None

    @property
    def name(self) -> str:
        return "azure"

    def _get_client(self) -> Any:
        """Lazily initialise the Azure ResourceManagementClient."""
        if self._client is None:
            try:
                from azure.identity import DefaultAzureCredential
                from azure.mgmt.resource import ResourceManagementClient
            except ImportError as exc:  # pragma: no cover
                raise ImportError(
                    "azure-mgmt-resource and azure-identity are required for the "
                    "Azure provider. Install them with: pip install stackdiff[azure]"
                ) from exc

            credential = DefaultAzureCredential()
            self._client = ResourceManagementClient(credential, self._subscription_id)
        return self._client

    def fetch_state(self, stack_name: str) -> StackState:
        """Return a StackState for all resources in *resource_group* tagged with *stack_name*."""
        client = self._get_client()
        resources: list[Resource] = []

        for item in client.resources.list_by_resource_group(self._resource_group):
            tags = item.tags or {}
            if tags.get("stack") != stack_name:
                continue
            resource = Resource(
                id=item.id,
                type=item.type,
                name=item.name,
                properties={
                    "location": item.location,
                    "kind": getattr(item, "kind", None),
                    "sku": str(item.sku) if getattr(item, "sku", None) else None,
                },
            )
            resources.append(resource)

        return StackState(provider=self.name, stack_name=stack_name, resources=resources)
