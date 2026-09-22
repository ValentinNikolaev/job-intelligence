from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
from contextlib import nullcontext
from datetime import date
from pathlib import Path
from unittest.mock import patch

from jobintel.application_lifecycle import ApplicationLifecycle


class MemoryStore:
    def __init__(self):
        self.documents = {}
        self.vacancies = [{"_id": "v1", "directory": "example-job", "meta": {"status": "analyzed"}}]

    def get(self, collection, key):
        return copy.deepcopy(self.documents.get((collection, key)))

    def put(self, collection, key, payload, *, expected_revision):
        previous = self.get(collection, key)
        assert expected_revision == (previous["revision"] if previous else 0)
        self.documents[(collection, key)] = {"_id": key, "revision": expected_revision + 1, **copy.deepcopy(payload)}

    def list(self, collection):
        return [copy.deepcopy(value) for (name, _), value in self.documents.items() if name == collection]

    def list_vacancies(self, **kwargs):
        return copy.deepcopy(self.vacancies)

    def lease(self, owner):
        return nullcontext()


class ApplicationLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.store = MemoryStore()
        self.lifecycle = ApplicationLifecycle(self.root, store=self.store, today=date(2026, 9, 22))
        self.cv = self.root / "registry/jobs/example-job/application/cv.md"
        self.cv.parent.mkdir(parents=True)
        self.cv.write_bytes(b"Original CV\n")
        self.source = self.root / "registry/candidate/cv.md"
        self.source.parent.mkdir(parents=True)
        self.source.write_text("Built PHP services at Example.\n", encoding="utf-8")
        profile = self.root / "config/application-profile.yaml"
        profile.parent.mkdir()
        profile.write_text("candidate:\n  full_name: Example Person\napplication_defaults:\n  notice_period: TODO_CONFIRM\n", encoding="utf-8")

    def submit(self, **kwargs):
        options = {"submission_id": "sent-1", "sent_on": "2026-09-01", "artifacts": [self.cv], "confirmed": True}
        return self.lifecycle.record_submission("v1", **{**options, **kwargs})

    def event(self, kind, **kwargs):
        options = {"submission_id": "sent-1", "event_id": kind, "occurred_on": "2026-09-04"}
        return self.lifecycle.record_event("v1", kind=kind, **{**options, **kwargs})

    def draft(self):
        return {"schema_version": 1, "vacancy_id": "v1", "kind": "answers", "grounding_review": True,
                "items": [{"prompt": "Relevant experience?", "text": "Built PHP services at Example.", "status": "confirmed",
                           "sources": [{"path": "registry/candidate/cv.md", "sha256": hashlib.sha256(self.source.read_bytes()).hexdigest(),
                                        "quote": "Built PHP services at Example."}]}]}

    def publish(self, draft=None, **kwargs):
        return self.lifecycle.publish_draft("v1", kind="answers", draft=draft or self.draft(), approved_vacancy=kwargs.get("approval", "v1"))

    def test_requires_mongodb_without_file_fallback(self):
        with patch("jobintel.application_lifecycle.storage_bridge.get_store", return_value=None):
            with self.assertRaisesRegex(RuntimeError, "fallback is disabled"):
                ApplicationLifecycle(self.root)

    def test_submission_copies_exact_bytes_and_survives_original_regeneration(self):
        result = self.submit()
        snapshot = self.root / result["snapshot"] / result["artifacts"][0]["snapshot"]
        self.cv.write_text("Regenerated CV", encoding="utf-8")
        self.assertEqual(snapshot.read_bytes(), b"Original CV\n")
        self.assertTrue(self.lifecycle.verify_submission("v1", submission_id="sent-1")["verified"])
        self.assertEqual(self.store.vacancies[0]["meta"]["status"], "analyzed")

    def test_snapshot_tampering_is_detected(self):
        result = self.submit()
        snapshot = self.root / result["snapshot"] / result["artifacts"][0]["snapshot"]
        snapshot.write_bytes(b"Different CV")
        with self.assertRaisesRegex(ValueError, "mismatch"):
            self.lifecycle.verify_submission("v1", submission_id="sent-1")

    def test_receipt_tampering_is_detected(self):
        result = self.submit()
        (self.root / result["snapshot"] / "receipt.json").write_text("{}", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "canonical history"):
            self.lifecycle.verify_submission("v1", submission_id="sent-1")

    def test_identical_retry_does_not_duplicate_submission(self):
        result = self.submit()
        self.assertEqual(self.submit(), result)
        self.assertEqual(self.lifecycle.report()["summary"]["submitted"], 1)

    def test_changed_retry_cannot_overwrite_snapshot(self):
        self.submit()
        self.cv.write_text("Changed", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "immutable"):
            self.submit()

    def test_duplicate_submission_new_id_is_rejected(self):
        self.submit()
        with self.assertRaisesRegex(ValueError, "already recorded"):
            self.submit(submission_id="duplicate")

    def test_confirmation_required(self):
        with self.assertRaisesRegex(ValueError, "explicit confirmation"):
            self.submit(confirmed=False)
        self.assertEqual(self.store.documents, {})

    def test_path_escape_and_other_vacancy_artifact_rejected(self):
        for artifact in [self.source, Path("../secret.md")]:
            with self.subTest(artifact=artifact), self.assertRaisesRegex(ValueError, "selected vacancy"):
                self.submit(artifacts=[artifact])

    def test_invalid_ids_dates_and_all_selector_rejected(self):
        with self.assertRaises(ValueError):
            self.submit(submission_id="../bad")
        with self.assertRaises(ValueError):
            self.submit(sent_on="2026-09-23")
        with self.assertRaises(ValueError):
            self.lifecycle.vacancy("all")

    def test_failed_database_write_can_retry_identical_snapshot(self):
        with patch.object(self.store, "put", side_effect=RuntimeError("temporary failure")):
            with self.assertRaises(RuntimeError):
                self.submit()
        self.assertEqual(self.lifecycle.report()["summary"]["submitted"], 0)
        self.submit()
        self.assertTrue(self.lifecycle.verify_submission("v1", submission_id="sent-1")["verified"])

    def test_outcome_requires_submission_and_valid_chronology(self):
        with self.assertRaisesRegex(ValueError, "confirmed submission"):
            self.event("human_reply")
        self.submit()
        with self.assertRaisesRegex(ValueError, "precede"):
            self.event("human_reply", occurred_on="2026-08-31")

    def test_event_is_idempotent_but_conflicting_id_and_duplicate_payload_rejected(self):
        self.submit()
        result = self.event("human_reply")
        self.assertEqual(self.event("human_reply"), result)
        with self.assertRaisesRegex(ValueError, "different content"):
            self.event("human_reply", occurred_on="2026-09-05")
        with self.assertRaisesRegex(ValueError, "already recorded"):
            self.event("human_reply", event_id="duplicate")

    def test_rejection_requires_original_message_or_user_description(self):
        self.submit()
        with self.assertRaisesRegex(ValueError, "full employer"):
            self.event("rejection")
        note = "Grazie.\r\n\r\nNon procederemo.\r\n"
        with self.assertRaisesRegex(ValueError, "first preserve"):
            self.event("rejection", note=note, note_origin="employer_message")
        feedback = self.root / "registry/feedback/example-job/2026-09-22-rejection.md"
        feedback.parent.mkdir(parents=True)
        feedback.write_bytes(note.encode("utf-8"))
        self.store.put("operational_logs", "manual-status-log.yaml", {"payload": {"events": [{
            "vacancy_id": "v1", "to_status": "rejected", "changed_at": "2026-09-22T10:00:00Z",
            "note": note + "\nregistry/feedback/example-job/2026-09-22-rejection.md"}]}}, expected_revision=0)
        event = self.event("rejection", note=note, note_origin="employer_message")
        self.assertEqual(event["note"], note)
        self.assertIn("recorded_at", event)
        self.assertEqual(event["occurred_on"], "2026-09-04")
        self.assertEqual(self.store.vacancies[0]["meta"]["status"], "analyzed")
        report = self.lifecycle.report()["summary"]
        self.assertEqual(report["rejections"], 1)
        self.assertEqual(report["human_responses"], 0)
        self.assertEqual(report["pending_censored"], 0)

    def test_autoack_is_not_a_human_response_or_invitation(self):
        self.submit()
        self.event("auto_ack")
        report = self.lifecycle.report()["summary"]
        self.assertEqual((report["submitted"], report["auto_acknowledged"], report["human_responses"], report["interview_invitations"]), (1, 1, 0, 0))
        self.assertEqual(report["pending_censored"], 1)
        self.assertIsNone(report["median_days_to_human_response_among_responders"])

    def test_invitation_and_response_delay_are_measured_per_submission(self):
        self.submit(channel="referral", positioning="Backend", format="compact")
        self.event("auto_ack", occurred_on="2026-09-02")
        self.event("interview_invitation", occurred_on="2026-09-05")
        self.event("interview", occurred_on="2026-09-08")
        report = self.lifecycle.report()
        summary = report["summary"]
        self.assertEqual(summary["interview_invitations"], 1)
        self.assertEqual(summary["human_responses"], 1)
        self.assertEqual(summary["median_days_to_human_response_among_responders"], 4)
        self.assertEqual(summary["pending_censored"], 0)
        self.assertIn("referral", report["segments"]["channel"])
        self.assertLess(summary["invitation_rate_wilson_95"][0], 0.5)
        self.assertIsNone(summary["strategy_recommendation"])

    def test_as_of_excludes_later_outcomes_and_submissions(self):
        self.submit()
        self.event("interview_invitation", occurred_on="2026-09-05")
        self.assertEqual(self.lifecycle.report(as_of="2026-09-03")["summary"]["interview_invitations"], 0)
        self.assertEqual(self.lifecycle.report(as_of="2026-08-31")["summary"]["submitted"], 0)

    def test_history_survives_vacancy_removal_and_empty_report_is_honest(self):
        self.assertIsNone(self.lifecycle.report()["summary"]["invitation_rate"])
        self.submit()
        self.store.vacancies.clear()
        self.assertEqual(self.lifecycle.report()["summary"]["submitted"], 1)
        self.assertIn("not_provided", self.lifecycle.report()["segments"]["channel"])

    def test_followups_advance_only_after_user_recorded_send_and_stop_after_two(self):
        self.submit()
        before = copy.deepcopy(self.store.documents)
        suggestion = self.lifecycle.followups()["suggestions"][0]
        self.assertEqual(suggestion["due_on"], "2026-09-08")
        self.assertEqual(before, self.store.documents)
        self.event("followup_sent", occurred_on="2026-09-10")
        self.assertEqual(self.lifecycle.followups()["suggestions"][0]["due_on"], "2026-09-17")
        self.event("followup_sent", event_id="followup-2", occurred_on="2026-09-18")
        self.assertEqual(self.lifecycle.followups()["suggestions"], [])

    def test_followups_stop_after_reply(self):
        self.submit()
        self.event("human_reply")
        self.assertEqual(self.lifecycle.followups()["suggestions"], [])

    def test_followup_policy_controls_spacing_and_maximum(self):
        self.submit()
        config = self.root / "config/application-lifecycle.yaml"
        config.write_text("schema_version: 1\nfollowups:\n  spacing_days: 10\n  max_followups: 1\n", encoding="utf-8")
        self.assertEqual(self.lifecycle.followups()["suggestions"][0]["due_on"], "2026-09-11")
        self.event("followup_sent", occurred_on="2026-09-12")
        self.assertEqual(self.lifecycle.followups()["suggestions"], [])
        config.write_text("schema_version: 1\nfollowups:\n  max_followups: 0\n", encoding="utf-8")
        self.assertEqual(self.lifecycle.followups()["suggestions"], [])

    def test_followup_policy_rejects_booleans_and_invalid_bounds(self):
        config = self.root / "config/application-lifecycle.yaml"
        for field, value in [("spacing_days", "true"), ("spacing_days", "0"), ("spacing_days", "366"),
                             ("max_followups", "true"), ("max_followups", "-1"), ("max_followups", "11"),
                             ("max_followups", "1.5")]:
            with self.subTest(field=field, value=value):
                config.write_text(f"schema_version: 1\nfollowups:\n  {field}: {value}\n", encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "integer"):
                    self.lifecycle.followups()

    def test_grounded_draft_exports_plain_text_idempotently(self):
        result = self.publish()
        self.assertFalse(result["sent"])
        self.assertEqual(self.publish(), result)
        self.assertIn("Built PHP services", (self.root / result["path"] / "document.txt").read_text(encoding="utf-8"))
        self.assertEqual(self.store.documents, {})

    def test_wrong_vacancy_or_missing_approval_cannot_publish(self):
        with self.assertRaisesRegex(ValueError, "explicit approval"):
            self.publish(approval="v2")
        draft = self.draft()
        draft["vacancy_id"] = "v2"
        with self.assertRaisesRegex(ValueError, "canonical vacancy"):
            self.publish(draft)

    def test_fabricated_quote_stale_source_and_output_as_evidence_rejected(self):
        draft = self.draft()
        draft["items"][0]["sources"][0]["quote"] = "Managed 100 engineers"
        with self.assertRaisesRegex(ValueError, "quote"):
            self.publish(draft)
        draft = self.draft()
        self.source.write_text("Updated evidence", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "hash"):
            self.publish(draft)
        draft = self.draft()
        draft["items"][0]["sources"][0]["path"] = str(self.cv)
        with self.assertRaisesRegex(ValueError, "immutable candidate"):
            self.publish(draft)

    def test_unknown_profile_field_cannot_be_used_as_confirmed_answer(self):
        draft = self.draft()
        draft["items"] = [{"prompt": "Notice?", "profile_field": "application_defaults.notice_period", "text": "Two weeks", "status": "confirmed"}]
        with self.assertRaisesRegex(ValueError, "unknown"):
            self.publish(draft)
        self.assertEqual(self.lifecycle.profile_questions()[0]["field"], "application_defaults.notice_period")
        draft["items"][0].update(text="", status="needs_confirmation")
        self.assertEqual(self.publish(draft)["needs_confirmation"], 1)

    def test_confirmed_profile_answer_must_match_exactly(self):
        draft = self.draft()
        draft["items"] = [{"prompt": "Name?", "profile_field": "candidate.full_name", "text": "Another Person", "status": "confirmed"}]
        with self.assertRaisesRegex(ValueError, "conflicts"):
            self.publish(draft)
        draft["items"][0]["text"] = "Example Person"
        self.publish(draft)

    def test_unconfirmed_answer_cannot_smuggle_guessed_claim(self):
        draft = self.draft()
        draft["items"][0].update(status="needs_confirmation", text="Probably eligible to work in EU")
        with self.assertRaisesRegex(ValueError, "unconfirmed"):
            self.publish(draft)

    def test_unconfirmed_items_are_marked_in_markdown_and_excluded_from_paste_text(self):
        draft = self.draft()
        draft["items"].append({"prompt": "Visa sponsorship?", "text": "Needs candidate confirmation.",
                               "status": "needs_confirmation"})
        result = self.publish(draft)
        destination = self.root / result["path"]
        markdown = (destination / "document.md").read_text(encoding="utf-8")
        paste = (destination / "document.txt").read_text(encoding="utf-8")
        self.assertIn("Visa sponsorship?", markdown)
        self.assertIn("**Needs candidate confirmation.**", markdown)
        self.assertNotIn("Visa sponsorship?", paste)
        self.assertNotIn("Needs candidate confirmation.", paste)
        self.assertIn("Built PHP services", paste)
        self.assertEqual(json.loads((destination / "draft.json").read_text(encoding="utf-8")), draft)

    def test_all_pending_items_produce_empty_paste_text(self):
        draft = self.draft()
        draft["items"] = [{"prompt": "Salary?", "text": "", "status": "needs_confirmation"}]
        result = self.publish(draft)
        self.assertEqual((self.root / result["path"] / "document.txt").read_bytes(), b"")

    def test_user_statement_is_preserved_as_durable_evidence(self):
        source = self.root / ".codex-work/interview-note.txt"
        source.parent.mkdir()
        source.write_text("I was asked about caching.", encoding="utf-8")
        draft = self.draft()
        draft["items"][0]["sources"] = [{"path": ".codex-work/interview-note.txt", "kind": "user_statement",
            "sha256": hashlib.sha256(source.read_bytes()).hexdigest(), "quote": "I was asked about caching."}]
        draft["items"][0]["text"] = "I was asked about caching."
        result = self.publish(draft)
        self.assertEqual(len(list((self.root / result["path"] / "sources").glob("*.txt"))), 1)

    def test_malformed_draft_returns_validation_error(self):
        with self.assertRaisesRegex(ValueError, "JSON object"):
            self.lifecycle.publish_draft("v1", kind="answers", draft=[], approved_vacancy="v1")


if __name__ == "__main__":
    unittest.main()
