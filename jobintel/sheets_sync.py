"""Deterministic, connector-neutral planning for the Job Applications sheet.

This module deliberately does not call Google APIs.  A scheduled Codex task reads
the live sheet, uses this module to produce a plan, performs the connector write,
and then passes the readback to :func:`verify_sync_plan`.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import yaml


SCHEMA_VERSION = 1
TECHNICAL_COLUMNS = (
    "application_id",
    "vacancy_id",
    "source_revision",
    "synced_source_version",
    "synced_at",
)
MANUAL_COLUMNS = (
    "next_action",
    "due_date",
    "last_contact",
    "contact_person_and_contact",
    "my_notes",
)
SYSTEM_COLUMNS = (
    "company",
    "title",
    "effective_at",
    "recorded_at",
    "status",
    "status_effective_at",
    "status_recorded_at",
    "location",
    "work_format",
    "salary_from",
    "salary_to",
    "salary_currency",
    "salary_period",
    "salary_tax_basis",
    "application_channel",
    "vacancy_url",
    "package_url",
    "completion_reason",
    *TECHNICAL_COLUMNS,
)
HISTORY_COLUMNS = (
    "event_id", "application_id", "vacancy_id", "status", "effective_at", "recorded_at", "reason", "note",
)
APPLICATION_TAB = "Отклики"
HISTORY_TAB = "История"
OVERVIEW_TAB = "Обзор"
LOOKUPS_TAB = "Справочники"
DISPLAY_HEADERS = {
    "company": "Компания", "title": "Должность", "effective_at": "Дата отклика",
    "recorded_at": "Дата записи", "status": "Текущий статус",
    "status_effective_at": "Дата изменения статуса", "status_recorded_at": "Дата записи статуса",
    "next_action": "Следующее действие", "due_date": "Срок действия", "last_contact": "Последний контакт",
    "contact_person_and_contact": "Контакт", "my_notes": "Мои заметки",
    "location": "Локация", "work_format": "Формат работы", "salary_from": "Зарплата от",
    "salary_to": "Зарплата до", "salary_currency": "Валюта", "salary_period": "Период",
    "salary_tax_basis": "Gross/Net", "application_channel": "Канал подачи", "vacancy_url": "Ссылка на вакансию",
    "package_url": "Пакет документов", "completion_reason": "Причина завершения",
    "application_id": "application_id", "vacancy_id": "ID вакансии", "source_revision": "source_revision",
    "synced_source_version": "synced_source_version", "synced_at": "synced_at",
}
HEADER_TO_FIELD = {label: field for field, label in DISPLAY_HEADERS.items()}
HEADER_TO_FIELD["vacancy_id"] = "vacancy_id"  # Existing sheets use the former technical header.
# A plan is only safe after the setup pass has created every system-owned column.
REQUIRED_HEADERS = SYSTEM_COLUMNS
APPLICATION_HEADERS = SYSTEM_COLUMNS + MANUAL_COLUMNS


class SheetsSyncError(RuntimeError):
    """An invalid deterministic export, observation, or plan."""


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def payload_hash(value: Mapping[str, Any]) -> str:
    payload = dict(value)
    payload.pop("payload_sha256", None)
    return "sha256:" + hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def build_export(source: Mapping[str, Any]) -> dict[str, Any]:
    """Validate and canonically order a storage export without changing its facts."""
    if source.get("schema_version") != SCHEMA_VERSION:
        raise SheetsSyncError("export schema_version must be 1")
    revision = _revision(source.get("source_revision"), "source_revision")
    applications = source.get("applications")
    events = source.get("events")
    coverage = source.get("coverage")
    if not isinstance(applications, list) or not isinstance(events, list) or not isinstance(coverage, Mapping):
        raise SheetsSyncError("export requires applications, events, and coverage")
    normalized_apps = [_application(item) for item in applications]
    ids = [item["application_id"] for item in normalized_apps]
    if len(ids) != len(set(ids)):
        raise SheetsSyncError("export has duplicate application_id")
    normalized_events = [_event(item) for item in events]
    event_ids = [item["event_id"] for item in normalized_events]
    if len(event_ids) != len(set(event_ids)):
        raise SheetsSyncError("export has duplicate event_id")
    result = {
        "schema_version": SCHEMA_VERSION,
        "source_revision": revision,
        "applications": sorted(normalized_apps, key=lambda item: item["application_id"]),
        "events": sorted(normalized_events, key=lambda item: item["event_id"]),
        "coverage": dict(coverage),
    }
    result["payload_sha256"] = payload_hash(result)
    return result


def build_sync_plan(
    export: Mapping[str, Any], observed: Mapping[str, Any], *, synced_at: str | None = None
) -> dict[str, Any]:
    """Return ID-keyed inserts/updates/noops and fail closed on conflicts."""
    source = build_export(export)
    sheet = _observed_sheet(observed, expected_headers=APPLICATION_HEADERS)

    rows_by_id: dict[str, dict[str, Any]] = {}
    for row in sheet["rows"]:
        application_id = _text(row["cells"].get("application_id"))
        if not application_id:
            continue
        if application_id in rows_by_id:
            raise SheetsSyncError(f"observed sheet has duplicate application_id: {application_id}")
        rows_by_id[application_id] = row

    operations: list[dict[str, Any]] = []
    conflicts: list[dict[str, Any]] = []
    excluded_ids = {
        _text(item.get("application_id"))
        for item in source["coverage"].get("confirmed_without_package_records", [])
        if isinstance(item, Mapping) and _text(item.get("application_id"))
    }
    for application in source["applications"]:
        expected = _system_cells(application, source["source_revision"])
        observed_row = rows_by_id.get(application["application_id"])
        if observed_row is None:
            operations.append({
                "kind": "insert",
                "application_id": application["application_id"],
                "row_index": None,
                "before": {},
                "cells": _with_sync_time(expected, synced_at),
            })
            continue
        before = {key: observed_row["cells"].get(key) for key in expected}
        current_revision = observed_row["cells"].get("source_revision")
        try:
            row_revision = _observed_revision(current_revision)
        except SheetsSyncError:
            conflicts.append(_conflict(application, observed_row, "invalid_observed_revision"))
            continue
        if row_revision > application["source_revision"]:
            conflicts.append(_conflict(application, observed_row, "observed_revision_newer"))
            continue
        changed = {key: value for key, value in expected.items() if _text(before.get(key)) != _text(value)}
        if changed:
            if row_revision == application["source_revision"] and not set(changed).issubset({"package_url"}):
                conflicts.append(_conflict(application, observed_row, "same_revision_data_mismatch"))
                continue
            changed = _with_sync_time(changed, synced_at)
        operations.append({
            "kind": "noop" if not changed else "update",
            "application_id": application["application_id"],
            "row_index": observed_row["row_index"],
            "before": before,
            "cells": changed,
        })
    for application_id in sorted(excluded_ids):
        row = rows_by_id.get(application_id)
        if row is None:
            continue
        if any(_text(row["cells"].get(field)) for field in MANUAL_COLUMNS):
            conflicts.append({"application_id": application_id, "row_index": row["row_index"],
                              "reason": "excluded_application_has_manual_data"})
            continue
        operations.append({"kind": "delete", "application_id": application_id,
                           "row_index": row["row_index"], "before": row["cells"], "cells": {}})
    result = {
        "schema_version": SCHEMA_VERSION,
        "export_payload_sha256": source["payload_sha256"],
        "observed_sheet_revision": sheet["sheet_revision"],
        "synced_at": synced_at,
        "manual_columns": list(MANUAL_COLUMNS),
        "operations": operations,
        "conflicts": conflicts,
        "history_operations": _history_operations(source["events"], observed.get("history"), excluded_ids),
        "summary": {
            "inserts": sum(item["kind"] == "insert" for item in operations),
            "updates": sum(item["kind"] == "update" for item in operations),
            "noops": sum(item["kind"] == "noop" for item in operations),
            "deletes": sum(item["kind"] == "delete" for item in operations),
            "conflicts": len(conflicts),
        },
    }
    result["summary"]["history_inserts"] = sum(
        item["kind"] == "insert" for item in result["history_operations"]
    )
    result["summary"]["history_noops"] = sum(
        item["kind"] == "noop" for item in result["history_operations"]
    )
    result["summary"]["history_deletes"] = sum(
        item["kind"] == "delete" for item in result["history_operations"]
    )
    result["payload_sha256"] = payload_hash(result)
    return result


def verify_sync_plan(plan: Mapping[str, Any], observed: Mapping[str, Any]) -> dict[str, Any]:
    """Validate a post-write CellData readback against a previously generated plan."""
    if plan.get("schema_version") != SCHEMA_VERSION:
        raise SheetsSyncError("plan schema_version must be 1")
    if plan.get("payload_sha256") != payload_hash(plan):
        raise SheetsSyncError("plan payload_sha256 does not match its content")
    sheet = _observed_sheet(observed, expected_headers=APPLICATION_HEADERS)
    rows: dict[str, dict[str, Any]] = {}
    for row in sheet["rows"]:
        application_id = _text(row["cells"].get("application_id"))
        if not application_id:
            continue
        if application_id in rows:
            raise SheetsSyncError(f"readback has duplicate application_id: {application_id}")
        rows[application_id] = row
    failures: list[dict[str, Any]] = []
    checked = 0
    for operation in plan.get("operations", []):
        if operation.get("kind") == "delete":
            if _text(operation.get("application_id")) in rows:
                failures.append({"application_id": operation["application_id"], "reason": "still_present_after_delete"})
            continue
        if operation.get("kind") not in {"insert", "update"}:
            continue
        application_id = _text(operation.get("application_id"))
        row = rows.get(application_id)
        if row is None:
            failures.append({"application_id": application_id, "reason": "missing_after_write"})
            continue
        for key, expected in _mapping(operation.get("cells"), "operation cells").items():
            checked += 1
            actual = row["cells"].get(key)
            if _text(actual) != _text(expected):
                failures.append({
                    "application_id": application_id,
                    "column": key,
                    "expected": expected,
                    "actual": actual,
                })
    history_input = observed.get("history")
    if plan.get("history_operations") and history_input is None:
        raise SheetsSyncError("readback history is required")
    if history_input is not None:
        history = _observed_history(_mapping(history_input, "readback history"))
        history_rows: dict[str, dict[str, Any]] = {}
        for row in history["rows"]:
            event_id = _text(row["cells"].get("event_id"))
            if not event_id:
                continue
            if event_id in history_rows:
                raise SheetsSyncError(f"readback history has duplicate event_id: {event_id}")
            history_rows[event_id] = row
        for operation in plan.get("history_operations", []):
            event_id = _text(operation.get("event_id"))
            row = history_rows.get(event_id)
            if operation.get("kind") == "delete":
                if row is not None:
                    failures.append({"event_id": event_id, "reason": "history_still_present_after_delete"})
                continue
            if row is None:
                failures.append({"event_id": event_id, "reason": "history_missing_after_write"})
                continue
            expected = operation.get("cells") if operation.get("kind") == "insert" else operation.get("before")
            for key, value in _mapping(expected, "history operation cells").items():
                checked += 1
                if _text(row["cells"].get(key)) != _text(value):
                    failures.append({"event_id": event_id, "column": key, "expected": value, "actual": row["cells"].get(key)})
    result = {"schema_version": SCHEMA_VERSION, "verified": not failures, "checked_cells": checked, "failures": failures}
    result["payload_sha256"] = payload_hash(result)
    return result


def literal_cell_data(value: Any) -> dict[str, str]:
    """Return a Sheets CellData userEnteredValue that cannot become a formula."""
    return {"userEnteredValue": {"stringValue": _text(value)}}


def observed_from_google(metadata: Mapping[str, Any], cells: Mapping[str, Any], *, tab: str = APPLICATION_TAB) -> dict[str, Any]:
    """Convert connector metadata/CellData into the planner's row representation."""
    sheet = next((item for item in metadata.get("sheets", []) if item.get("properties", {}).get("title") == tab), None)
    if not isinstance(sheet, Mapping):
        raise SheetsSyncError(f"metadata has no {tab!r} tab")
    cell_sheet = next((item for item in cells.get("sheets", []) if item.get("properties", {}).get("title") == tab), {})
    data = sheet.get("data") or cell_sheet.get("data") or cells.get("data")
    if not isinstance(data, list) or not data:
        return {"schema_version": 1, "sheet_revision": _text(metadata.get("spreadsheetId")), "headers": [], "rows": []}
    if len(data) != 1 or data[0].get("startRow", 0) != 0 or data[0].get("startColumn", 0) != 0:
        raise SheetsSyncError("read each managed tab as one complete range starting at A1")
    row_data = data[0].get("rowData") or data[0].get("rowData", [])
    if not isinstance(row_data, list):
        row_data = []
    headers = [HEADER_TO_FIELD.get(_cell_text(cell), _cell_text(cell)) for cell in (row_data[0].get("values", []) if row_data else [])]
    while headers and not headers[-1]:
        headers.pop()
    rows = []
    next_row = 2
    for index, raw in enumerate(row_data[1:], start=2):
        values = raw.get("values", [])
        if any(_cell_text(cell) for cell in values):
            next_row = index + 1
        mapped = {header: _cell_text(values[column]) if column < len(values) else "" for column, header in enumerate(headers) if header}
        if any(mapped.values()):
            rows.append({"row_index": index, "cells": mapped})
    return {"schema_version": 1, "sheet_revision": _text(metadata.get("spreadsheetId")), "headers": headers, "rows": rows, "next_row": next_row}


def workbook_read_ranges(metadata: Mapping[str, Any]) -> list[str]:
    ranges = []
    for title in (APPLICATION_TAB, HISTORY_TAB):
        sheet = next((item for item in metadata.get("sheets", []) if item.get("properties", {}).get("title") == title), None)
        grid = sheet.get("properties", {}).get("gridProperties", {}) if sheet else {}
        rows, columns = grid.get("rowCount"), grid.get("columnCount")
        if not isinstance(rows, int) or not isinstance(columns, int) or rows < 1 or columns < 1:
            raise SheetsSyncError(f"missing current grid dimensions for {title}")
        letters = ""
        while columns:
            columns, remainder = divmod(columns - 1, 26)
            letters = chr(65 + remainder) + letters
        ranges.append(f"'{title}'!A1:{letters}{rows}")
    return ranges


def observe_workbook(metadata: Mapping[str, Any], cells: Mapping[str, Any], *, requested_ranges: Sequence[str]) -> dict[str, Any]:
    if not set(workbook_read_ranges(metadata)).issubset(set(requested_ranges)):
        raise SheetsSyncError("connector read ranges must cover both complete current grids")
    observed = observed_from_google(metadata, cells)
    observed["history"] = observed_from_google(metadata, cells, tab=HISTORY_TAB)
    return observed


def build_setup_requests(metadata: Mapping[str, Any], *, confirmed_blank_sheet1: bool) -> list[dict[str, Any]]:
    """Create the four-tab workbook only when the caller proved the original grid blank."""
    if not confirmed_blank_sheet1:
        raise SheetsSyncError("setup is permitted only after a bounded read proves Sheet1 blank")
    sheets = _mapping_list(metadata.get("sheets"), "metadata sheets")
    by_title = {item.get("properties", {}).get("title"): item.get("properties", {}).get("sheetId") for item in sheets}
    if any(title in by_title for title in (APPLICATION_TAB, HISTORY_TAB, OVERVIEW_TAB, LOOKUPS_TAB)):
        raise SheetsSyncError("managed tabs already exist; use incremental sync instead of setup")
    requests: list[dict[str, Any]] = []
    primary_id = by_title.get(APPLICATION_TAB)
    if primary_id is None:
        sheet1 = by_title.get("Sheet1")
        if sheet1 is None:
            raise SheetsSyncError("setup requires an existing Отклики tab or confirmed blank Sheet1")
        primary_id = sheet1
        requests.append({"updateSheetProperties": {"properties": {"sheetId": primary_id, "title": APPLICATION_TAB}, "fields": "title"}})
    used_ids = {item.get("properties", {}).get("sheetId") for item in sheets}
    ids = {APPLICATION_TAB: primary_id}
    for offset, title in enumerate((HISTORY_TAB, OVERVIEW_TAB, LOOKUPS_TAB), start=1001):
        if title in by_title:
            ids[title] = by_title[title]
        else:
            while offset in used_ids:
                offset += 1
            ids[title] = offset
            used_ids.add(offset)
            requests.append({"addSheet": {"properties": {"sheetId": offset, "title": title}}})
    primary_columns = next(item["properties"].get("gridProperties", {}).get("columnCount", 26)
                           for item in sheets if item["properties"]["sheetId"] == primary_id)
    if primary_columns < len(SYSTEM_COLUMNS + MANUAL_COLUMNS):
        requests.append({"updateSheetProperties": {"properties": {"sheetId": primary_id,
            "gridProperties": {"columnCount": len(SYSTEM_COLUMNS + MANUAL_COLUMNS)}},
            "fields": "gridProperties.columnCount"}})
    requests.append({"updateSpreadsheetProperties": {"properties": {"timeZone": "Europe/Rome"}, "fields": "timeZone"}})
    requests.extend(_tab_setup_requests(ids))
    return requests


def build_batch_requests(plan: Mapping[str, Any], *, sheet_ids: Mapping[str, int], application_next_row: int, history_next_row: int) -> list[dict[str, Any]]:
    """Compile a conflict-free plan into raw connector batchUpdate requests."""
    if plan.get("conflicts"):
        raise SheetsSyncError("cannot build requests for a conflicting plan")
    app_id, history_id = _sheet_id(sheet_ids, APPLICATION_TAB), _sheet_id(sheet_ids, HISTORY_TAB)
    requests: list[dict[str, Any]] = []
    next_app, next_history = application_next_row, history_next_row
    for operation in plan.get("operations", []):
        if operation.get("kind") in {"noop", "delete"}:
            continue
        row = operation.get("row_index") or next_app
        next_app += operation.get("kind") == "insert"
        requests.extend(_write_cells(app_id, row - 1, operation.get("cells"), SYSTEM_COLUMNS + MANUAL_COLUMNS))
    for operation in plan.get("history_operations", []):
        if operation.get("kind") != "insert":
            continue
        requests.extend(_write_cells(history_id, next_history - 1, operation["cells"], HISTORY_COLUMNS))
        next_history += 1
    for operation in sorted((item for item in plan.get("operations", []) if item.get("kind") == "delete"),
                            key=lambda item: item["row_index"], reverse=True):
        row = operation["row_index"] - 1
        requests.append({"deleteDimension": {"range": {"sheetId": app_id, "dimension": "ROWS",
                                                          "startIndex": row, "endIndex": row + 1}}})
    for operation in sorted((item for item in plan.get("history_operations", []) if item.get("kind") == "delete"),
                            key=lambda item: item["row_index"], reverse=True):
        row = operation["row_index"] - 1
        requests.append({"deleteDimension": {"range": {"sheetId": history_id, "dimension": "ROWS",
                                                          "startIndex": row, "endIndex": row + 1}}})
    if requests:
        column = SYSTEM_COLUMNS.index("vacancy_id")
        requests.extend([
            {"updateCells": {"range": {"sheetId": app_id, "startRowIndex": 0, "endRowIndex": 1,
                                       "startColumnIndex": column, "endColumnIndex": column + 1},
                             "rows": [{"values": [literal_cell_data(DISPLAY_HEADERS["vacancy_id"])]}],
                             "fields": "userEnteredValue"}},
            {"updateDimensionProperties": {"range": {"sheetId": app_id, "dimension": "COLUMNS",
                                                    "startIndex": column, "endIndex": column + 1},
                                           "properties": {"hiddenByUser": False, "pixelSize": 285},
                                           "fields": "hiddenByUser,pixelSize"}},
        ])
    return requests


def cli_main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="sheets")
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("export", "plan", "verify", "requests", "observed", "read-ranges"):
        command = commands.add_parser(name)
        command.add_argument("--output", required=True, type=Path)
        if name == "export":
            command.add_argument("--input", required=True, type=Path)
        elif name == "observed":
            command.add_argument("--metadata", required=True, type=Path)
            command.add_argument("--cells", required=True, type=Path)
            command.add_argument("--ranges", required=True, type=Path)
        elif name == "read-ranges":
            command.add_argument("--metadata", required=True, type=Path)
        elif name == "plan":
            command.add_argument("--export", required=True, type=Path)
            command.add_argument("--observed", required=True, type=Path)
            command.add_argument("--synced-at")
        elif name == "verify":
            command.add_argument("--plan", required=True, type=Path)
            command.add_argument("--observed", required=True, type=Path)
        else:
            command.add_argument("--plan", required=True, type=Path)
            command.add_argument("--metadata", required=True, type=Path)
            command.add_argument("--observed", type=Path)
            command.add_argument("--application-next-row", type=int)
            command.add_argument("--history-next-row", type=int)
    setup = commands.add_parser("setup")
    setup.add_argument("--metadata", required=True, type=Path)
    setup.add_argument("--confirmed-blank-sheet1", action="store_true")
    setup.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "setup":
            result = {"requests": build_setup_requests(
                _read_json(_codex_work_path(args.metadata)),
                confirmed_blank_sheet1=args.confirmed_blank_sheet1,
            )}
            result["payload_sha256"] = payload_hash(result)
        elif args.command == "export":
            result = build_export(_read_json(_codex_work_path(args.input)))
        elif args.command == "observed":
            result = observe_workbook(_read_json(_codex_work_path(args.metadata)), _read_json(_codex_work_path(args.cells)),
                                      requested_ranges=_read_json(_codex_work_path(args.ranges))["ranges"])
        elif args.command == "read-ranges":
            result = {"ranges": workbook_read_ranges(_read_json(_codex_work_path(args.metadata)))}
        elif args.command == "plan":
            result = build_sync_plan(
                _read_json(_codex_work_path(args.export)),
                _read_json(_codex_work_path(args.observed)),
                synced_at=args.synced_at,
            )
        elif args.command == "verify":
            result = verify_sync_plan(
                _read_json(_codex_work_path(args.plan)), _read_json(_codex_work_path(args.observed))
            )
        else:
            config = load_destination_config(Path.cwd() / "config" / "data-services.yaml")
            metadata = _read_json(_codex_work_path(args.metadata))
            observed = _read_json(_codex_work_path(args.observed)) if args.observed else {}
            app_next = observed.get("next_row", args.application_next_row)
            history_next = observed.get("history", {}).get("next_row", args.history_next_row)
            if any(not isinstance(value, int) or isinstance(value, bool) or value < 2 for value in (app_next, history_next)):
                raise SheetsSyncError("requests requires --observed with verified append positions")
            result = {"requests": build_batch_requests(
                _read_json(_codex_work_path(args.plan)),
                sheet_ids=_sheet_ids_from_metadata(metadata),
                application_next_row=app_next,
                history_next_row=history_next,
            ), "spreadsheet_id": config["spreadsheet_id"]}
            expansions = []
            for sheet in metadata["sheets"]:
                properties = sheet["properties"]
                sheet_id = properties["sheetId"]
                required_rows = max((item["updateCells"]["range"]["endRowIndex"] for item in result["requests"]
                                     if "updateCells" in item and item["updateCells"]["range"]["sheetId"] == sheet_id), default=0)
                current_rows = properties.get("gridProperties", {}).get("rowCount", 0)
                if required_rows > current_rows:
                    expansions.append({"appendDimension": {"sheetId": sheet_id, "dimension": "ROWS", "length": required_rows - current_rows}})
            result["requests"] = expansions + result["requests"]
            result["payload_sha256"] = payload_hash(result)
        _write_json(_codex_work_path(args.output), result)
        if args.command == "verify" and result.get("verified") is False:
            return 1
    except (OSError, ValueError, SheetsSyncError) as exc:
        print(f"sheets {args.command} failed: {exc}", file=sys.stderr)
        return 1
    return 0


def _application(value: Any) -> dict[str, Any]:
    item = _mapping(value, "application")
    required = ("application_id", "vacancy_id", "directory", "company", "title", "status", "source_revision")
    result = dict(item)
    for field in required:
        if not _text(item.get(field)):
            raise SheetsSyncError(f"application {field} is required")
        result[field] = _text(item[field])
    result["source_revision"] = _revision(item["source_revision"], "application source_revision")
    return result


def _event(value: Any) -> dict[str, Any]:
    item = _mapping(value, "event")
    if not _text(item.get("event_id")) or not _text(item.get("vacancy_id")) or not _text(item.get("status")):
        raise SheetsSyncError("event_id, vacancy_id, and status are required")
    return dict(item)


def _history_operations(events: list[dict[str, Any]], observed: Any, excluded_ids: set[str] | None = None) -> list[dict[str, Any]]:
    existing: dict[str, dict[str, Any]] = {}
    if observed is not None:
        history = _observed_history(_mapping(observed, "observed history"))
        for row in history["rows"]:
            event_id = _text(row["cells"].get("event_id"))
            if not event_id:
                continue
            if event_id in existing:
                raise SheetsSyncError(f"observed history has duplicate event_id: {event_id}")
            existing[event_id] = row
    operations = []
    for event in events:
        cells = {field: _text(event.get(field)) for field in HISTORY_COLUMNS}
        row = existing.get(event["event_id"])
        if row is None:
            operations.append({"kind": "insert", "event_id": event["event_id"], "row_index": None, "before": {}, "cells": cells})
        elif any(_text(row["cells"].get(field)) != value for field, value in cells.items()):
            raise SheetsSyncError(f"observed history conflicts with immutable event_id: {event['event_id']}")
        else:
            operations.append({"kind": "noop", "event_id": event["event_id"], "row_index": row["row_index"], "before": row["cells"], "cells": {}})
    if excluded_ids:
        for event_id, row in existing.items():
            if _text(row["cells"].get("application_id")) in excluded_ids:
                operations.append({"kind": "delete", "event_id": event_id,
                                   "row_index": row["row_index"], "before": row["cells"], "cells": {}})
    return operations


def _observed_history(value: Mapping[str, Any]) -> dict[str, Any]:
    return _observed_sheet(value, expected_headers=HISTORY_COLUMNS)


def _observed_sheet(value: Mapping[str, Any], *, expected_headers: tuple[str, ...] | None = None) -> dict[str, Any]:
    if value.get("schema_version") != SCHEMA_VERSION:
        raise SheetsSyncError("observed sheet schema_version must be 1")
    headers = value.get("headers")
    rows = value.get("rows")
    if not isinstance(headers, list) or not all(isinstance(header, str) and header for header in headers):
        raise SheetsSyncError("observed headers must be non-empty strings")
    if len(headers) != len(set(headers)):
        raise SheetsSyncError("observed sheet has duplicate headers")
    if expected_headers is not None and tuple(headers[:len(expected_headers)]) != expected_headers:
        raise SheetsSyncError("observed sheet headers are not in canonical managed-column order")
    if not isinstance(rows, list):
        raise SheetsSyncError("observed rows must be a list")
    normalized_rows = []
    indices: set[int] = set()
    for raw in rows:
        row = _mapping(raw, "observed row")
        index = row.get("row_index")
        if isinstance(index, bool) or not isinstance(index, int) or index < 1 or index in indices:
            raise SheetsSyncError("observed row_index must be a unique positive integer")
        indices.add(index)
        cells = _mapping(row.get("cells"), "observed cells")
        normalized_rows.append({"row_index": index, "cells": dict(cells)})
    return {"headers": headers, "rows": normalized_rows, "sheet_revision": _text(value.get("sheet_revision")) or None}


def _system_cells(application: Mapping[str, Any], export_revision: int) -> dict[str, str]:
    values = {field: _text(application.get(field)) for field in SYSTEM_COLUMNS if field not in TECHNICAL_COLUMNS}
    if isinstance(application.get("work_format"), bool):
        values["work_format"] = "Удалённо" if application["work_format"] else ""
    values.update({
        "application_id": _text(application["application_id"]),
        "vacancy_id": _text(application["vacancy_id"]),
        "source_revision": str(application["source_revision"]),
        "synced_source_version": str(application["source_revision"]),
    })
    return values


def _with_sync_time(cells: dict[str, str], synced_at: str | None) -> dict[str, str]:
    result = dict(cells)
    if synced_at is not None:
        result["synced_at"] = _text(synced_at)
    return result


def _tab_setup_requests(ids: Mapping[str, int]) -> list[dict[str, Any]]:
    app_headers = [DISPLAY_HEADERS[field] for field in SYSTEM_COLUMNS + MANUAL_COLUMNS]
    history_headers = list(HISTORY_COLUMNS)
    header_style = {"backgroundColorStyle": {"rgbColor": {"red": 0.93, "green": 0.93, "blue": 0.93}}, "textFormat": {"bold": True, "foregroundColorStyle": {"rgbColor": {"red": 0, "green": 0, "blue": 0}}}}
    requests = []
    for title, headers in ((APPLICATION_TAB, app_headers), (HISTORY_TAB, history_headers)):
        sheet_id = _sheet_id(ids, title)
        requests.extend([
            {"updateCells": {"range": {"sheetId": sheet_id, "startRowIndex": 0, "endRowIndex": 1, "startColumnIndex": 0, "endColumnIndex": len(headers)}, "rows": [{"values": [literal_cell_data(header) for header in headers]}], "fields": "userEnteredValue"}},
            {"repeatCell": {"range": {"sheetId": sheet_id, "startRowIndex": 0, "endRowIndex": 1}, "cell": {"userEnteredFormat": header_style}, "fields": "userEnteredFormat(backgroundColorStyle,textFormat)"}},
            {"updateSheetProperties": {"properties": {"sheetId": sheet_id, "gridProperties": {"frozenRowCount": 1}}, "fields": "gridProperties.frozenRowCount"}},
        ])
    app_id = _sheet_id(ids, APPLICATION_TAB)
    first_tech = len(SYSTEM_COLUMNS) - len(TECHNICAL_COLUMNS)
    requests.extend([
        {"updateDimensionProperties": {"range": {"sheetId": app_id, "dimension": "COLUMNS", "startIndex": first_tech, "endIndex": first_tech + 1}, "properties": {"hiddenByUser": True}, "fields": "hiddenByUser"}},
        {"updateDimensionProperties": {"range": {"sheetId": app_id, "dimension": "COLUMNS", "startIndex": first_tech + 2, "endIndex": first_tech + len(TECHNICAL_COLUMNS)}, "properties": {"hiddenByUser": True}, "fields": "hiddenByUser"}},
        {"updateDimensionProperties": {"range": {"sheetId": app_id, "dimension": "COLUMNS", "startIndex": 0, "endIndex": 2}, "properties": {"pixelSize": 180}, "fields": "pixelSize"}},
        {"repeatCell": {"range": {"sheetId": app_id, "startRowIndex": 1, "startColumnIndex": 2, "endColumnIndex": 4}, "cell": {"userEnteredFormat": {"numberFormat": {"type": "DATE_TIME", "pattern": "yyyy-mm-dd hh:mm"}}}, "fields": "userEnteredFormat.numberFormat"}},
        {"repeatCell": {"range": {"sheetId": app_id, "startRowIndex": 1, "startColumnIndex": 5, "endColumnIndex": 7}, "cell": {"userEnteredFormat": {"numberFormat": {"type": "DATE_TIME", "pattern": "yyyy-mm-dd hh:mm"}}}, "fields": "userEnteredFormat.numberFormat"}},
        {"setBasicFilter": {"filter": {"range": {"sheetId": app_id, "startRowIndex": 0, "startColumnIndex": 0, "endColumnIndex": len(app_headers)}}}},
        {"updateCells": {"range": {"sheetId": _sheet_id(ids, OVERVIEW_TAB), "startRowIndex": 0, "endRowIndex": 5, "startColumnIndex": 0, "endColumnIndex": 2}, "rows": [
            {"values": [literal_cell_data("Обзор откликов"), literal_cell_data("")]},
            {"values": [literal_cell_data("Активные процессы"), {"userEnteredValue": {"formulaValue": "=IF(COUNTA('Отклики'!E2:E)=0,\"\",COUNTIFS('Отклики'!E2:E,\"<>\",'Отклики'!E2:E,\"<>closed\",'Отклики'!E2:E,\"<>rejected\",'Отклики'!E2:E,\"<>withdrawn\"))"}}]},
            {"values": [literal_cell_data("Действия на сегодня"), {"userEnteredValue": {"formulaValue": "=IF(COUNTA('Отклики'!Y2:Y)=0,\"\",COUNTIF('Отклики'!Y2:Y,TODAY()))"}}]},
            {"values": [literal_cell_data("Просроченные действия"), {"userEnteredValue": {"formulaValue": "=IF(COUNTA('Отклики'!Y2:Y)=0,\"\",COUNTIFS('Отклики'!Y2:Y,\"<\"&TODAY(),'Отклики'!Y2:Y,\"<>\"))"}}]},
            {"values": [literal_cell_data("Завершённые процессы"), {"userEnteredValue": {"formulaValue": "=IF(COUNTA('Отклики'!E2:E)=0,\"\",COUNTIF('Отклики'!E2:E,\"closed\")+COUNTIF('Отклики'!E2:E,\"rejected\")+COUNTIF('Отклики'!E2:E,\"withdrawn\"))"}}]},
        ], "fields": "userEnteredValue"}},
        {"updateCells": {"range": {"sheetId": _sheet_id(ids, LOOKUPS_TAB), "startRowIndex": 0, "endRowIndex": 2, "startColumnIndex": 0, "endColumnIndex": 1}, "rows": [{"values": [literal_cell_data("Статусы")]}, {"values": [literal_cell_data("found, applied, interview, rejected, withdrawn, closed")]}], "fields": "userEnteredValue"}},
    ])
    requests.extend(_filter_view_requests(app_id, len(app_headers)))
    return requests


def _filter_view_requests(sheet_id: int, end_column: int) -> list[dict[str, Any]]:
    base = {"sheetId": sheet_id, "startRowIndex": 0, "startColumnIndex": 0, "endColumnIndex": end_column}
    status = SYSTEM_COLUMNS.index("status")
    due = len(SYSTEM_COLUMNS) + MANUAL_COLUMNS.index("due_date")
    return [
        {"addFilterView": {"filter": {"title": "Активные процессы", "range": base, "criteria": {str(status): {"hiddenValues": ["closed", "rejected", "withdrawn"]}}}}},
        {"addFilterView": {"filter": {"title": "Действия на сегодня", "range": base, "criteria": {str(due): {"condition": {"type": "CUSTOM_FORMULA", "values": [{"userEnteredValue": "=$Y2=TODAY()"}]}}}}}},
        {"addFilterView": {"filter": {"title": "Просроченные действия", "range": base, "criteria": {str(due): {"condition": {"type": "CUSTOM_FORMULA", "values": [{"userEnteredValue": "=AND($Y2<TODAY(),$Y2<>\"\")"}]}}}}}},
        {"addFilterView": {"filter": {"title": "Завершённые процессы", "range": base, "criteria": {str(status): {"condition": {"type": "CUSTOM_FORMULA", "values": [{"userEnteredValue": "=OR($E2=\"closed\",$E2=\"rejected\",$E2=\"withdrawn\")"}]}}}}}},
    ]


def _write_cells(sheet_id: int, row_index: int, cells: Any, columns: tuple[str, ...]) -> list[dict[str, Any]]:
    changes = _mapping(cells, "operation cells")
    indexed = []
    for column in columns:
        if column not in changes:
            continue
        indexed.append((columns.index(column), column, changes[column]))
    for column in changes:
        if column not in columns:
            raise SheetsSyncError(f"unknown sheet column: {column}")
    requests = []
    group: list[tuple[int, str, Any]] = []
    for item in indexed + [(None, "", None)]:
        if group and (item[0] is None or item[0] != group[-1][0] + 1):
            start = group[0][0]
            requests.append({"updateCells": {"range": {"sheetId": sheet_id, "startRowIndex": row_index, "endRowIndex": row_index + 1, "startColumnIndex": start, "endColumnIndex": group[-1][0] + 1}, "rows": [{"values": [_cell_for_field(field, value) for _, field, value in group]}], "fields": "userEnteredValue"}})
            group = []
        if item[0] is not None:
            group.append(item)
    return requests


def _cell_for_field(field: str, value: Any) -> dict[str, Any]:
    # Preserve exact provenance timestamps and unknowns through connector readback.
    # User-owned due dates are never written by this exporter.
    return literal_cell_data(value)


def _sheet_id(sheet_ids: Mapping[str, int], title: str) -> int:
    value = sheet_ids.get(title)
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise SheetsSyncError(f"missing sheetId for {title}")
    return value


def _sheet_ids_from_metadata(metadata: Mapping[str, Any]) -> dict[str, int]:
    return {
        title: _sheet_id({title: item.get("properties", {}).get("sheetId")}, title)
        for title in (APPLICATION_TAB, HISTORY_TAB)
        for item in _mapping_list(metadata.get("sheets"), "metadata sheets")
        if item.get("properties", {}).get("title") == title
    }


def _mapping_list(value: Any, label: str) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise SheetsSyncError(f"{label} must be a list")
    return [_mapping(item, label) for item in value]


def _cell_text(cell: Any) -> str:
    if not isinstance(cell, Mapping):
        return ""
    value = cell.get("userEnteredValue") or cell.get("effectiveValue") or {}
    if not isinstance(value, Mapping):
        return _text(cell.get("formattedValue"))
    for key in ("stringValue", "numberValue", "boolValue", "formulaValue"):
        if key in value:
            return _text(value[key])
    return _text(cell.get("formattedValue"))


def _conflict(application: Mapping[str, Any], row: Mapping[str, Any], reason: str) -> dict[str, Any]:
    return {"application_id": application["application_id"], "row_index": row["row_index"], "reason": reason}


def _mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise SheetsSyncError(f"{label} must be a mapping")
    return dict(value)


def _revision(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise SheetsSyncError(f"{label} must be a non-negative integer")
    return value


def _observed_revision(value: Any) -> int:
    """Parse the literal-string revision read from a Sheets CellData value."""
    if isinstance(value, int) and not isinstance(value, bool):
        return _revision(value, "observed source_revision")
    text = _text(value)
    if not text.isascii() or not text.isdecimal():
        raise SheetsSyncError("observed source_revision must be a non-negative integer")
    return int(text)


def _text(value: Any) -> str:
    return "" if value is None else str(value)


def _read_json(path: Path) -> dict[str, Any]:
    loaded = json.loads(path.read_text(encoding="utf-8"))
    return _mapping(loaded, str(path))


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_destination_config(path: Path) -> dict[str, str]:
    """Read the non-secret Sheets and backup destination IDs from project config."""
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise SheetsSyncError(f"cannot read data-services config: {exc}") from exc
    root = _mapping(loaded, "data-services config")
    google = _mapping(root.get("google"), "google config")
    keys = ("spreadsheet_id", "parent_folder_id", "backup_folder_id")
    result = {key: _text(google.get(key)).strip() for key in keys}
    missing = [key for key, value in result.items() if not value]
    if missing:
        raise SheetsSyncError("google_drive config missing: " + ", ".join(missing))
    return result


def _codex_work_path(path: Path) -> Path:
    resolved = path.resolve()
    work = (Path.cwd() / ".codex-work").resolve()
    try:
        resolved.relative_to(work)
    except ValueError as exc:
        raise SheetsSyncError(f"JSON artifacts must be under {work}") from exc
    return resolved


if __name__ == "__main__":
    raise SystemExit(cli_main())
