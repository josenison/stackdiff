"""AWS provider — fetches CloudFormation stack resources as StackState."""

from __future__ import annotations

from typing import Any

try:
    import boto3
except ImportError as exc:  # pragma: no cover
    raise ImportError("boto3 is required for the AWS provider: pip install boto3") from exc

from stackdiff.providers.base import BaseProvider, Resource, StackState


class AWSProvider(BaseProvider):
    """Retrieves stack state from AWS CloudFormation."""

    def __init__(self, profile: str | None = None) -> None:
        self._profile = profile

    @property
    def name(self) -> str:
        return "aws"

    def fetch_state(self, environment: str, **kwargs: Any) -> StackState:
        """Fetch all resources in the named CloudFormation stack.

        Args:
            environment: The CloudFormation stack name to inspect.
            region: AWS region (optional, falls back to boto3 default).
        """
        region: str | None = kwargs.get("region")
        session = boto3.Session(profile_name=self._profile, region_name=region)
        cf = session.client("cloudformation")

        paginator = cf.get_paginator("list_stack_resources")
        resources: list[Resource] = []

        for page in paginator.paginate(StackName=environment):
            for item in page.get("StackResourceSummaries", []):
                resources.append(
                    Resource(
                        id=item.get("PhysicalResourceId", ""),
                        name=item["LogicalResourceId"],
                        type=item["ResourceType"],
                        region=region or "us-east-1",
                        status=item["ResourceStatus"],
                        properties={},
                        tags={},
                    )
                )

        return StackState(environment=environment, provider=self.name, resources=resources)
