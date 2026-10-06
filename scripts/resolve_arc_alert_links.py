"""Stage authenticated Arc HTML mail and authorized job-link destinations."""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from email.utils import parseaddr
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from jobintel.arc_alerts import go_php_cards, resolve_tracking


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="Ignored JSON array of Gmail full messages")
    parser.add_argument("--output", type=Path, required=True, help="Ignored Arc evidence batch")
    parser.add_argument("--allow-job-redirects", action="store_true", help="User authorized Arc job-card HEAD requests")
    args = parser.parse_args()
    if not args.allow_job_redirects:
        parser.error("Arc job-card redirect resolution needs explicit user authorization")
    emails = []
    report = {"emails": 0, "selected": 0, "off_profile": 0, "unresolved": 0}
    for message in json.loads(args.input.read_text(encoding="utf-8")):
        payload = message["payload"]
        headers = {h["name"].lower(): h["value"] for h in payload["headers"]}
        if parseaddr(headers.get("from", ""))[1].lower() != "talent@arc.dev":
            raise ValueError("unexpected Arc sender")
        auth = headers.get("authentication-results", "")
        if any(re.search(rf"\b{check}=fail\b", auth) for check in ("dkim", "spf", "dmarc")):
            raise ValueError("Arc sender authentication failed")
        parts = [payload]
        body = None
        while parts:
            part = parts.pop()
            if part["mime_type"] == "text/html":
                body = part["body"]["content"]
                break
            parts.extend(part.get("parts") or [])
        if body is None:
            raise ValueError("Arc HTML message body unavailable")
        cards, off_profile = go_php_cards(body)
        report["off_profile"] += off_profile
        resolved = {}
        jobs = []
        for card in cards:
            try:
                destination = resolve_tracking(card["source_url"])
            except (ValueError, OSError):
                report["unresolved"] += 1
                continue
            resolved[card["source_url"]] = destination
            jobs.append(dict(card, source_url=destination))
        report["emails"] += 1
        report["selected"] += len(jobs)
        if jobs:
            emails.append({"message_id": message["id"], "sender": headers["from"], "subject": headers["subject"],
                           "received_at": datetime.fromtimestamp(int(message["internal_date"]) / 1000, timezone.utc).isoformat(),
                           "body_html": body, "resolved_links": resolved, "jobs": jobs})
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps({"schema_version": 1, "emails": emails}), encoding="utf-8")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
