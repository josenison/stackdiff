from typing import Optional
from googleapiclient import discovery
from .base import StackProvider, StackState, Resource


class GCPProvider(StackProvider):
    """Google Cloud Deployment Manager provider."""

    def __init__(self, project: str, credentials=None):
        self.project = project
        self._credentials = credentials
        self._client: Optional[object] = None

    @property
    def name(self) -> str:
        return "gcp"

    def _get_client(self):
        if self._client is None:
            self._client = discovery.build(
                "deploymentmanager",
                "v2",
                credentials=self._credentials,
            )
        return self._client

    def fetch_state(self, stack_name: str) -> StackState:
        """Fetch resources from a GCP Deployment Manager deployment."""
        client = self._get_client()
        resources = []
        try:
            resp = (
                client.resources()
                .list(project=self.project, deployment=stack_name)
                .execute()
            )
            for item in resp.get("resources", []):
                properties = item.get("properties", "{}")
                if isinstance(properties, str):
                    import json
                    try:
                        properties = json.loads(properties)
                    except ValueError:
                        properties = {"raw": properties}
                resources.append(
                    Resource(
                        id=item["name"],
                        type=item.get("type", "unknown"),
                        properties=properties,
                    )
                )
        except Exception as exc:  # pylint: disable=broad-except
            raise RuntimeError(
                f"Failed to fetch GCP deployment '{stack_name}' "
                f"in project '{self.project}': {exc}"
            ) from exc
        return StackState(stack_name=stack_name, resources=resources)
