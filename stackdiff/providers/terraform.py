"""Terraform state file provider for stackdiff."""

import json
from pathlib import Path
from typing import Union

from stackdiff.providers.base import Resource, StackState


class TerraformProvider:
    """Reads infrastructure state from a Terraform state file (.tfstate)."""

    def __init__(self, state_file: Union[str, Path]) -> None:
        self._state_file = Path(state_file)

    @property
    def name(self) -> str:
        return "terraform"

    def fetch_state(self, stack_name: str) -> StackState:
        """Parse a .tfstate file and return a StackState.

        Args:
            stack_name: Logical name to assign to this state snapshot.

        Returns:
            StackState populated with resources found in the state file.
        """
        if not self._state_file.exists():
            raise FileNotFoundError(
                f"Terraform state file not found: {self._state_file}"
            )

        raw = json.loads(self._state_file.read_text(encoding="utf-8"))
        resources = {}

        for res in raw.get("resources", []):
            res_type = res.get("type", "unknown")
            res_name = res.get("name", "unnamed")
            provider = res.get("provider", "")

            for idx, instance in enumerate(res.get("instances", [])):
                attrs = instance.get("attributes", {})
                resource_id = attrs.get("id") or f"{res_type}.{res_name}[{idx}]"
                logical_id = f"{res_type}.{res_name}" if idx == 0 else f"{res_type}.{res_name}[{idx}]"

                resource = Resource(
                    id=resource_id,
                    type=res_type,
                    properties={
                        "name": res_name,
                        "provider": provider,
                        **attrs,
                    },
                )
                resources[logical_id] = resource

        return StackState(name=stack_name, resources=resources)
