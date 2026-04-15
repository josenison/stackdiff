"""Tests for stackdiff.diff — core diffing logic."""

import pytest

from stackdiff.diff import ChangeType, diff_states
from stackdiff.providers.base import Resource, StackState


def _resource(name: str, rtype: str = "AWS::S3::Bucket", status: str = "CREATE_COMPLETE") -> Resource:
    return Resource(id=f"id-{name}", name=name, type=rtype, region="us-east-1", status=status)


def _state(env: str, resources: list[Resource]) -> StackState:
    return StackState(environment=env, provider="aws", resources=resources)


class TestDiffStates:
    def test_identical_stacks_produce_no_changes(self):
        r = _resource("MyBucket")
        result = diff_states(_state("staging", [r]), _state("prod", [r]))
        assert not result.has_changes
        assert result.summary()["unchanged"] == 1

    def test_added_resource_detected(self):
        src = _state("staging", [])
        tgt = _state("prod", [_resource("NewBucket")])
        result = diff_states(src, tgt)
        assert result.has_changes
        added = [d for d in result.diffs if d.change_type == ChangeType.ADDED]
        assert len(added) == 1
        assert added[0].key == "AWS::S3::Bucket::NewBucket"

    def test_removed_resource_detected(self):
        src = _state("staging", [_resource("OldBucket")])
        tgt = _state("prod", [])
        result = diff_states(src, tgt)
        removed = [d for d in result.diffs if d.change_type == ChangeType.REMOVED]
        assert len(removed) == 1

    def test_modified_status_detected(self):
        src_r = _resource("MyBucket", status="CREATE_COMPLETE")
        tgt_r = _resource("MyBucket", status="UPDATE_COMPLETE")
        result = diff_states(_state("staging", [src_r]), _state("prod", [tgt_r]))
        modified = [d for d in result.diffs if d.change_type == ChangeType.MODIFIED]
        assert len(modified) == 1
        assert "status" in modified[0].changed_fields

    def test_summary_counts_all_categories(self):
        common = _resource("Kept")
        only_src = _resource("Gone")
        only_tgt = _resource("New")
        src = _state("staging", [common, only_src])
        tgt = _state("prod", [common, only_tgt])
        summary = diff_states(src, tgt).summary()
        assert summary["unchanged"] == 1
        assert summary["removed"] == 1
        assert summary["added"] == 1

    def test_result_env_names_preserved(self):
        result = diff_states(_state("dev", []), _state("prod", []))
        assert result.source_env == "dev"
        assert result.target_env == "prod"
