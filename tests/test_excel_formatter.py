"""Tests for the Excel (XLSX) formatter."""
from __future__ import annotations

import io
import pytest

from stackdiff.diff import ChangeType, DiffResult, ResourceDiff
from stackdiff.providers.base import Resource

openpyxl = pytest.importorskip("openpyxl")

from stackdiff.formatters.excel_fmt import format_diff  # noqa: E402


def _res(rid: str, rtype: str = "Instance") -> Resource:
    return Resource(resource_id=rid, resource_type=rtype, properties={})


def _rdiff(
    change: ChangeType,
    a: Resource | None = None,
    b: Resource | None = None,
) -> ResourceDiff:
    return ResourceDiff(change_type=change, resource_a=a, resource_b=b)


def _make_result(*diffs: ResourceDiff) -> DiffResult:
    return DiffResult(diffs=list(diffs))


def _load_wb(raw: bytes):
    return openpyxl.load_workbook(io.BytesIO(raw))


class TestExcelFormatter:
    def test_no_changes_returns_bytes(self):
        result = _make_result()
        raw = format_diff(result)
        assert isinstance(raw, bytes)
        assert len(raw) > 0

    def test_no_changes_has_only_header_row(self):
        result = _make_result()
        wb = _load_wb(format_diff(result))
        ws = wb.active
        assert ws.max_row == 1

    def test_header_row_contains_expected_columns(self):
        result = _make_result()
        wb = _load_wb(format_diff(result))
        ws = wb.active
        headers = [ws.cell(row=1, column=i).value for i in range(1, 6)]
        assert headers == ["Resource ID", "Resource Type", "Change Type", "Environment A", "Environment B"]

    def test_added_resource_appears_in_second_row(self):
        r = _res("i-001", "EC2Instance")
        result = _make_result(_rdiff(ChangeType.ADDED, b=r))
        wb = _load_wb(format_diff(result))
        ws = wb.active
        assert ws.max_row == 2
        assert ws.cell(row=2, column=1).value == "i-001"
        assert ws.cell(row=2, column=2).value == "EC2Instance"
        assert ws.cell(row=2, column=3).value == "added"

    def test_removed_resource_change_type_cell(self):
        r = _res("bucket-1", "S3Bucket")
        result = _make_result(_rdiff(ChangeType.REMOVED, a=r))
        wb = _load_wb(format_diff(result))
        ws = wb.active
        assert ws.cell(row=2, column=3).value == "removed"
        assert ws.cell(row=2, column=4).value == "bucket-1"
        assert ws.cell(row=2, column=5).value == ""

    def test_multiple_diffs_produce_correct_row_count(self):
        diffs = [
            _rdiff(ChangeType.ADDED, b=_res(f"res-{i}")) for i in range(5)
        ]
        result = _make_result(*diffs)
        wb = _load_wb(format_diff(result))
        ws = wb.active
        assert ws.max_row == 6  # 1 header + 5 data

    def test_worksheet_title_is_stackdiff(self):
        result = _make_result()
        wb = _load_wb(format_diff(result))
        assert wb.active.title == "StackDiff"
