"""Provider registry for stackdiff."""

from typing import Dict, Type

from stackdiff.providers.aws import AWSProvider
from stackdiff.providers.gcp import GCPProvider
from stackdiff.providers.azure import AzureProvider
from stackdiff.providers.terraform import TerraformProvider

_REGISTRY: Dict[str, Type] = {
    "aws": AWSProvider,
    "gcp": GCPProvider,
    "azure": AzureProvider,
    "terraform": TerraformProvider,
}


def register(name: str, provider_class: Type) -> None:
    """Register a new provider under *name*."""
    _REGISTRY[name] = provider_class


def get_provider(name: str) -> Type:
    """Return the provider class for *name*.

    Raises:
        KeyError: if the provider is not registered.
    """
    if name not in _REGISTRY:
        raise KeyError(
            f"Unknown provider '{name}'. "
            f"Available providers: {', '.join(sorted(_REGISTRY))}"
        )
    return _REGISTRY[name]


def available_providers() -> list:
    """Return a sorted list of registered provider names."""
    return sorted(_REGISTRY.keys())
