from __future__ import annotations

import unittest

from jobintel.sheets_sync import (
    APPLICATION_TAB,
    APPLICATION_HEADERS,
    HISTORY_TAB,
    SYSTEM_COLUMNS,
    SheetsSyncError,
    build_batch_requests,
    build_export,
    build_setup_requests,
    build_sync_plan,
    literal_cell_data,
    observe_workbook,
    verify_sync_plan,
)


def source() -> dict:
    return {
        "schema_version": 1,
        "source_revision": 7,
        "applications": [{
            "application_id": "app-1", "vacancy_id": "vac-1", "directory": "job-a",
            "company": "=Safe literal", "title": "Backend Engineer", "status": "applied",
            "effective_at": None, "recorded_at": "2026-09-21T10:00:00Z",
            "status_effective_at": None, "status_recorded_at": "2026-09-21T10:00:00Z",
            "source_revision": 4, "location": "Italy",
        }],
        "events": [{"event_id": "event-1", "application_id": "app-1", "vacancy_id": "vac-1", "status": "applied"}],
        "coverage": {"earliest_known_application": None},
    }


def observed(rows: list[dict]) -> dict:
    return {"schema_version": 1, "sheet_revision": "revision-1", "headers": list(APPLICATION_HEADERS), "rows": rows}


class SheetsSyncTests(unittest.TestCase):
    def test_observation_preserves_append_space_for_unknown_cells(self) -> None:
        metadata = {"sheets": [{"properties": {"title": title, "gridProperties": {"rowCount": 1000, "columnCount": 28}}} for title in (APPLICATION_TAB, HISTORY_TAB)]}
        ranges = [f"'{title}'!A1:AB1000" for title in (APPLICATION_TAB, HISTORY_TAB)]
        cells = {"sheets": [{"properties": {"title": title}, "data": [{"rowData": [
            {"values": [literal_cell_data("application_id"), {}]}, {},
            {"values": [{}, literal_cell_data("unlabelled manual note")]},
        ]}]} for title in (APPLICATION_TAB, HISTORY_TAB)]}
        result = observe_workbook(metadata, cells, requested_ranges=ranges)
        self.assertEqual(4, result["next_row"])
        self.assertEqual(["application_id"], result["headers"])
        self.assertEqual(4, result["history"]["next_row"])
        with self.assertRaises(SheetsSyncError):
            observe_workbook(metadata, cells, requested_ranges=[item.replace("1000", "10") for item in ranges])
        cells["sheets"][0]["data"][0]["startRow"] = 2
        with self.assertRaises(SheetsSyncError):
            observe_workbook(metadata, cells, requested_ranges=ranges)

    def test_export_is_canonical_and_hashed(self) -> None:
        exported = build_export(source())
        self.assertTrue(exported["payload_sha256"].startswith("sha256:"))
        self.assertEqual("app-1", exported["applications"][0]["application_id"])

    def test_plan_inserts_by_id_and_never_includes_manual_columns(self) -> None:
        plan = build_sync_plan(source(), observed([]))
        operation = plan["operations"][0]
        self.assertEqual("insert", operation["kind"])
        self.assertNotIn("my_notes", operation["cells"])
        self.assertEqual("=Safe literal", operation["cells"]["company"])

    def test_plan_is_safe_after_row_sorting(self) -> None:
        plan = build_sync_plan(source(), observed([{
            "row_index": 99,
            "cells": {"application_id": "app-1", "source_revision": "3", "company": "old", "my_notes": "keep"},
        }]))
        self.assertEqual("update", plan["operations"][0]["kind"])
        self.assertEqual(99, plan["operations"][0]["row_index"])
        self.assertNotIn("my_notes", plan["operations"][0]["cells"])

    def test_newer_observed_revision_is_a_conflict(self) -> None:
        plan = build_sync_plan(source(), observed([{
            "row_index": 2, "cells": {"application_id": "app-1", "source_revision": "5"},
        }]))
        self.assertEqual("observed_revision_newer", plan["conflicts"][0]["reason"])

    def test_duplicate_ids_fail_closed(self) -> None:
        with self.assertRaises(SheetsSyncError):
            build_sync_plan(source(), observed([
                {"row_index": 2, "cells": {"application_id": "app-1", "source_revision": "4"}},
                {"row_index": 3, "cells": {"application_id": "app-1", "source_revision": "4"}},
            ]))

    def test_noop_does_not_change_sync_timestamp(self) -> None:
        exported = build_export(source())
        expected = build_sync_plan(exported, observed([]))["operations"][0]["cells"]
        plan = build_sync_plan(exported, observed([{"row_index": 2, "cells": expected}]))
        self.assertEqual("noop", plan["operations"][0]["kind"])

    def test_global_export_revision_change_alone_is_a_noop(self) -> None:
        exported = build_export(source())
        row = build_sync_plan(exported, observed([]))["operations"][0]["cells"]
        changed_export = source()
        changed_export["source_revision"] = 8
        plan = build_sync_plan(changed_export, observed([{"row_index": 2, "cells": row}]))
        self.assertEqual("noop", plan["operations"][0]["kind"])

    def test_moved_header_and_same_revision_data_mismatch_fail_closed(self) -> None:
        shifted = observed([])
        shifted["headers"][0], shifted["headers"][1] = shifted["headers"][1], shifted["headers"][0]
        with self.assertRaises(SheetsSyncError):
            build_sync_plan(source(), shifted)
        plan = build_sync_plan(source(), observed([{"row_index": 2, "cells": {"application_id": "app-1", "source_revision": "4", "company": "manual edit"}}]))
        self.assertEqual("same_revision_data_mismatch", plan["conflicts"][0]["reason"])

    def test_readback_is_separate_and_detects_mismatch(self) -> None:
        plan = build_sync_plan(source(), observed([]))
        after = dict(plan["operations"][0]["cells"])
        after["company"] = "wrong"
        history = {"schema_version": 1, "headers": ["event_id", "application_id", "vacancy_id", "status", "effective_at", "recorded_at", "reason", "note"], "rows": [{"row_index": 2, "cells": plan["history_operations"][0]["cells"]}]}
        report = verify_sync_plan(plan, {**observed([{"row_index": 2, "cells": after}]), "history": history})
        self.assertFalse(report["verified"])
        self.assertEqual("company", report["failures"][0]["column"])

    def test_readback_requires_exact_history_and_rejects_duplicate_application_ids(self) -> None:
        plan = build_sync_plan(source(), observed([]))
        after = dict(plan["operations"][0]["cells"])
        with self.assertRaises(SheetsSyncError):
            verify_sync_plan(plan, observed([{"row_index": 2, "cells": after}, {"row_index": 3, "cells": after}]))
        report = verify_sync_plan(plan, {**observed([{"row_index": 2, "cells": after}]), "history": {"schema_version": 1, "headers": ["event_id", "application_id", "vacancy_id", "status", "effective_at", "recorded_at", "reason", "note"], "rows": []}})
        self.assertFalse(report["verified"])
        self.assertEqual("history_missing_after_write", report["failures"][0]["reason"])

    def test_literal_values_use_string_value_not_formula_value(self) -> None:
        self.assertEqual({"userEnteredValue": {"stringValue": "=SUM(A1:A2)"}}, literal_cell_data("=SUM(A1:A2)"))

    def test_history_is_append_only_and_id_keyed(self) -> None:
        export = source()
        export["events"].append({"event_id": "event-2", "application_id": "app-1", "vacancy_id": "vac-1", "status": "interview", "reason": "invited"})
        history = {"schema_version": 1, "headers": ["event_id", "application_id", "vacancy_id", "status", "effective_at", "recorded_at", "reason", "note"], "rows": [{"row_index": 8, "cells": {"event_id": "event-1", "application_id": "app-1", "vacancy_id": "vac-1", "status": "applied", "effective_at": "", "recorded_at": "", "reason": "", "note": ""}}]}
        plan = build_sync_plan(export, {**observed([]), "history": history})
        self.assertEqual(["noop", "insert"], [item["kind"] for item in plan["history_operations"]])

    def test_altered_immutable_history_event_fails_closed(self) -> None:
        history = {"schema_version": 1, "headers": ["event_id", "application_id", "vacancy_id", "status", "effective_at", "recorded_at", "reason", "note"], "rows": [{"row_index": 8, "cells": {"event_id": "event-1", "vacancy_id": "vac-1", "status": "rejected"}}]}
        with self.assertRaises(SheetsSyncError):
            build_sync_plan(source(), {**observed([]), "history": history})

    def test_incremental_requests_do_not_write_manual_columns(self) -> None:
        plan = build_sync_plan(source(), observed([]), synced_at="2026-09-21T12:00:00Z")
        requests = build_batch_requests(plan, sheet_ids={APPLICATION_TAB: 0, HISTORY_TAB: 1001}, application_next_row=2, history_next_row=2)
        written_columns = [item["updateCells"]["range"]["startColumnIndex"] for item in requests if "updateCells" in item]
        self.assertNotIn(len(SYSTEM_COLUMNS) + 4, written_columns)
        self.assertTrue(requests)

    def test_package_link_can_fill_without_storage_revision_change(self) -> None:
        exported = source()
        exported["applications"][0]["package_url"] = "https://example.test/package"
        old = build_sync_plan(source(), observed([]))["operations"][0]["cells"]
        plan = build_sync_plan(exported, observed([{"row_index": 2, "cells": old}]))
        self.assertEqual("update", plan["operations"][0]["kind"])
        self.assertEqual({"package_url": "https://example.test/package"}, plan["operations"][0]["cells"])

    def test_excluded_package_row_and_history_are_deleted_only_without_manual_data(self) -> None:
        exported = source()
        exported["applications"] = []
        exported["events"] = []
        exported["coverage"] = {"confirmed_without_package_records": [{"application_id": "app-1"}]}
        row = {"row_index": 2, "cells": {"application_id": "app-1", "vacancy_id": "vac-1"}}
        history = {"schema_version": 1, "headers": ["event_id", "application_id", "vacancy_id", "status", "effective_at", "recorded_at", "reason", "note"],
                   "rows": [{"row_index": 2, "cells": {"event_id": "event-1", "application_id": "app-1"}}]}
        plan = build_sync_plan(exported, {**observed([row]), "history": history})
        self.assertEqual(1, plan["summary"]["deletes"])
        self.assertEqual(1, plan["summary"]["history_deletes"])
        requests = build_batch_requests(plan, sheet_ids={APPLICATION_TAB: 0, HISTORY_TAB: 1001},
                                        application_next_row=3, history_next_row=3)
        self.assertEqual(2, sum("deleteDimension" in request for request in requests))
        self.assertTrue(verify_sync_plan(plan, {**observed([]), "history": {**history, "rows": []}})["verified"])
        row["cells"]["my_notes"] = "keep"
        blocked = build_sync_plan(exported, {**observed([row]), "history": history})
        self.assertEqual("excluded_application_has_manual_data", blocked["conflicts"][0]["reason"])

    def test_setup_renames_only_confirmed_blank_sheet1_and_adds_views(self) -> None:
        metadata = {"sheets": [{"properties": {"title": "Sheet1", "sheetId": 0}}]}
        with self.assertRaises(SheetsSyncError):
            build_setup_requests(metadata, confirmed_blank_sheet1=False)
        requests = build_setup_requests(metadata, confirmed_blank_sheet1=True)
        self.assertTrue(any("updateSheetProperties" in item for item in requests))
        self.assertEqual(4, sum("addFilterView" in item for item in requests))
        closed = next(item["addFilterView"] for item in requests if item.get("addFilterView", {}).get("filter", {}).get("title") == "Завершённые процессы")
        condition = next(iter(closed["filter"]["criteria"].values()))["condition"]
        self.assertEqual("CUSTOM_FORMULA", condition["type"])
        self.assertEqual('=OR($E2="closed",$E2="rejected",$E2="withdrawn")', condition["values"][0]["userEnteredValue"])


if __name__ == "__main__":
    unittest.main()
