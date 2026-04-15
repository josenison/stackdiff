"""Base provider interface for cloud infrastructure state retrieval."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Resource:
    """Represents a single cloud resource."""

    id: str
    name: str
    type: str
    region: str
    status: str
    properties: dict[str, Any] = field(default_factory=dict)
    tags: dict[str, str] = field(default_factory=dict)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Resource):
            return NotImplemented
        return self.id == other.id and self.type == other.type

    def __hash__(self) -> int:
        return hash((self.id, self.type))


@dataclass
class StackState:
    """Represents the full state of a deployed stack in an environment."""

    environment: str
    provider: str
    resources: list[Resource] = field(default_factory=list)

    def resource_map(self) -> dict[str, Resource]:
        """Return resources keyed by (type, name) for easy lookup."""
        return {f"{r.type}::{r.name}": r for r in self.resources}


class BaseProvider(ABC):
    """Abstract base class all cloud providers must implement."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider identifier (e.g. 'aws', 'gcp')."""

    @abstractmethod
    def fetch_state(self, environment: str, **kwargs: Any) -> StackState:
        """Fetch current infrastructure state for the given environment."""
