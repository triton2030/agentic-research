"""Regression cases for record identity, source occurrences and corpus transactions."""
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

SCRIPTS = Path(__file__).parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
spec = importlib.util.spec_from_file_location("repair_digest", SCRIPTS / "chat_digest.py")
digest = importlib.util.module_from_spec(spec)
spec.loader.exec_module(digest)


class IdentityRepairTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.corpus = self.root / "_ops/chat-recall"
        self.corpus.mkdir(parents=True)
        (self.corpus / "topics.md").write_text("# Карта тем\n\n- `scenes` — Сцены\n")

    def tearDown(self):
        self.temp.cleanup()

    def command(self, quote="да", timestamp="2026-09-22T10:00:00Z", *options):
        return [sys.executable, str(SCRIPTS / "chat_capture.py"), "--project", str(self.root),
                "--agent", "codex", "--session", "11111111-2222-3333-4444-555555555555",
                "--quote", quote, "--type", "решение", "--topic", "scenes",
                "--source-timestamp", timestamp, "--context-note", "Сцены; выбранный вариант",
                "--session-context", "Сцены; модель каталога", "--supersedes-none", "--json", *options]

    def capture(self, *args):
        result = subprocess.run(self.command(*args), capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def records(self):
        return digest.load(self.corpus)[0]

    def test_receipt_and_retrieval_keep_same_anchor_after_header_growth_and_backfill(self):
        first = self.capture()
        self.assertRegex(first["anchor"], r"\.md#recall-[a-f0-9]{32}$")
        self.capture("другая тема", "2026-09-22T10:01:00Z", "--topic", "other", "--new-topic", "Вторая тема")
        self.capture("ранняя реплика", "2025-01-01T00:00:00Z")
        self.assertTrue(Path(first["path"]).exists(), "published file path was renamed")
        record = next(r for r in self.records() if r["text"] == "да")
        self.assertEqual(record["address"], first["anchor"])
        self.assertEqual(record["record_id"], first["record_id"])

    def test_same_words_at_two_source_times_are_distinct(self):
        first = self.capture()
        second = self.capture("да", "2026-09-22T10:01:00Z")
        self.assertEqual(second["status"], "written")
        records = self.records()
        self.assertEqual([r["text"] for r in records], ["да", "да"])
        self.assertNotEqual(first["anchor"], second["anchor"])
        self.assertNotEqual(records[0]["record_id"], records[1]["record_id"])

    def test_explicit_source_occurrence_retry_is_idempotent(self):
        first = self.capture("да", "2026-09-22T10:00:00Z", "--source-ref", "q7-answer")
        second = self.capture("да", "2026-09-22T10:00:00Z", "--source-ref", "q7-answer")
        self.assertEqual(second["status"], "already-present")
        self.assertEqual(first["anchor"], second["anchor"])
        self.assertEqual(len(self.records()), 1)

    def test_same_source_ref_changed_context_is_not_silently_rebound(self):
        self.capture("да", "2026-09-22T10:00:00Z", "--source-ref", "q7-answer")
        result = subprocess.run(self.command("да", "2026-09-22T10:00:00Z", "--source-ref", "q7-answer", "--context-note", "Другая сцена"), capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn("source occurrence", result.stderr)
        self.assertEqual(len(self.records()), 1)

    def test_bare_line_reference_cannot_bind_to_neighbor(self):
        first = self.capture("первая")
        record = self.records()[0]
        command = self.command("отмена", "2026-09-22T11:00:00Z")
        command.remove("--supersedes-none")
        command += ["--supersedes", f"{record['file']}#L{record['line']}"]
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 2, "unverified line was accepted as identity")
        self.assertEqual(len(self.records()), 1)

    def test_legacy_relation_without_identity_remains_unresolved(self):
        path = self.corpus / "legacy.md"
        path.write_text('---\nsession: legacy\ndate: 2026-09-22\n---\n* 2026-09-22T10:00:00Z — "старое" — type: решение | topic: scenes\n* 2026-09-22T11:00:00Z — "новое" — type: решение | topic: scenes | supersedes: legacy.md:5\n')
        records = self.records()
        digest.link_supersessions(records)
        self.assertNotIn("superseded_by", records[0])
        self.assertIn("unverified-supersedes", records[1]["diagnostics"])

    def test_capture_waits_for_corpus_lock(self):
        with (self.corpus / ".capture.lock").open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            process = subprocess.Popen(self.command(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            try:
                time.sleep(0.25)
                self.assertIsNone(process.poll(), "capture ignored the active corpus transaction")
            finally:
                fcntl.flock(lock, fcntl.LOCK_UN)
                stdout, stderr = process.communicate(timeout=10)
        self.assertEqual(process.returncode, 0, stderr)

    def test_parallel_captures_preserve_all_quotes_and_new_topics(self):
        # The delay makes pre-lock lost-update failures deterministic without a barrier
        # that would deadlock the corrected implementation while holding its lock.
        runner = "import sys,time;sys.path.insert(0,sys.argv[1]);import chat_capture as c;w=c.write_atomic;c.write_atomic=lambda *a:(time.sleep(.04),w(*a))[1];sys.argv=sys.argv[1:];raise SystemExit(c.main())"
        processes = []
        for index in range(12):
            command = self.command(f"реплика {index}", f"2026-09-22T10:{index:02}:00Z", "--topic", f"topic-{index}", "--new-topic", f"Предмет {index}")
            processes.append(subprocess.Popen([sys.executable, "-c", runner, str(SCRIPTS), *command[2:]], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True))
        results = [process.communicate(timeout=30) for process in processes]
        self.assertTrue(all(p.returncode == 0 for p in processes), str(results))
        self.assertEqual(len(self.records()), 12)
        topics = (self.corpus / "topics.md").read_text()
        self.assertTrue(all(f"`topic-{i}`" in topics for i in range(12)))


    def test_two_yes_answers_in_one_message_are_distinct_source_fragments(self):
        message = "3351cd9c-ec7d-4158-b76d-c0aa8ab56cfe"
        first = self.capture("да", "2026-09-22T10:00:00Z", "--source-ref", message + "#goal")
        second = self.capture("да", "2026-09-22T10:00:00Z", "--source-ref", message + "#scenes", "--context-note", "Сцены; согласованный вариант")
        self.assertNotEqual(first["anchor"], second["anchor"])
        self.assertEqual([r["text"] for r in self.records()], ["да", "да"])
        repeated = self.capture("да", "2026-09-22T10:00:00Z", "--source-ref", message + "#scenes", "--context-note", "Сцены; согласованный вариант")
        self.assertEqual(repeated["anchor"], second["anchor"])
        self.assertEqual(repeated["status"], "already-present")

    def test_exact_timestamp_fallback_distinguishes_context_in_same_message(self):
        first = self.capture("да", "2026-09-22T10:00:00Z", "--context-note", "GOAL; тайбрейкер")
        second = self.capture("да", "2026-09-22T10:00:00Z", "--context-note", "Сцены; выбранный вариант")
        self.assertNotEqual(first["anchor"], second["anchor"])
        self.assertEqual(second["deduplication"], "exact-timestamp-and-scene")

    def test_date_only_without_source_ref_does_not_claim_idempotency(self):
        first = self.capture("да", "2026-09-22")
        second = self.capture("да", "2026-09-22")
        self.assertNotEqual(first["anchor"], second["anchor"])
        self.assertEqual(second["deduplication"], "none")
        self.assertIn("--source-ref", second["warning"])

    def test_relations_keep_target_after_manual_insertion_and_header_growth(self):
        first = self.capture("первое решение")
        self.capture("другая тема", "2026-09-22T10:01:00Z", "--topic", "other", "--new-topic", "Вторая тема")
        path = Path(first["path"])
        original = path.read_text()
        path.write_text(original.replace("### ", '* 2026-09-01T00:00:00Z — "вставка" — type: факт | topic: scenes\n\n### ', 1))
        for relation, quote in [("--supersedes", "новое решение"), ("--contested", "спорное решение")]:
            command = self.command(quote, "2026-09-22T11:00:00Z")
            command.remove("--supersedes-none")
            result = subprocess.run([*command, relation, first["anchor"]], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
        records = self.records()
        digest.link_supersessions(records)
        old = next(r for r in records if r["text"] == "первое решение")
        self.assertEqual(len(old["superseded_by"]), 1)
        self.assertEqual(len(old["contested_by"]), 1)
        self.assertNotIn("superseded_by", next(r for r in records if r["text"] == "вставка"))

    def legacy(self):
        raw = '* 2026-09-22T10:00:00Z — "да" — type: решение | topic: scenes'
        path = self.corpus / "legacy.md"
        path.write_text('---\nsession: legacy\ndate: 2026-09-22\n---\n' + raw + '\n')
        return path, raw, hashlib.sha256(raw.encode()).hexdigest()

    def repair(self, *args):
        return subprocess.run([sys.executable, str(SCRIPTS / "chat_repair.py"), "--project", str(self.root), *args], capture_output=True, text=True)

    def test_repair_requires_verified_identity_and_dry_run_preserves_file(self):
        path, raw, sha = self.legacy()
        original = path.read_bytes()
        self.assertEqual(self.repair("--address", "legacy.md:5").returncode, 2)
        plan = self.root / "plan.json"
        result = self.repair("--address", f"legacy.md:5 sha:{sha}", "--plan-out", str(plan))
        self.assertEqual(result.returncode, 0, result.stderr)
        mapping = json.loads(result.stdout)["mapping"][0]
        self.assertEqual(path.read_bytes(), original)
        self.assertEqual(mapping["old_address"], "legacy.md#L5")
        self.assertRegex(mapping["anchor"], r"legacy\.md#recall-[a-f0-9]{32}")
        result = self.repair("--apply-plan", str(plan))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.records()[0]["address"], mapping["anchor"])
        self.assertIn(raw, path.read_text())
        self.assertEqual(path.name, "legacy.md")

    def test_repair_refuses_changed_file_before_any_write(self):
        path, raw, sha = self.legacy()
        plan = self.root / "plan.json"
        result = self.repair("--address", f"legacy.md:5 sha:{sha}", "--plan-out", str(plan))
        self.assertEqual(result.returncode, 0, result.stderr)
        path.write_text(path.read_text() + "\nAnother editor added this.\n")
        changed = path.read_bytes()
        result = self.repair("--apply-plan", str(plan))
        self.assertEqual(result.returncode, 2)
        self.assertIn("changed since plan", result.stderr)
        self.assertEqual(path.read_bytes(), changed)

    def test_verified_legacy_hash_resolves_after_drift_but_ambiguous_hash_refuses(self):
        path, raw, sha = self.legacy()
        path.write_text(path.read_text().replace("---\nsession:", "---\ntitle: added\nsession:"))
        result = self.repair("--address", f"legacy.md:5 sha:{sha[:8]}")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["mapping"][0]["line"], 6)
        path.write_text(path.read_text() + raw + "\n")
        result = self.repair("--address", f"legacy.md:5 sha:{sha}")
        self.assertEqual(result.returncode, 2)
        self.assertIn("2 records", result.stderr)

    def test_failed_transaction_cannot_rollback_another_writers_capture(self):
        marker = self.root / "failure-marker"
        runner = """import sys, time
sys.path.insert(0, sys.argv[1])
import chat_capture as c
from pathlib import Path
marker = Path(sys.argv[2])
def fail(*args, **kwargs):
    marker.touch()
    time.sleep(.25)
    raise c.CaptureError("planned receipt failure")
c.record_receipt = fail
sys.argv = sys.argv[2:3] + sys.argv[3:]
raise SystemExit(c.main())
"""
        command = self.command("failed quote", "2026-09-22T10:01:00Z", "--topic", "failed-topic", "--new-topic", "Не сохраняется")
        process = subprocess.Popen([sys.executable, "-c", runner, str(SCRIPTS), str(marker), *command[2:]], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        deadline = time.monotonic() + 5
        while not marker.exists() and process.poll() is None and time.monotonic() < deadline:
            time.sleep(.01)
        if not marker.exists():
            stdout, stderr = process.communicate(timeout=10)
            self.fail(stderr)
        successful = self.capture("successful quote", "2026-09-22T10:02:00Z", "--topic", "successful-topic", "--new-topic", "Сохраняется")
        stdout, stderr = process.communicate(timeout=10)
        self.assertEqual(process.returncode, 2, stderr)
        self.assertEqual([r["text"] for r in self.records()], ["successful quote"])
        self.assertIn("`successful-topic`", (self.corpus / "topics.md").read_text())
        self.assertNotIn("`failed-topic`", (self.corpus / "topics.md").read_text())


    def test_repair_preserves_original_bytes_with_crlf_bom_and_no_final_newline(self):
        path, raw, sha = self.legacy()
        original = ('\ufeff---\r\nsession: legacy\r\ndate: 2026-09-22\r\n---\r\n' + raw).encode('utf-8')
        path.write_bytes(original)
        plan = self.root / "plan.json"
        result = self.repair("--address", f"legacy.md:5 sha:{sha}", "--plan-out", str(plan))
        self.assertEqual(result.returncode, 0, result.stderr)
        identity = json.loads(result.stdout)["mapping"][0]["record_id"]
        result = self.repair("--apply-plan", str(plan))
        self.assertEqual(result.returncode, 0, result.stderr)
        after = path.read_bytes()
        self.assertEqual(after.replace(f"### {identity}\n\n".encode(), b""), original)

    def test_repair_rejects_duplicate_planned_target_before_any_write(self):
        path, raw, sha = self.legacy()
        plan = self.root / "plan.json"
        result = self.repair("--address", f"legacy.md:5 sha:{sha}", "--plan-out", str(plan))
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(plan.read_text())
        other = dict(payload["mapping"][0])
        other["record_id"] = "recall-" + "0" * 32
        other["anchor"] = "legacy.md#" + other["record_id"]
        payload["mapping"].append(other)
        plan.write_text(json.dumps(payload))
        before = path.read_bytes()
        result = self.repair("--apply-plan", str(plan))
        self.assertEqual(result.returncode, 2)
        self.assertIn("duplicate planned target", result.stderr)
        self.assertEqual(path.read_bytes(), before)


    def show(self, address):
        return subprocess.run([sys.executable, str(SCRIPTS / "chat_digest.py"), str(self.corpus), "--show", address, "--json"], capture_output=True, text=True)

    def test_show_reads_receipt_address_and_record_id_after_header_growth(self):
        receipt = self.capture("исходное решение")
        self.capture("другая тема", "2026-09-22T10:01:00Z", "--topic", "other", "--new-topic", "Вторая тема")
        for selector in (receipt["anchor"], receipt["record_id"]):
            with self.subTest(selector=selector):
                result = self.show(selector)
                self.assertEqual(result.returncode, 0, result.stderr)
                records = json.loads(result.stdout)["records"]
                self.assertEqual(len(records), 1)
                self.assertEqual(records[0]["text"], "исходное решение")
                self.assertEqual(records[0]["address"], receipt["anchor"])

    def test_show_rejects_duplicate_stable_address_and_record_id(self):
        receipt = self.capture("исходное решение")
        path = Path(receipt["path"])
        text = path.read_text()
        path.write_text(text + "\n" + text[text.index("### recall-"):])
        for selector in (receipt["anchor"], receipt["record_id"]):
            with self.subTest(selector=selector):
                result = self.show(selector)
                self.assertEqual(result.returncode, 2)
                self.assertIn("неоднозначен", result.stderr)

    def test_show_help_names_record_id_and_complete_stable_address(self):
        result = subprocess.run([sys.executable, str(SCRIPTS / "chat_digest.py"), "--help"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("record_id", result.stdout)
        self.assertIn("<file>.md#recall-<id>", result.stdout)


if __name__ == "__main__":
    unittest.main()
