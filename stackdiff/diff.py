"""Core diffing logic — compares two StackState objects and reports differences."""

from dataclasses import dataclass, field
from enum import Enum

from stackdiff.providers.base import Resource, StackState


class ChangeType(str, Enum):
    ADDED = "added"
    REMOVED = "removed"
    MODIFIED = "modified"
    UNCHANGED = "unchanged"


@dataclass
class ResourceDiff:
    key: str
    change_type: ChangeType
    source: Resource | None = None
    target: Resource | None = None
    changed_fields: list[str] = field(default_factory=list)


@dataclass
class DiffResult:
    source_env: str
    target_env: str
    diffs: list[ResourceDiff] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return any(d.change_type != ChangeType.UNCHANGED for d in self.diffs)

    def summary(self) -> dict[str, int]:
        counts: dict[str, int] = {ct.value: 0 for ct in ChangeType}
        for d in self.diffs:
            counts[d.change_type.value] += 1
        return counts


DIFFED_FIELDS = ("status", "region", "properties", "tags")


def diff_states(source: StackState, target: StackState) -> DiffResult:
    """Compare two StackState objects and return a DiffResult."""
    result = DiffResult(source_env=source.environment, target_env=target.environment)

    src_map = source.resource_map()
    tgt_map = target.resource_map()

    all_keys = set(src_map) | set(tgt_map)

    for key in sorted(all_keys):
        src_res = src_map.get(key)
        tgt_res = tgt_map.get(key)

        if src_res is None:
            result.diffs.append(ResourceDiff(key=key, change_type=ChangeType.ADDED, target=tgt_res))
        elif tgt_res is None:
            result.diffs.append(ResourceDiff(key=key, change_type=ChangeType.REMOVED, source=src_res))
        else:
            changed = [f for f in DIFFED_FIELDS if getattr(src_res, f) != getattr(tgt_res, f)]
            change_type = ChangeType.MODIFIED if changed else ChangeType.UNCHANGED
            result.diffs.append(
                ResourceDiff(key=key, change_type=change_type, source=src_res, target=tgt_res, changed_fields=changed)
            )

    return result
