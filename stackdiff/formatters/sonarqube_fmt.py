"""SonarQube generic issue format for stackdiff results."""
from __future__ import annotations
import json
from stackdiff.diff import DiffResult, ChangeType

_SEVERITY = {
    ChangeType.ADDED: "MINOR",
    ChangeType.REMOVED: "MAJOR",
    ChangeType.MODIFIED: "INFO",
}


def format_diff(result: DiffResult, **kwargs) -> str:
    """Return a SonarQube generic external issues JSON string."""
    issues = []
    for rd in result.diffs:
        if rd.change_type == ChangeType.UNCHANGED:
            continue
        severity = _SEVERITY.get(rd.change_type, "INFO")
        resource_id = getattr(rd.resource, "resource_id", str(rd.resource))
        resource_type = getattr(rd.resource, "resource_type", "unknown")
        message = (
            f"[{rd.change_type.value}] {resource_type} '{resource_id}'"
        )
        if rd.change_type == ChangeType.MODIFIED and rd.diff_detail:
            message += f": {rd.diff_detail}"
        issues.append({
            "engineId": "stackdiff",
            "ruleId": f"stackdiff:{rd.change_type.value.lower()}",
            "severity": severity,
            "type": "BUG" if rd.change_type == ChangeType.REMOVED else "CODE_SMELL",
            "primaryLocation": {
                "message": message,
                "filePath": kwargs.get("file_path", "infrastructure"),
            },
        })
    return json.dumps({"issues": issues}, indent=2)
