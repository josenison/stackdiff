"""SARIF 2.1.0 formatter for stackdiff results."""
from __future__ import annotations

import json
from typing import Any

from stackdiff.diff import ChangeType, DiffResult

_LEVEL = {
    ChangeType.ADDED: "warning",
    ChangeType.REMOVED: "error",
    ChangeType.MODIFIED: "warning",
    ChangeType.UNCHANGED: "note",
}


def _make_result(rdiff: Any) -> dict:
    return {
        "ruleId": rdiff.change_type.value,
        "level": _LEVEL.get(rdiff.change_type, "note"),
        "message": {
            "text": (
                f"{rdiff.change_type.value}: {rdiff.resource_id} "
                f"(type={rdiff.resource_type})"
            )
        },
        "locations": [
            {
                "logicalLocations": [
                    {
                        "name": rdiff.resource_id,
                        "kind": rdiff.resource_type,
                    }
                ]
            }
        ],
    }


def format_diff(result: DiffResult) -> str:
    sarif: dict = {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "stackdiff",
                        "informationUri": "https://github.com/example/stackdiff",
                        "rules": [
                            {"id": ct.value} for ct in ChangeType
                        ],
                    }
                },
                "results": [
                    _make_result(d)
                    for d in result.diffs
                    if d.change_type != ChangeType.UNCHANGED
                ],
            }
        ],
    }
    return json.dumps(sarif, indent=2)
