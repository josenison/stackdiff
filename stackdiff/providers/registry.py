"""Provider registry — maps provider names to factory callables."""
from __future__ import annotations

from typing import Callable, Dict, Type

from stackdiff.providers.base import StackProvider

_REGISTRY: Dict[str, Type[StackProvider]] = {}


def register(name: str, provider_cls: Type[StackProvider]) -> None:
    """Register *provider_cls* under *name*."""
    _REGISTRY[name] = provider_cls


def get_provider(name: str, **kwargs) -> StackProvider:  # type: ignore[return]
    """Instantiate and return the provider registered under *name*.

    Extra *kwargs* are forwarded to the provider constructor.

    Raises
    ------
    KeyError
        If *name* has not been registered.
    """
    if name not in _REGISTRY:
        raise KeyError(
            f"Unknown provider '{name}'. Available: {', '.join(available_providers())}"
        )
    return _REGISTRY[name](**kwargs)


def available_providers() -> list[str]:
    """Return the names of all registered providers."""
    return sorted(_REGISTRY.keys())


# ---------------------------------------------------------------------------
# Built-in provider registrations
# ---------------------------------------------------------------------------

from stackdiff.providers.aws import AWSProvider  # noqa: E402
from stackdiff.providers.gcp import GCPProvider  # noqa: E402
from stackdiff.providers.azure import AzureProvider  # noqa: E402

register("aws", AWSProvider)
register("gcp", GCPProvider)
register("azure", AzureProvider)
