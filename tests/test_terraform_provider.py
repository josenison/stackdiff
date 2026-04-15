"""Tests for the Terraform state file provider."""

import json
import pytest
from pathlib import Path

from stackdiff.providers.terraform import TerraformProvider
from stackdiff.providers.base import StackState


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_state(tmp_path: Path, data: dict) -> Path:
    p = tmp_path / "terraform.tfstate"
    p.write_text(json.dumps(data), encoding="utf-8")
    return p


_SAMPLE_STATE = {
    "version": 4,
    "resources": [
        {
            "type": "aws_instance",
            "name": "web",
            "provider": "provider[\"registry.terraform.io/hashicorp/aws\"]",
            "instances": [
                {
                    "attributes": {
                        "id": "i-0abc123",
                        "instance_type": "t3.micro",
                        "ami": "ami-0deadbeef",
                    }
                }
            ],
        },
        {
            "type": "aws_s3_bucket",
            "name": "assets",
            "provider": "provider[\"registry.terraform.io/hashicorp/aws\"]",
            "instances": [
                {"attributes": {"id": "my-assets-bucket", "region": "us-east-1"}}
            ],
        },
    ],
}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestTerraformProvider:
    def test_name(self, tmp_path):
        provider = TerraformProvider(tmp_path / "fake.tfstate")
        assert provider.name == "terraform"

    def test_fetch_state_returns_stack_state(self, tmp_path):
        state_file = _write_state(tmp_path, _SAMPLE_STATE)
        provider = TerraformProvider(state_file)
        result = provider.fetch_state("prod")
        assert isinstance(result, StackState)
        assert result.name == "prod"

    def test_resources_parsed_correctly(self, tmp_path):
        state_file = _write_state(tmp_path, _SAMPLE_STATE)
        provider = TerraformProvider(state_file)
        result = provider.fetch_state("prod")
        assert "aws_instance.web" in result.resources
        assert "aws_s3_bucket.assets" in result.resources

    def test_resource_properties_populated(self, tmp_path):
        state_file = _write_state(tmp_path, _SAMPLE_STATE)
        provider = TerraformProvider(state_file)
        result = provider.fetch_state("prod")
        instance = result.resources["aws_instance.web"]
        assert instance.id == "i-0abc123"
        assert instance.type == "aws_instance"
        assert instance.properties["instance_type"] == "t3.micro"

    def test_empty_state_file(self, tmp_path):
        state_file = _write_state(tmp_path, {"version": 4, "resources": []})
        provider = TerraformProvider(state_file)
        result = provider.fetch_state("empty")
        assert result.resources == {}

    def test_missing_file_raises(self, tmp_path):
        provider = TerraformProvider(tmp_path / "nonexistent.tfstate")
        with pytest.raises(FileNotFoundError, match="nonexistent.tfstate"):
            provider.fetch_state("prod")

    def test_multiple_instances_get_indexed_keys(self, tmp_path):
        state = {
            "resources": [
                {
                    "type": "aws_instance",
                    "name": "worker",
                    "provider": "",
                    "instances": [
                        {"attributes": {"id": "i-aaa"}},
                        {"attributes": {"id": "i-bbb"}},
                    ],
                }
            ]
        }
        state_file = _write_state(tmp_path, state)
        provider = TerraformProvider(state_file)
        result = provider.fetch_state("multi")
        assert "aws_instance.worker" in result.resources
        assert "aws_instance.worker[1]" in result.resources
