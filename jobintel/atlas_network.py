"""Temporary Atlas database access for a single GitHub runner IPv4 address."""
from __future__ import annotations

import argparse
import base64
import ipaddress
import json
import os
import re
import sys
import tempfile
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


MAX_GRANT_DURATION = timedelta(hours=2)
RECONCILE_ATTEMPTS = 3


class AtlasNetworkError(RuntimeError):
    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class AtlasAccess:
    def __init__(self, project_id: str, client_id: str, client_secret: str):
        if not re.fullmatch(r"[a-fA-F0-9]{24}", project_id):
            raise AtlasNetworkError("ATLAS_PROJECT_ID must be a 24-character project ID")
        if not client_id or not client_secret:
            raise AtlasNetworkError("ATLAS_CLIENT_ID and ATLAS_CLIENT_SECRET are required")
        self.project_id = project_id
        basic = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
        token = self._request("https://cloud.mongodb.com/api/oauth/token", "POST",
                              b"grant_type=client_credentials",
                              {"Authorization": "Basic " + basic,
                               "Content-Type": "application/x-www-form-urlencoded"})
        self.token = token["access_token"]

    @staticmethod
    def _request(url, method="GET", data=None, headers=None):
        try:
            request = Request(url, data=data, headers=headers or {}, method=method)
            with urlopen(request, timeout=30) as response:
                raw = response.read()
                return json.loads(raw) if raw else {}
        except HTTPError as exc:
            raise AtlasNetworkError(
                f"Atlas request failed with HTTP {exc.code}", status_code=exc.code
            ) from None
        except (URLError, TimeoutError):
            raise AtlasNetworkError("Atlas network request failed") from None

    def request(self, method="GET", entry=None, payload=None):
        url = f"https://cloud.mongodb.com/api/atlas/v2/groups/{self.project_id}/accessList"
        if entry is not None:
            url += "/" + quote(entry, safe="")
        data = json.dumps(payload).encode() if payload is not None else None
        return self._request(url, method, data, {"Authorization": "Bearer " + self.token,
                              "Accept": "application/vnd.atlas.2025-03-12+json",
                              "Content-Type": "application/json"})


def public_runner_ip() -> str:
    try:
        with urlopen("https://checkip.amazonaws.com", timeout=15) as response:
            value = response.read(128).decode().strip()
        address = ipaddress.ip_address(value)
    except (ValueError, URLError, TimeoutError):
        raise AtlasNetworkError("cannot determine runner public IP") from None
    if address.version != 4 or not address.is_global:
        raise AtlasNetworkError("runner must have a public IPv4 address")
    return str(address)


def grant(access, ip: str, receipt_path: Path, *, now=None) -> dict:
    try:
        address = ipaddress.ip_address(ip)
    except ValueError:
        raise AtlasNetworkError("only one public IPv4 /32 may be added") from None
    if address.version != 4 or not address.is_global:
        raise AtlasNetworkError("only one public IPv4 /32 may be added")
    now = _utc_datetime(now or datetime.now(timezone.utc), "grant time")
    cidr = f"{address}/32"
    if receipt_path.exists():
        previous = _read_receipt(receipt_path)
        _validate_receipt(previous, access.project_id, cidr, now=now)
        if previous["created"]:
            _ensure_owned_entry(access, previous)
        return previous
    # A pre-existing grant is never modified or removed by this run.
    try:
        existing = access.request(entry=cidr)
    except AtlasNetworkError as exc:
        if exc.status_code != 404:
            raise
        existing = None
    created = existing is None
    receipt = {
        "schema_version": 1,
        "project_id": access.project_id,
        "cidr": cidr,
        "created": created,
        "comment": "job-intelligence:" + uuid.uuid4().hex if created else None,
        "created_at": _utc_text(now),
        "expires_at": _utc_text(now + MAX_GRANT_DURATION),
    }
    if existing is not None:
        receipt["observed_comment"] = existing.get("comment")
    # Save ownership before requesting: a retry can reconcile an uncertain POST.
    _write_receipt(receipt_path, receipt)
    if created:
        _ensure_owned_entry(access, receipt)
    return receipt


def revoke(access, receipt_path: Path) -> None:
    if not receipt_path.exists():
        return
    receipt = _read_receipt(receipt_path)
    _validate_receipt(receipt, access.project_id, receipt.get("cidr"), require_current=False)
    network = ipaddress.ip_network(receipt["cidr"], strict=True)
    if not receipt.get("created"):
        return
    _delete_owned_entry(access, str(network), receipt["comment"])


def _ensure_owned_entry(access, receipt: dict) -> None:
    cidr = receipt["cidr"]
    comment = receipt["comment"]
    payload = [
        {
            "cidrBlock": cidr,
            "comment": comment,
            "deleteAfterDate": receipt["expires_at"],
        }
    ]
    last_error: AtlasNetworkError | None = None
    for _ in range(RECONCILE_ATTEMPTS):
        try:
            row = access.request(entry=cidr)
        except AtlasNetworkError as exc:
            if exc.status_code != 404:
                last_error = exc
                continue
        else:
            _validate_owned_row(row, comment)
            return

        try:
            access.request("POST", payload=payload)
        except AtlasNetworkError as exc:
            last_error = exc

        try:
            row = access.request(entry=cidr)
        except AtlasNetworkError as exc:
            if exc.status_code != 404:
                last_error = exc
            continue
        _validate_owned_row(row, comment)
        return
    message = "Atlas network entry could not be reconciled after an uncertain create"
    raise AtlasNetworkError(message) from last_error


def _validate_owned_row(row: dict, comment: str) -> None:
    if not isinstance(row, dict) or row.get("comment") != comment:
        raise AtlasNetworkError("network entry ownership changed")


def _delete_owned_entry(access, cidr: str, comment: str) -> None:
    last_error: AtlasNetworkError | None = None
    for _ in range(RECONCILE_ATTEMPTS):
        try:
            row = access.request(entry=cidr)
        except AtlasNetworkError as exc:
            if exc.status_code == 404:
                return
            last_error = exc
            continue
        if not isinstance(row, dict) or row.get("comment") != comment:
            raise AtlasNetworkError("network cleanup refuses another owner's entry")
        try:
            access.request("DELETE", entry=cidr)
        except AtlasNetworkError as exc:
            if exc.status_code == 404:
                return
            last_error = exc
        try:
            remaining = access.request(entry=cidr)
        except AtlasNetworkError as exc:
            if exc.status_code == 404:
                return
            last_error = exc
            continue
        if not isinstance(remaining, dict) or remaining.get("comment") != comment:
            raise AtlasNetworkError("network cleanup ownership changed during retry")
    raise AtlasNetworkError(
        "Atlas network entry deletion could not be reconciled"
    ) from last_error


def _read_receipt(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        raise AtlasNetworkError("network receipt is unreadable") from None
    if not isinstance(value, dict):
        raise AtlasNetworkError("network receipt must be an object")
    return value


def _write_receipt(path: Path, receipt: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle = tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        newline="\n",
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
        delete=False,
    )
    temporary = Path(handle.name)
    try:
        with handle:
            json.dump(receipt, handle, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _validate_receipt(
    receipt: dict,
    project_id: str,
    cidr: str | None,
    *,
    now: datetime | None = None,
    require_current: bool = True,
) -> None:
    if receipt.get("schema_version") != 1:
        raise AtlasNetworkError("unsupported network receipt schema")
    if receipt.get("project_id") != project_id or receipt.get("cidr") != cidr:
        raise AtlasNetworkError("network receipt belongs to another project or address")
    try:
        network = ipaddress.ip_network(str(receipt.get("cidr", "")), strict=True)
    except ValueError:
        raise AtlasNetworkError("network cleanup refuses an unsafe CIDR") from None
    if network.version != 4 or network.prefixlen != 32 or not network.network_address.is_global:
        raise AtlasNetworkError("network cleanup refuses an unsafe CIDR")
    expires_at = _parse_utc(receipt.get("expires_at"), "expires_at")
    created_at = (
        _parse_utc(receipt.get("created_at"), "created_at")
        if receipt.get("created_at") is not None
        else expires_at - MAX_GRANT_DURATION
    )
    duration = expires_at - created_at
    if duration <= timedelta(0) or duration > MAX_GRANT_DURATION:
        raise AtlasNetworkError("network receipt expiry exceeds the two-hour limit")
    if require_current and (now or datetime.now(timezone.utc)) >= expires_at:
        raise AtlasNetworkError("network receipt has expired")
    created = receipt.get("created")
    if not isinstance(created, bool):
        raise AtlasNetworkError("network receipt has invalid ownership state")
    comment = receipt.get("comment")
    if created and not re.fullmatch(r"job-intelligence:[a-f0-9]{32}", str(comment or "")):
        raise AtlasNetworkError("network receipt has invalid ownership comment")
    if not created and comment is not None:
        raise AtlasNetworkError("pre-existing network receipt must not claim ownership")


def _parse_utc(value, field: str) -> datetime:
    if not isinstance(value, str):
        raise AtlasNetworkError(f"network receipt has invalid {field}")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise AtlasNetworkError(f"network receipt has invalid {field}") from None
    return _utc_datetime(parsed, field)


def _utc_datetime(value: datetime, field: str) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise AtlasNetworkError(f"{field} must include a timezone")
    return value.astimezone(timezone.utc)


def _utc_text(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


def cli_main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=["grant", "revoke"])
    parser.add_argument("--receipt", type=Path, default=Path(".codex-work/atlas-network.json"))
    args = parser.parse_args(argv)
    try:
        args.receipt.resolve().relative_to((Path.cwd() / ".codex-work").resolve())
        access = AtlasAccess(os.environ.get("ATLAS_PROJECT_ID", ""),
                             os.environ.get("ATLAS_CLIENT_ID", ""),
                             os.environ.get("ATLAS_CLIENT_SECRET", ""))
        if args.operation == "grant":
            grant(access, public_runner_ip(), args.receipt)
        else:
            revoke(access, args.receipt)
        print("Atlas runner access " + args.operation + " verified")
        return 0
    except (AtlasNetworkError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(cli_main())
