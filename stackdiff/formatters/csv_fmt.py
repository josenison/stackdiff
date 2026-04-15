"""CSV formatter for diff results."""

import csv
import io
from ..diff import DiffResult, ChangeType


def format_diff(result: DiffResult, stack_a: str = "stack-a", stack_b: str = "stack-b") -> str:
    """Format a DiffResult as a CSV string.

    Columns: resource_id, resource_type, change_type, stack_a_value, stack_b_value
    """
    output = io.StringIO()
    writer = csv.writer(output, lineterminator="\n")

    writer.writerow(["resource_id", "resource_type", "change_type", stack_a, stack_b])

    if not result.has_changes():
        return output.getvalue()

    for rdiff in result.changes:
        change_label = rdiff.change_type.value

        if rdiff.change_type == ChangeType.ADDED:
            writer.writerow([
                rdiff.resource_b.resource_id,
                rdiff.resource_b.resource_type,
                change_label,
                "",
                rdiff.resource_b.resource_id,
            ])
        elif rdiff.change_type == ChangeType.REMOVED:
            writer.writerow([
                rdiff.resource_a.resource_id,
                rdiff.resource_a.resource_type,
                change_label,
                rdiff.resource_a.resource_id,
                "",
            ])
        elif rdiff.change_type == ChangeType.MODIFIED:
            a_attrs = str(rdiff.resource_a.attributes)
            b_attrs = str(rdiff.resource_b.attributes)
            writer.writerow([
                rdiff.resource_a.resource_id,
                rdiff.resource_a.resource_type,
                change_label,
                a_attrs,
                b_attrs,
            ])
        else:
            writer.writerow([
                rdiff.resource_a.resource_id,
                rdiff.resource_a.resource_type,
                change_label,
                rdiff.resource_a.resource_id,
                rdiff.resource_b.resource_id,
            ])

    return output.getvalue()
