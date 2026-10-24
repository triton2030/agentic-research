"""CLI regressions for the 2026-10-05 Capture fixes, on disposable corpora."""
import json
import importlib.util
import io
from contextlib import redirect_stdout
from datetime import datetime, timezone
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
import uuid

PACKAGE = Path(__file__).resolve().parents[1]
SCRIPTS = PACKAGE / "scripts"
sys.path.insert(0, str(SCRIPTS))
import chat_digest as digest


class CaptureFixesTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="recall-fixes-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.session = str(uuid.uuid4())
        self.log = self.root / "_ops/chat-recall"

    def command(self, quote="Тестовая реплика", *options, agent="claude", initial=False, type_="решение", relation=True):
        command = [sys.executable, str(SCRIPTS / "chat_capture.py"),
                   "--project", str(self.root), "--agent", agent,
                   "--session", self.session, "--quote", quote, "--type", type_,
                   "--topic", "capture", "--context-note", "Capture helper; runtime metadata", "--json"]
        if initial:
            command += ["--new-topic", "Проверка помощника записи", "--session-context", "помощник записи; старый предмет"]
        if relation:
            command += ["--supersedes-none"]
        return command + list(options)

    def capture(self, quote="Тестовая реплика", *options, ok=True, **kwargs):
        result = subprocess.run(self.command(quote, *options, **kwargs), capture_output=True, text=True)
        self.assertEqual(result.returncode, 0 if ok else 2, result.stderr)
        return json.loads(result.stdout) if ok else result.stderr

    def records(self):
        records, _ = digest.load(self.log)
        digest.link_supersessions(records)
        return records

    def old_positions(self):
        first = self.capture("Первое прежнее решение", "--source-timestamp", "2026-10-01T12:00:00Z", initial=True)
        second = self.capture("Второе прежнее решение", "--source-timestamp", "2026-10-02T12:00:00Z")
        return first, second

    def test_agent_case_reuses_existing_holder_without_card(self):
        first = self.capture(initial=True)
        for agent in ("Claude", "CLAUDE", "claude"):
            receipt = self.capture(f"Продолжение {agent}", agent=agent)
            self.assertEqual(receipt["path"], first["path"])
        self.assertEqual(len(list(self.log.glob("*claude*.md"))), 1)

    def test_uppercase_legacy_filename_and_header_are_preserved(self):
        receipt = self.capture(initial=True)
        path = Path(receipt["path"])
        text = path.read_text().replace("agent: claude", "agent: Claude")
        renamed = path.with_name(path.name.replace("-claude-", "-Claude-"))
        path.rename(renamed)
        renamed.write_text(text)
        next_receipt = self.capture("Новое слово", agent="CLAUDE")
        self.assertEqual(next_receipt["path"], str(renamed))
        self.assertIn("agent: Claude", renamed.read_text())

    def test_agent_case_resolves_runtime_environment(self):
        command = self.command(initial=True, agent="Codex")
        index = command.index("--session")
        del command[index:index + 2]
        env = {**os.environ, "CODEX_THREAD_ID": self.session}
        result = subprocess.run(command, capture_output=True, text=True, env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("-codex-", json.loads(result.stdout)["path"])

    def test_other_agent_error_names_holder_and_agent(self):
        first = self.capture(initial=True)
        before = Path(first["path"]).read_bytes()
        error = self.capture(agent="codex", ok=False)
        self.assertIn(first["path"], error)
        self.assertIn("agent: claude", error)
        self.assertEqual(Path(first["path"]).read_bytes(), before)
        self.assertEqual(len(list(self.log.glob("2*.md"))), 1)

    def test_missing_card_error_names_existing_holder(self):
        receipt = self.capture(initial=True)
        path = Path(receipt["path"])
        path.write_text("\n".join(line for line in path.read_text().splitlines() if not line.startswith("session-context:")) + "\n")
        error = self.capture(agent="Claude", ok=False)
        self.assertIn(str(path), error)
        self.assertIn("agent: claude", error)

    def test_duplicate_holder_error_names_both_agents(self):
        receipt = self.capture(initial=True)
        path = Path(receipt["path"])
        other = path.with_name("duplicate-" + path.name.replace("-claude-", "-Claude-"))
        other.write_bytes(path.read_bytes())
        error = self.capture(ok=False)
        self.assertIn(str(path), error)
        self.assertIn(str(other), error)

    def test_same_turn_omits_timestamp_and_ref_with_honest_receipt(self):
        receipt = self.capture(initial=True)
        self.assertEqual(receipt["deduplication"], "none")
        self.assertIn("retries create separate records", receipt["warning"])
        record = self.records()[0]
        self.assertEqual(record["precision"], "exact")
        self.assertIsNone(record["source_ref"])

    def test_fractional_timestamp_is_lossless_and_retry_is_idempotent(self):
        options = ("--source-timestamp", "2026-10-05T08:39:48.123456Z")
        first = self.capture("Дробное время", *options, initial=True)
        second = self.capture("Дробное время", *options)
        self.assertEqual(second["status"], "already-present")
        self.assertEqual(first["anchor"], second["anchor"])
        self.assertEqual(self.records()[0]["timestamp"], "2026-10-05T08:39:48.123456+00:00")

    def test_two_implicit_captures_in_same_second_have_valid_supersession(self):
        spec = importlib.util.spec_from_file_location("capture_microsecond_probe", SCRIPTS / "chat_capture.py")
        capture = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(capture)

        class TickDateTime(datetime):
            ticks = 100000

            @classmethod
            def now(cls, tz=None):
                cls.ticks += 1
                return cls(2026, 10, 5, 12, 0, 0, cls.ticks, tzinfo=timezone.utc)

        def direct(command):
            output = io.StringIO()
            with mock.patch.object(capture, "datetime", TickDateTime), mock.patch.object(sys, "argv", command[1:]), redirect_stdout(output):
                self.assertEqual(capture.main(), 0)
            return json.loads(output.getvalue())

        first = direct(self.command("Быстрое прежнее решение", initial=True))
        second = direct(self.command("Быстрая отмена", "--supersedes", first["anchor"], relation=False))
        records = self.records()
        old = next(record for record in records if record["address"] == first["anchor"])
        new = next(record for record in records if record["address"] == second["anchor"])
        self.assertEqual(old["superseded_by"], [second["anchor"]])
        self.assertNotIn("supersedes-not-newer", new["diagnostics"])
        self.assertEqual(datetime.fromisoformat(old["timestamp"]).second, datetime.fromisoformat(new["timestamp"]).second)
        self.assertLess(datetime.fromisoformat(old["timestamp"]), datetime.fromisoformat(new["timestamp"]))

    def test_multiple_supersedes_roundtrip_and_retry(self):
        first, second = self.old_positions()
        options = ("--source-timestamp", "2026-10-03T12:00:00Z", "--supersedes", first["anchor"], second["anchor"])
        receipt = self.capture("Новое решение", *options, relation=False)
        retry = self.capture("Новое решение", *options, relation=False)
        self.assertEqual(retry["status"], "already-present")
        records = self.records()
        new = next(record for record in records if record["text"] == "Новое решение")
        self.assertEqual(json.loads(new["supersedes"]), [first["anchor"], second["anchor"]])
        for old in records:
            if old != new:
                self.assertEqual(old["superseded_by"], [receipt["anchor"]])
        self.assertFalse(new["diagnostics"])

    def test_repeated_contested_option_links_each_target_once(self):
        first, second = self.old_positions()
        receipt = self.capture("Спорная позиция", "--contested", first["anchor"], "--contested", second["anchor"], first["anchor"], relation=False)
        for old in self.records():
            if old["text"] != "Спорная позиция":
                self.assertEqual(old["contested_by"], [receipt["anchor"]])
                self.assertNotIn("superseded_by", old)

    def test_bad_second_address_leaves_holder_and_map_unchanged(self):
        first, _ = self.old_positions()
        before = {path: path.read_bytes() for path in self.log.glob("*.md")}
        error = self.capture("Неверная отмена", "--supersedes", first["anchor"], "missing.md#recall-" + "0" * 32, relation=False, ok=False)
        self.assertIn("supersedes:", error)
        self.assertEqual(before, {path: path.read_bytes() for path in self.log.glob("*.md")})

    def test_multi_relations_do_not_allow_mixed_answers(self):
        first, second = self.old_positions()
        error = self.capture("Смешанный ответ", "--supersedes", first["anchor"], second["anchor"], "--contested", first["anchor"], relation=False, ok=False)
        self.assertIn("contradicts", error)

    def test_add_subjects_preserves_prior_card_and_quote_bytes(self):
        receipt = self.capture(initial=True)
        path = Path(receipt["path"])
        old_body = path.read_text().split("### ", 1)[1]
        options = ("--source-ref", "addition-1", "--add-subjects", "Новый предмет; старый предмет", "--add-subjects", "новый предмет; другой предмет")
        self.capture("Дополнение", *options)
        self.capture("Дополнение", *options)
        text = path.read_text()
        self.assertIn('session-context: "помощник записи; старый предмет; Новый предмет; другой предмет"', text)
        self.assertIn("### " + old_body.rstrip() + "\n", text)
        self.assertEqual(len(self.records()), 2)

    def test_add_subjects_updates_card_even_on_quote_retry(self):
        self.capture("Повтор", "--source-ref", "retry", initial=True)
        receipt = self.capture("Повтор", "--source-ref", "retry", "--add-subjects", "дополнительный маршрут")
        self.assertEqual(receipt["status"], "context-updated")
        self.assertEqual(len(self.records()), 1)
        self.assertIn("дополнительный маршрут", self.records()[0]["session_context"])

    def test_add_subjects_requires_prior_card_and_rejects_replacement(self):
        error = self.capture("Нет карточки", "--new-topic", "Помощник записи", "--add-subjects", "предмет", ok=False)
        self.assertIn("existing conversation card", error)
        error = self.capture("Два режима", "--add-subjects", "предмет", initial=True, ok=False)
        self.assertIn("cannot combine", error)

    def test_permission_is_separate_type_and_survives_retrieval(self):
        self.capture("Разрешаю архивировать эту папку", initial=True, type_="разрешение", relation=False)
        record = self.records()[0]
        self.assertEqual(record["type"], "разрешение")
        self.assertFalse(record["diagnostics"])
        result = subprocess.run([sys.executable, str(SCRIPTS / "chat_capture.py"), "--list-metadata", "--project", str(self.root)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn("разрешение: согласие владельца на одно названное действие", result.stdout)

    def test_help_explains_same_turn_and_new_interfaces(self):
        result = subprocess.run([sys.executable, str(SCRIPTS / "chat_capture.py"), "--help"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        for text in ("fractional seconds", "same-turn capture", "no transcript lookup", "--add-subjects", "one or more addresses"):
            self.assertIn(text, " ".join(result.stdout.split()))


if __name__ == "__main__":
    unittest.main()
