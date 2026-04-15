"""Unit tests for the GCP Deployment Manager provider."""
from unittest.mock import MagicMock, patch
import json
import pytest
from stackdiff.providers.gcp import GCPProvider


def _make_resource(name: str, rtype: str, props: dict) -> dict:
    return {"name": name, "type": rtype, "properties": json.dumps(props)}


@pytest.fixture()
def provider():
    return GCPProvider(project="my-project")


def _mock_client(resources):
    """Build a mock Discovery client that returns *resources*."""
    mock_list = MagicMock()
    mock_list.execute.return_value = {"resources": resources}
    mock_resources = MagicMock()
    mock_resources.list.return_value = mock_list
    client = MagicMock()
    client.resources.return_value = mock_resources
    return client


class TestGCPProvider:
    def test_name(self, provider):
        assert provider.name == "gcp"

    def test_fetch_state_returns_stack_state(self, provider):
        raw = [_make_resource("vm-1", "compute.v1.instance", {"zone": "us-central1-a"})]
        provider._client = _mock_client(raw)
        state = provider.fetch_state("my-deployment")
        assert state.stack_name == "my-deployment"
        assert len(state.resources) == 1
        r = state.resources[0]
        assert r.id == "vm-1"
        assert r.type == "compute.v1.instance"
        assert r.properties["zone"] == "us-central1-a"

    def test_empty_deployment(self, provider):
        provider._client = _mock_client([])
        state = provider.fetch_state("empty-deployment")
        assert state.resources == []

    def test_api_error_raises_runtime_error(self, provider):
        mock_list = MagicMock()
        mock_list.execute.side_effect = Exception("403 Forbidden")
        mock_resources = MagicMock()
        mock_resources.list.return_value = mock_list
        client = MagicMock()
        client.resources.return_value = mock_resources
        provider._client = client
        with pytest.raises(RuntimeError, match="Failed to fetch GCP deployment"):
            provider.fetch_state("bad-deployment")

    def test_resource_map_keyed_by_id(self, provider):
        raw = [
            _make_resource("bucket-a", "storage.v1.bucket", {}),
            _make_resource("bucket-b", "storage.v1.bucket", {}),
        ]
        provider._client = _mock_client(raw)
        state = provider.fetch_state("my-deployment")
        rmap = state.resource_map()
        assert set(rmap.keys()) == {"bucket-a", "bucket-b"}
