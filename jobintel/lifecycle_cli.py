"""Record user-confirmed application history and publish grounded Codex drafts."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from pymongo.errors import PyMongoError

from .application_lifecycle import ApplicationLifecycle, DRAFT_KINDS, EVENT_KINDS, profile_questions


def main(argv=None, *, root: Path | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=root or Path(__file__).resolve().parents[1])
    commands = parser.add_subparsers(dest="command", required=True)
    submission = commands.add_parser("record-submission", help="record exact files already sent by the user")
    submission.add_argument("vacancy")
    submission.add_argument("--submission-id", required=True)
    submission.add_argument("--sent-on", required=True)
    submission.add_argument("--artifact", type=Path, action="append", required=True)
    submission.add_argument("--confirm-sent", action="store_true")
    for name in ("channel", "positioning", "format", "role-family"):
        submission.add_argument("--" + name)
    event = commands.add_parser("record-event", help="record an observed outcome without changing vacancy status")
    event.add_argument("vacancy")
    event.add_argument("--submission-id", required=True)
    event.add_argument("--event-id", required=True)
    event.add_argument("--kind", choices=sorted(EVENT_KINDS), required=True)
    event.add_argument("--occurred-on", required=True)
    event.add_argument("--note-file", type=Path)
    event.add_argument("--note-origin", choices=["employer_message", "user_description", "not_provided"], default="not_provided")
    verify = commands.add_parser("verify-submission", help="check immutable snapshots against canonical recorded hashes")
    verify.add_argument("vacancy")
    verify.add_argument("--submission-id", required=True)
    for command in ("report", "followups"):
        commands.add_parser(command).add_argument("--as-of")
    commands.add_parser("profile-questions")
    draft = commands.add_parser("publish-draft", help="validate a named-vacancy draft; never sends messages")
    draft.add_argument("vacancy")
    draft.add_argument("--kind", choices=sorted(DRAFT_KINDS), required=True)
    draft.add_argument("--draft", type=Path, required=True)
    draft.add_argument("--approved-vacancy", required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "profile-questions":
            print(json.dumps({"questions": profile_questions(args.project_root)}, ensure_ascii=False, indent=2))
            return 0
        lifecycle = ApplicationLifecycle(args.project_root)
        if args.command == "record-submission":
            result = lifecycle.record_submission(args.vacancy, submission_id=args.submission_id,
                sent_on=args.sent_on, artifacts=args.artifact, confirmed=args.confirm_sent,
                channel=args.channel, positioning=args.positioning, format=args.format, role_family=args.role_family)
        elif args.command == "record-event":
            note = None
            if args.note_file:
                with args.note_file.open(encoding="utf-8-sig", newline="") as handle:
                    note = handle.read()
            result = lifecycle.record_event(args.vacancy, submission_id=args.submission_id,
                event_id=args.event_id, kind=args.kind, occurred_on=args.occurred_on,
                note=note, note_origin=args.note_origin)
            if args.kind == "rejection":
                result = {**result, "status_action_required": "Use run.py status only on the user's explicit request; "
                          "preserve the full message in registry/feedback and the manual status audit note."}
        elif args.command == "verify-submission":
            result = lifecycle.verify_submission(args.vacancy, submission_id=args.submission_id)
        elif args.command == "report":
            result = lifecycle.report(as_of=args.as_of)
        elif args.command == "followups":
            result = lifecycle.followups(as_of=args.as_of)
        else:
            result = lifecycle.publish_draft(args.vacancy, kind=args.kind,
                draft=json.loads(args.draft.read_text(encoding="utf-8-sig")), approved_vacancy=args.approved_vacancy)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, RuntimeError, PyMongoError) as exc:
        print(f"Application lifecycle error: {exc}", file=sys.stderr)
        return 2


cli_main = main
