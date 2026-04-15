"""Provider registry — maps provider names to their factory functions."""
from typing import Callable, Dict
from .base import StackProvider
from .aws import AWSProvider
from .gcp import GCPProvider

# Registry maps provider name -> callable(**kwargs) -> StackProvider
_REGISTRY: Dict[str, Callable[..., StackProvider]] = {}


def register(name: str, factory: Callable[..., StackProvider]) -> None:
    """Register a provider factory under *name*."""
    _REGISTRY[name] = factory


def get_provider(name: str, **kwargs) -> StackProvider:
    """Instantiate a registered provider by name.

    Raises
    ------
    KeyError
        If *name* is not registered.
    """
    if name not in _REGISTRY:
        available = ", ".join(sorted(_REGISTRY))
        raise KeyError(
            f"Unknown provider '{name}'. Available providers: {available}"
        )
    return _REGISTRY[name](**kwargs)


def available_providers():
    """Return a sorted list of registered provider names."""
    return sorted(_REGISTRY.keys())


# ── built-in registrations ──────────────────────────────────────────────────
register("aws", lambda **kw: AWSProvider(
    region=kw.get("region", "us-east-1"),
    profile=kw.get("profile"),
))

register("gcp", lambda **kw: GCPProvider(
    project=kw["project"],
    credentials=kw.get("credentials"),
))
