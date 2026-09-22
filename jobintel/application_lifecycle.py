"""MongoDB application events and immutable copies of submitted/ancillary artifacts."""
from __future__ import annotations

import hashlib
import json
import math
import re
import shutil
import tempfile
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from statistics import median

import yaml

from . import storage_bridge

EVENT_KINDS = frozenset({"auto_ack", "human_reply", "interview_invitation", "interview",
                         "offer", "rejection", "withdrawal", "followup_sent"})
HUMAN_KINDS = frozenset({"human_reply", "interview_invitation", "interview", "offer"})
CLOSED_KINDS = frozenset({"offer", "rejection", "withdrawal"})
DRAFT_KINDS = frozenset({"answers", "interview-practice", "interview-debrief", "followup"})
_KEY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,199}$")
_UNRESOLVED = {"", "TODO_CONFIRM", "unknown", "not_provided", "needs_confirmation"}


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _json(value) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def _key(value: str) -> str:
    if not isinstance(value, str) or not _KEY.fullmatch(value) or value.casefold() in {
        "con", "prn", "aux", "nul", *(f"com{i}" for i in range(1, 10)), *(f"lpt{i}" for i in range(1, 10))
    }:
        raise ValueError("IDs must be safe, explicit alphanumeric keys (with '-' or '_')")
    return value


def _date(value: str, today: date) -> date:
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise ValueError("dates must use YYYY-MM-DD")
    result = date.fromisoformat(value)
    if result > today:
        raise ValueError("observed event dates cannot be in the future")
    return result


def _label(value: str | None) -> str:
    if value is None or not str(value).strip():
        return "not_provided"
    if len(str(value)) > 160:
        raise ValueError("segment labels must be at most 160 characters")
    return str(value).strip()


def _interval(successes: int, total: int) -> list[float] | None:
    if not total:
        return None
    z, p = 1.96, successes / total
    denominator = 1 + z * z / total
    center = (p + z * z / (2 * total)) / denominator
    radius = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / denominator
    return [round(max(0, center - radius), 4), round(min(1, center + radius), 4)]


def _load_profile(root: Path) -> dict:
    path = root / "config/application-profile.yaml"
    try:
        profile = (yaml.safe_load(path.read_text(encoding="utf-8")) or {}) if path.is_file() else {}
    except yaml.YAMLError as exc:
        raise ValueError("application profile is not valid YAML") from exc
    if not isinstance(profile, dict):
        raise ValueError("application profile must be a mapping")
    return profile


def profile_questions(root: Path) -> list[dict]:
    """Inspect unresolved local profile fields without accessing operational storage."""
    questions = []

    def walk(value, prefix=""):
        if isinstance(value, dict):
            for key, child in value.items():
                walk(child, f"{prefix}.{key}".lstrip("."))
        elif value is None or isinstance(value, str) and value.strip() in _UNRESOLVED:
            questions.append({"field": prefix, "value": value, "status": "needs_confirmation"})

    walk(_load_profile(root))
    return questions


class ApplicationLifecycle:
    def __init__(self, root: Path, *, store=None, today: date | None = None):
        self.root = root.resolve()
        self.store = store if store is not None else storage_bridge.get_store(self.root)
        if self.store is None:
            raise RuntimeError("application lifecycle requires MongoDB; file fallback is disabled")
        self.today = today or date.today()

    def vacancy(self, selector: str) -> dict:
        if not selector or selector.casefold() == "all":
            raise ValueError("select exactly one vacancy by ID or directory")
        candidates = self.store.list_vacancies(scope="jobs", include_archived=True)
        found = [v for v in candidates if selector in {str(v["_id"]), v["directory"]}]
        if len(found) != 1:
            raise ValueError("vacancy selector must resolve to exactly one canonical MongoDB record")
        _key(str(found[0]["_id"]))
        _key(found[0]["directory"])
        return found[0]

    def _log(self, vacancy_id: str) -> tuple[dict | None, list]:
        previous = self.store.get("operational_logs", "application-lifecycle:" + vacancy_id)
        return previous, list((previous or {}).get("payload", {}).get("events", []))

    def _append(self, vacancy: dict, event: dict) -> dict:
        previous, events = self._log(str(vacancy["_id"]))
        old = next((e for e in events if e["event_id"] == event["event_id"]), None)
        if old is not None:
            if {k: v for k, v in old.items() if k != "recorded_at"} != event:
                raise ValueError("event ID already exists with different content")
            return old
        event = {**event, "recorded_at": datetime.now(timezone.utc).isoformat()}
        events.append(event)
        self.store.put("operational_logs", "application-lifecycle:" + str(vacancy["_id"]), {
            "payload": {"schema_version": 1, "vacancy_id": str(vacancy["_id"]),
                        "directory": vacancy["directory"], "events": events}},
            expected_revision=previous["revision"] if previous else 0)
        return event

    def _bundle(self, destination: Path, files: dict[str, bytes]) -> None:
        """Publish a directory atomically; retry may reuse an identical complete bundle."""
        destination.resolve().relative_to((self.root / "registry/application-history").resolve())
        if destination.exists():
            actual = {p.relative_to(destination).as_posix(): p.read_bytes()
                      for p in destination.rglob("*") if p.is_file()}
            if actual != files:
                raise ValueError("immutable artifact bundle exists with different or corrupted content")
            return
        destination.parent.mkdir(parents=True, exist_ok=True)
        staging = Path(tempfile.mkdtemp(prefix=".lifecycle-", dir=destination.parent))
        try:
            for name, data in files.items():
                target = staging / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
            staging.rename(destination)
        finally:
            if staging.exists():
                staging.resolve().relative_to(destination.parent.resolve())
                shutil.rmtree(staging)

    def record_submission(self, selector: str, *, submission_id: str, sent_on: str,
                          artifacts: list[Path], confirmed: bool, channel: str | None = None,
                          positioning: str | None = None, format: str | None = None,
                          role_family: str | None = None) -> dict:
        if not confirmed:
            raise ValueError("recording requires explicit confirmation that the user sent these exact files")
        vacancy = self.vacancy(selector)
        _key(submission_id)
        _date(sent_on, self.today)
        if not 1 <= len(artifacts) <= 10:
            raise ValueError("select one to ten exact CV/letter files that were sent")
        package_root = self.root / "registry/jobs" / vacancy["directory"]
        files, receipts = {}, []
        for source in artifacts:
            path = (self.root / source).resolve()
            try:
                relative = path.relative_to(package_root.resolve())
            except ValueError:
                raise ValueError("sent artifacts must belong to the selected vacancy's application package") from None
            if len(relative.parts) < 2 or not relative.parts[0].startswith("application"):
                raise ValueError("sent artifacts must come from an application package")
            if path.suffix.lower() not in {".md", ".txt", ".docx", ".pdf"}:
                raise ValueError("unsupported sent artifact format")
            data = path.read_bytes()
            if not data:
                raise ValueError("sent artifact is empty")
            name = "files/" + relative.as_posix()
            if name in files:
                raise ValueError("a sent artifact was selected twice")
            files[name] = data
            receipts.append({"source": path.relative_to(self.root).as_posix(), "snapshot": name,
                             "sha256": _sha(data), "size": len(data)})
        destination = self.root / "registry/application-history" / str(vacancy["_id"]) / "submissions" / submission_id
        event = {"event_id": "submission:" + submission_id, "kind": "submission",
                 "submission_id": submission_id, "occurred_on": sent_on,
                 "channel": _label(channel), "positioning": _label(positioning),
                 "format": _label(format), "role_family": _label(role_family),
                 "artifacts": sorted(receipts, key=lambda r: r["source"]),
                 "snapshot": destination.relative_to(self.root).as_posix()}
        files["receipt.json"] = _json({"schema_version": 1, "vacancy_id": str(vacancy["_id"]), **event})
        with self.store.lease("application-lifecycle:record-submission"):
            _, events = self._log(str(vacancy["_id"]))
            if any(e["kind"] == "submission" and e["submission_id"] != submission_id and
                   e["occurred_on"] == sent_on and e["artifacts"] == event["artifacts"] for e in events):
                raise ValueError("identical submission already recorded; reuse its submission ID")
            self._bundle(destination, files)
            return self._append(vacancy, event)

    def verify_submission(self, selector: str, *, submission_id: str) -> dict:
        vacancy = self.vacancy(selector)
        _, events = self._log(str(vacancy["_id"]))
        event = next((e for e in events if e["kind"] == "submission" and e["submission_id"] == submission_id), None)
        if event is None:
            raise ValueError("unknown submission")
        destination = (self.root / event["snapshot"]).resolve()
        destination.relative_to((self.root / "registry/application-history").resolve())
        receipt = json.loads((destination / "receipt.json").read_text(encoding="utf-8"))
        expected = {"schema_version": 1, "vacancy_id": str(vacancy["_id"]),
                    **{k: v for k, v in event.items() if k != "recorded_at"}}
        if receipt != expected:
            raise ValueError("submission receipt differs from canonical history")
        for artifact in event["artifacts"]:
            path = (destination / artifact["snapshot"]).resolve()
            path.relative_to(destination)
            data = path.read_bytes()
            if len(data) != artifact["size"] or _sha(data) != artifact["sha256"]:
                raise ValueError("submission snapshot hash or size mismatch")
        return {"verified": True, "submission_id": submission_id,
                "vacancy_id": str(vacancy["_id"]), "artifacts": len(event["artifacts"])}

    def record_event(self, selector: str, *, submission_id: str, event_id: str,
                     kind: str, occurred_on: str, note: str | None = None,
                     note_origin: str = "not_provided") -> dict:
        vacancy = self.vacancy(selector)
        _key(submission_id)
        _key(event_id)
        observed = _date(occurred_on, self.today)
        if kind not in EVENT_KINDS:
            raise ValueError("unsupported lifecycle event kind")
        if note_origin not in {"employer_message", "user_description", "not_provided"}:
            raise ValueError("note_origin must distinguish employer message from user description")
        if (note is None) != (note_origin == "not_provided"):
            raise ValueError("supply both note text and its explicit origin, or neither")
        if note is not None and not note.strip():
            raise ValueError("note text is empty")
        if kind == "rejection" and note is None:
            raise ValueError("rejection requires the full employer message or the user's description")
        event = {"event_id": event_id, "submission_id": submission_id, "kind": kind,
                 "occurred_on": occurred_on, "note": note, "note_origin": note_origin}
        with self.store.lease("application-lifecycle:record-event"):
            _, events = self._log(str(vacancy["_id"]))
            submission = next((e for e in events if e["kind"] == "submission" and e["submission_id"] == submission_id), None)
            if submission is None:
                raise ValueError("record a confirmed submission before its outcomes")
            if observed < date.fromisoformat(submission["occurred_on"]):
                raise ValueError("an outcome cannot precede its submission")
            if kind == "rejection":
                event.update(self._rejection_provenance(vacancy, note))
            if any(e["event_id"] != event_id and {k: v for k, v in e.items() if k not in {"event_id", "recorded_at"}} ==
                   {k: v for k, v in event.items() if k != "event_id"} for e in events):
                raise ValueError("identical outcome already recorded; reuse its event ID")
            return self._append(vacancy, event)

    def _rejection_provenance(self, vacancy: dict, note: str) -> dict:
        audit = self.store.get("operational_logs", "manual-status-log.yaml") or {}
        history = audit.get("payload", {}).get("events", [])
        feedback_root = self.root / "registry/feedback" / vacancy["directory"]
        for path in sorted(feedback_root.glob("????-??-??-rejection.md")):
            text = path.read_bytes().decode("utf-8-sig")
            if note.strip() not in text:
                continue
            relative = path.relative_to(self.root).as_posix()
            for event in reversed(history):
                audit_note = event.get("note") or ""
                if (str(event.get("vacancy_id")) == str(vacancy["_id"]) and event.get("to_status") == "rejected"
                    and note.strip() in audit_note and relative in audit_note.replace("\\", "/")):
                    return {"feedback_file": relative, "status_audit_changed_at": event.get("changed_at")}
        raise ValueError("first preserve the rejection in registry/feedback and the manual run.py status audit note; "
                         "this command cannot change status or bypass the user-requested rejection workflow")

    def _rows(self, as_of: date) -> list[dict]:
        rows = []
        for doc in self.store.list("operational_logs"):
            if not str(doc["_id"]).startswith("application-lifecycle:"):
                continue
            history = doc["payload"]
            events = [e for e in history["events"] if date.fromisoformat(e["occurred_on"]) <= as_of]
            for submission in (e for e in events if e["kind"] == "submission"):
                outcomes = [e for e in events if e["submission_id"] == submission["submission_id"] and e["kind"] != "submission"]
                rows.append({**submission, "vacancy_id": history["vacancy_id"], "directory": history["directory"], "outcomes": outcomes})
        return rows

    @staticmethod
    def _summary(rows: list[dict], as_of: date) -> dict:
        invited = replied = acknowledged = pending = closed = rejected = 0
        delays, response_delays = [], []
        for row in rows:
            kinds = {e["kind"] for e in row["outcomes"]}
            invited += "interview_invitation" in kinds
            acknowledged += "auto_ack" in kinds
            rejected += "rejection" in kinds
            human = [e for e in row["outcomes"] if e["kind"] in HUMAN_KINDS]
            replied += bool(human)
            closed += bool(kinds & CLOSED_KINDS)
            pending += not human and not kinds & CLOSED_KINDS
            if human:
                delays.append((min(date.fromisoformat(e["occurred_on"]) for e in human) - date.fromisoformat(row["occurred_on"])).days)
            responses = [e for e in row["outcomes"] if e["kind"] in HUMAN_KINDS | {"rejection"}]
            if responses:
                response_delays.append((min(date.fromisoformat(e["occurred_on"]) for e in responses) - date.fromisoformat(row["occurred_on"])).days)
        count = len(rows)
        return {"submitted": count, "unique_vacancies": len({r["vacancy_id"] for r in rows}),
                "interview_invitations": invited, "invitation_rate": invited / count if count else None,
                "invitation_rate_wilson_95": _interval(invited, count), "human_responses": replied,
                "auto_acknowledged": acknowledged, "pending_censored": pending, "closed": closed,
                "rejections": rejected,
                "observed_at_least_14_days": sum((as_of - date.fromisoformat(r["occurred_on"])).days >= 14 for r in rows),
                "median_days_to_human_response_among_responders": median(delays) if delays else None,
                "median_days_to_response_among_responders": median(response_delays) if response_delays else None,
                "strategy_recommendation": None}

    def report(self, *, as_of: str | None = None) -> dict:
        cutoff = _date(as_of or self.today.isoformat(), self.today)
        rows = self._rows(cutoff)
        groups = {}
        for dimension in ("channel", "positioning", "format", "role_family"):
            groups[dimension] = {label: self._summary([r for r in rows if r[dimension] == label], cutoff)
                                 for label in sorted({r[dimension] for r in rows})}
        return {"as_of": cutoff.isoformat(), "summary": self._summary(rows, cutoff), "segments": groups,
                "interpretation": "Observed invitations / confirmed submissions. Pending applications are censored, not rejections. "
                "Intervals are descriptive and assume independent observations; repeated vacancies, unequal follow-up, "
                "small samples and selection effects limit comparisons. No causal or automatic strategy recommendations.",
                "profile_questions": self.profile_questions()}

    def followups(self, *, as_of: str | None = None) -> dict:
        cutoff = _date(as_of or self.today.isoformat(), self.today)
        path = self.root / "config/application-lifecycle.yaml"
        try:
            config = yaml.safe_load(path.read_text(encoding="utf-8")) if path.is_file() else {"schema_version": 1}
        except yaml.YAMLError as exc:
            raise ValueError("application lifecycle configuration is not valid YAML") from exc
        if not isinstance(config, dict) or type(config.get("schema_version")) is not int or config["schema_version"] != 1:
            raise ValueError("application lifecycle configuration requires schema_version 1")
        policy = config.get("followups", {})
        if not isinstance(policy, dict):
            raise ValueError("followups policy must be a mapping")
        spacing = policy.get("spacing_days", 7)
        maximum = policy.get("max_followups", 2)
        if type(spacing) is not int or not 1 <= spacing <= 365:
            raise ValueError("followup spacing_days must be an integer from 1 to 365")
        if type(maximum) is not int or not 0 <= maximum <= 10:
            raise ValueError("max_followups must be an integer from 0 to 10")
        suggestions = []
        for row in self._rows(cutoff):
            if any(e["kind"] in HUMAN_KINDS | CLOSED_KINDS for e in row["outcomes"]):
                continue
            sent = sorted(e["occurred_on"] for e in row["outcomes"] if e["kind"] == "followup_sent")
            if len(sent) >= maximum:
                continue
            base = date.fromisoformat(sent[-1] if sent else row["occurred_on"])
            due = base + timedelta(days=spacing)
            suggestions.append({"vacancy_id": row["vacancy_id"], "directory": row["directory"],
                                "submission_id": row["submission_id"], "followup_number": len(sent) + 1,
                                "due_on": due.isoformat(), "due": due <= cutoff,
                                "action": "Review channel and employer instructions; request a named-vacancy draft if useful. No message is sent."})
        return {"as_of": cutoff.isoformat(), "suggestions": suggestions, "automatic_send": False,
                "policy": {"spacing_days": spacing, "max_followups": maximum}}

    def _profile(self) -> dict:
        return _load_profile(self.root)

    def profile_questions(self) -> list[dict]:
        return profile_questions(self.root)

    def publish_draft(self, selector: str, *, kind: str, draft: dict, approved_vacancy: str) -> dict:
        vacancy = self.vacancy(selector)
        if approved_vacancy not in {str(vacancy["_id"]), vacancy["directory"]}:
            raise ValueError("preparation requires explicit approval identifying this vacancy")
        if not isinstance(draft, dict):
            raise ValueError("draft must be a JSON object")
        if kind not in DRAFT_KINDS or draft.get("kind") != kind:
            raise ValueError("draft kind does not match the selected document")
        if draft.get("schema_version") != 1 or draft.get("vacancy_id") != str(vacancy["_id"]):
            raise ValueError("draft must use schema_version 1 and the exact canonical vacancy ID")
        if draft.get("grounding_review") is not True:
            raise ValueError("Codex final grounding review is required")
        items = draft.get("items")
        if not isinstance(items, list) or not 1 <= len(items) <= 100:
            raise ValueError("draft must contain 1-100 structured items")
        source_files = {}
        for item in items:
            if not isinstance(item, dict) or not isinstance(item.get("prompt"), str) or not item["prompt"].strip():
                raise ValueError("each item requires a question or section prompt")
            if item.get("status") not in {"confirmed", "needs_confirmation"}:
                raise ValueError("each item must explicitly state confirmed or needs_confirmation")
            text = item.get("text")
            if not isinstance(text, str):
                raise ValueError("each item requires text")
            if item["status"] == "needs_confirmation":
                if text.strip() not in {"", "Needs candidate confirmation."}:
                    raise ValueError("unconfirmed items cannot publish a proposed factual answer")
                continue
            if not text.strip() or "TODO_CONFIRM" in text:
                raise ValueError("confirmed answer contains an unresolved placeholder")
            field = item.get("profile_field")
            if field:
                if not isinstance(field, str):
                    raise ValueError("profile_field must be a dot-separated string")
                value = self._profile()
                for part in field.split("."):
                    value = value.get(part) if isinstance(value, dict) else None
                if value is None or isinstance(value, (dict, list)) or str(value).strip() in _UNRESOLVED:
                    raise ValueError("profile field is unknown; request candidate confirmation")
                if text.strip() != str(value).strip():
                    raise ValueError("answer conflicts with the confirmed profile field; preserve its exact value")
                continue
            sources = item.get("sources")
            if not isinstance(sources, list) or not sources:
                raise ValueError("confirmed factual answers require source evidence")
            for source in sources:
                if not isinstance(source, dict):
                    raise ValueError("source evidence must be an object")
                path = (self.root / str(source.get("path", ""))).resolve()
                try:
                    relative = path.relative_to(self.root).as_posix()
                except ValueError:
                    raise ValueError("evidence source must stay inside the project") from None
                candidate = relative.startswith("registry/candidate/") and path.suffix.lower() == ".md"
                statement = relative.startswith(".codex-work/") and source.get("kind") == "user_statement"
                if not (candidate or statement):
                    raise ValueError("use immutable candidate evidence or an explicitly identified user statement")
                data = path.read_bytes()
                if source.get("sha256") != _sha(data):
                    raise ValueError("evidence source hash is stale or incorrect")
                quote = source.get("quote")
                if not isinstance(quote, str) or not quote.strip() or quote not in data.decode("utf-8-sig"):
                    raise ValueError("evidence quote is absent from its source")
                if statement:
                    source_files["sources/" + _sha(data) + ".txt"] = data
        payload = _json(draft)
        digest = _sha(payload)
        destination = self.root / "registry/application-history" / str(vacancy["_id"]) / "drafts" / kind / digest
        markdown = "\n\n".join(
            f"## {i['prompt']}\n\n" + (i["text"] if i["status"] == "confirmed"
                                       else "**Needs candidate confirmation.**")
            for i in items) + "\n"
        plain = "\n\n".join(f"{i['prompt']}\n{i['text']}" for i in items if i["status"] == "confirmed")
        if plain:
            plain += "\n"
        files = {"draft.json": payload, "document.md": markdown.encode("utf-8"), "document.txt": plain.encode("utf-8"), **source_files}
        with self.store.lease("application-lifecycle:publish-draft"):
            self._bundle(destination, files)
        return {"kind": kind, "vacancy_id": str(vacancy["_id"]), "sha256": digest,
                "path": destination.relative_to(self.root).as_posix(),
                "needs_confirmation": sum(i["status"] == "needs_confirmation" for i in items), "sent": False}
