"""Focused proof for the per-record incremental topic pipeline."""

from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).parents[3]
SCRIPTS = ROOT / "experiments" / "openviking-chat-recall" / "scripts"
RUNTIME = ROOT / "skills" / "codex" / "1chat-recall" / "scripts"
for directory in (SCRIPTS, RUNTIME):
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BUILD = load("build_update_under_test", SCRIPTS / "build_update_tasks.py")
APPLY = load("apply_update_under_test", SCRIPTS / "apply_update.py")
CHECK = load("check_coverage_under_test", SCRIPTS / "check_coverage.py")
SET_HORIZON = load("set_horizon_under_test", SCRIPTS / "set_horizon.py")
RUNTIME_RECONCILE = load(
    "runtime_topic_reconcile_under_test", RUNTIME / "topic_reconcile.py"
)


class UpdatePipelineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.previous_cwd = Path.cwd()
        os.chdir(self.root)
        (self.root / "_ops" / "chat-recall" / "topics").mkdir(parents=True)

    def tearDown(self) -> None:
        os.chdir(self.previous_cwd)
        self.temp.cleanup()

    @staticmethod
    def record(text: str, topic: str | None, record_type: str = "решение") -> str:
        suffix = f" | topic: {topic}" if topic is not None else ""
        return (
            f'* 2026-08-24T12:00:00+00:00 — "{text}" — '
            f"type: {record_type}{suffix}"
        )

    def write_topic(
        self, topic: str, body: str = "", root: Path | None = None
    ) -> Path:
        project = self.root if root is None else root
        path = project / "_ops" / "chat-recall" / "topics" / f"{topic}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            f"---\ntopic: {topic}\ntitle: {topic}\nsources: 0\n---\n# {topic}\n{body}",
            encoding="utf-8",
        )
        return path

    @staticmethod
    def snapshot_tree(root: Path) -> dict[str, bytes]:
        return {
            path.relative_to(root).as_posix(): path.read_bytes()
            for path in root.rglob("*")
            if path.is_file()
        }

    def foreign_fixture(self) -> tuple[Path, Path, Path, str]:
        project = self.root / "foreign-project"
        raw = project / "_ops" / "chat-recall" / "raw"
        raw.mkdir(parents=True)
        artifact = self.root / "foreign-artifacts"
        holder_name = "2026-08-25-130000-codex-foreign.md"
        session = "foreign-session"
        holder = raw / holder_name
        holder.write_text(
            "\n".join(
                self.holder_lines(
                    session,
                    self.record("Новая позиция", "topic-a"),
                    self.record("Без темы", None),
                )
            ),
            encoding="utf-8",
        )
        topic = self.write_topic(
            "topic-a",
            "",
            project,
        )
        flat = artifact / "flatten-v1" / "flat"
        flat.mkdir(parents=True)
        (flat / holder_name).write_text(
            f"source: {holder_name}\n\n- Уже покрыто. [L5]\n",
            encoding="utf-8",
        )
        return project, artifact, topic, holder_name

    def run_script(self, name: str, *args: object) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPTS / name), *(str(arg) for arg in args)],
            cwd=self.root,
            capture_output=True,
            text=True,
            check=False,
        )

    @staticmethod
    def holder_lines(session: str, *records: str) -> list[str]:
        return ["---", f"session: {session}", "---", "", *records]

    def test_builder_groups_rows_by_record_topic_not_holder(self) -> None:
        text = "\n".join(
            [
                "---",
                "session: demo",
                "---",
                "",
                self.record("Первое", "topic-a"),
                self.record("Второе", "topic-b"),
            ]
        )

        grouped = BUILD.topic_distribution(text, [5, 6])

        self.assertEqual(grouped, {"topic-a": [5], "topic-b": [6]})

    def test_builder_quarantines_uncovered_corrections_from_append(self) -> None:
        lines = [
            "---",
            "---",
            self.record("Новая позиция", "topic-a"),
            self.record("Исправление", "topic-a").replace(
                "type: решение", "type: коррекция"
            ),
        ]

        appendable, repair = BUILD.classify_uncovered("holder.md", lines, set())

        self.assertEqual(appendable, [3])
        self.assertEqual(repair, [4])

    def test_builder_excludes_acknowledged_noop_from_all_deltas(self) -> None:
        line = self.record("Разовая команда", "topic-a")
        fingerprint = hashlib.sha256(line.encode("utf-8")).hexdigest()
        session = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
        lines = self.holder_lines(session, line)

        appendable, repair = BUILD.classify_uncovered(
            "holder.md", lines, set(), {(session, fingerprint)}
        )

        self.assertEqual(appendable, [])
        self.assertEqual(repair, [])

    def test_builder_and_coverage_consume_the_same_noop_ledger(self) -> None:
        fingerprint = "a" * 64
        ledger = self.root / "_ops" / "chat-recall" / "topics" / "reconcile-noops.json"
        ledger.write_text(
            json.dumps(
                {
                    "version": 1,
                    "records": [
                        {
                            "topic": "topic-a",
                            "session": "session",
                            "record_sha256": fingerprint,
                            "anchor": "holder.md#L5",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )

        identity = {("session", fingerprint)}
        self.assertEqual(BUILD.noop_identities(), identity)
        self.assertEqual(CHECK.noop_identities(), identity)
        self.assertEqual(SET_HORIZON.noop_identities(), identity)

    def test_identical_lines_in_two_sessions_suppress_only_acknowledged_one(
        self,
    ) -> None:
        line = self.record("Одинаковые слова", "topic-a")
        fingerprint = hashlib.sha256(line.encode("utf-8")).hexdigest()
        session_a = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
        session_b = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
        acknowledged = {(session_a, fingerprint)}

        rows_a, _ = BUILD.classify_uncovered(
            "a.md", self.holder_lines(session_a, line), set(), acknowledged
        )
        rows_b, _ = BUILD.classify_uncovered(
            "b.md", self.holder_lines(session_b, line), set(), acknowledged
        )

        self.assertEqual(rows_a, [])
        self.assertEqual(rows_b, [5])

        raw = self.root / "_ops" / "chat-recall" / "raw"
        raw.mkdir()
        (raw / "a.md").write_text(
            "\n".join(self.holder_lines(session_a, line)), encoding="utf-8"
        )
        (raw / "b.md").write_text(
            "\n".join(self.holder_lines(session_b, line)), encoding="utf-8"
        )
        ledger = self.root / "_ops" / "chat-recall" / "topics" / "reconcile-noops.json"
        ledger.write_text(
            json.dumps(
                {
                    "version": 1,
                    "records": [
                        {
                            "topic": "topic-a",
                            "session": session_a,
                            "record_sha256": fingerprint,
                            "anchor": "a.md#L5",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(SET_HORIZON.main(True), 0)
        horizon = json.loads(output.getvalue())
        self.assertEqual(horizon["records"], 2)
        self.assertEqual(horizon["records_with_no_topic_effect"], 1)

    def test_pending_correction_identity_survives_line_drift(self) -> None:
        name = "2026-08-24-120000-codex-cccccccc.md"
        session = "cccccccc-cccc-cccc-cccc-cccccccccccc"
        correction = self.record("Исправление", "topic-a").replace(
            "type: решение", "type: коррекция"
        )
        lines = self.holder_lines(session, correction)
        raw = self.root / "_ops" / "chat-recall" / "raw"
        raw.mkdir()
        holder = raw / name
        holder.write_text("\n".join(lines), encoding="utf-8")
        self.write_topic("topic-a")

        fresh, pending = BUILD.deltas()

        self.assertEqual(fresh, {})
        self.assertEqual(len(pending), 1)
        item = pending[0]
        self.assertEqual(item["topic"], "topic-a")
        self.assertEqual(item["session"], session)
        self.assertEqual(item["anchor"], f"{name}#L5")
        self.assertEqual(
            item["record_sha256"], hashlib.sha256(correction.encode()).hexdigest()
        )

        lines.insert(2, "types: [correction]")
        holder.write_text("\n".join(lines), encoding="utf-8")
        live_anchor = RUNTIME_RECONCILE.locate_record(
            self.root,
            item["session"],
            item["record_sha256"],
            item["topic"],
        )
        self.assertEqual(live_anchor, f"{name}#L6")

    def test_applier_rejects_one_point_spanning_two_topics(self) -> None:
        self.write_topic("topic-a")
        self.write_topic("topic-b")
        topic, numbers, error = APPLY.route_point(
            "holder.md",
            ["5", "6"],
            {5: "topic-a", 6: "topic-b"},
            {("holder.md", 5), ("holder.md", 6)},
        )

        self.assertIsNone(topic)
        self.assertEqual(numbers, [5, 6])
        self.assertEqual(error, "пункт смешал записи разных тем")

    def test_applier_routes_new_holder_without_legacy_assignment(self) -> None:
        self.write_topic("topic-a")

        topic, numbers, error = APPLY.route_point(
            "new-holder.md",
            ["5"],
            {5: "topic-a"},
            {("new-holder.md", 5)},
        )

        self.assertEqual(topic, "topic-a")
        self.assertEqual(numbers, [5])
        self.assertIsNone(error)

    def test_applier_does_not_fallback_when_record_topic_is_missing(self) -> None:
        self.write_topic("topic-a")

        topic, numbers, error = APPLY.route_point(
            "legacy-holder.md",
            ["5"],
            {},
            {("legacy-holder.md", 5)},
        )

        self.assertIsNone(topic)
        self.assertEqual(numbers, [5])
        self.assertEqual(error, "у записи нет темы")

    def test_only_trailing_anchor_block_is_routed(self) -> None:
        parsed = APPLY.trailing_anchors("- L2 cache остаётся. [L5, L6]")

        self.assertEqual(parsed, (["5", "6"], "- L2 cache остаётся."))

    def test_batch_append_is_atomic_and_recounts_source_holders(self) -> None:
        topic_file = self.write_topic(
            "topic-a", "\n- Старое. [2026-08-20-120000-codex-aaaaaaaa.md#L10]\n"
        )
        topic_file.chmod(0o640)

        written = APPLY.append_topic_rows(
            "topic-a",
            ["- Новое. [2026-08-24-120000-codex-bbbbbbbb.md#L20]"],
        )

        rendered = topic_file.read_text(encoding="utf-8")
        self.assertTrue(written)
        self.assertIn("sources: 2", rendered)
        self.assertIn("- Старое.", rendered)
        self.assertIn("- Новое.", rendered)
        self.assertEqual(topic_file.stat().st_mode & 0o777, 0o640)

    def test_batch_and_runtime_share_one_lock_address(self) -> None:
        topic = "topic-a"

        self.assertEqual(
            APPLY.topic_lock_path(self.root, topic),
            RUNTIME_RECONCILE.topic_lock_path(self.root, topic),
        )

    def test_foreign_root_update_cli_represents_no_topic_and_applies_only_topic_rows(
        self,
    ) -> None:
        project, artifact, topic_file, holder_name = self.foreign_fixture()
        tasks = self.root / "foreign-tasks"
        result = self.run_script(
            "build_update_tasks.py",
            "--project-root",
            project,
            "--artifact-dir",
            artifact,
            tasks,
        )

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        delta = json.loads((artifact / "update-delta.json").read_text())
        self.assertEqual(delta, {holder_name: [5]})
        pending = json.loads(
            (artifact / "update-repair-pending.json").read_text()
        )
        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0]["topic"], None)
        self.assertEqual(pending[0]["reason"], "missing-topic")
        self.assertEqual(pending[0]["anchor"], f"{holder_name}#L6")
        task_text = (tasks / f"{holder_name[:-3]}.txt").read_text()
        self.assertIn("L5", task_text)
        self.assertNotIn("L6", task_text)

        runs = self.root / "foreign-runs"
        runs.mkdir()
        run_path = runs / holder_name.replace(".md", ".json")
        run_path.write_text(
            json.dumps(
                {
                    "ok": True,
                    "response": "---\n- Ошибочно направлено. [L6]\n",
                }
            ),
            encoding="utf-8",
        )
        before_dry = topic_file.read_bytes()
        rejected = self.run_script(
            "apply_update.py",
            "--dry",
            "--project-root",
            project,
            "--artifact-dir",
            artifact,
            runs,
        )
        self.assertEqual(rejected.returncode, 1)
        self.assertIn("не принят пункт", rejected.stdout)
        self.assertEqual(topic_file.read_bytes(), before_dry)

        run_path.write_text(
            json.dumps(
                {
                    "ok": True,
                    "response": "---\n- Новое знание. [L5]\n",
                }
            ),
            encoding="utf-8",
        )
        dry = self.run_script(
            "apply_update.py",
            "--dry",
            "--project-root",
            project,
            "--artifact-dir",
            artifact,
            runs,
        )
        self.assertEqual(dry.returncode, 0, dry.stdout + dry.stderr)
        self.assertEqual(topic_file.read_bytes(), before_dry)

        applied = self.run_script(
            "apply_update.py",
            "--project-root",
            project,
            "--artifact-dir",
            artifact,
            runs,
        )
        self.assertEqual(applied.returncode, 0, applied.stdout + applied.stderr)
        rendered = topic_file.read_text(encoding="utf-8")
        self.assertIn("Новое знание.", rendered)
        self.assertIn(f"[{holder_name}#L5]", rendered)

    def test_apply_update_rejects_partial_delta_before_dry_mutation(self) -> None:
        project, artifact, topic_a, holder_name = self.foreign_fixture()
        raw_holder = project / "_ops" / "chat-recall" / "raw" / holder_name
        raw_lines = raw_holder.read_text(encoding="utf-8").splitlines()
        raw_lines[5] = self.record("Вторая позиция", "topic-b")
        raw_holder.write_text("\n".join(raw_lines), encoding="utf-8")
        topic_b = self.write_topic("topic-b", root=project)
        artifact.mkdir(parents=True, exist_ok=True)
        (artifact / "update-delta.json").write_text(
            json.dumps({holder_name: [5, 6]}), encoding="utf-8"
        )

        runs = self.root / "partial-runs"
        runs.mkdir()
        (runs / holder_name.replace(".md", ".json")).write_text(
            json.dumps(
                {
                    "ok": True,
                    "response": "---\n- Только первая позиция. [L5]\n",
                }
            ),
            encoding="utf-8",
        )
        before_project = self.snapshot_tree(project)
        before_artifact = self.snapshot_tree(artifact)

        partial = self.run_script(
            "apply_update.py",
            "--dry",
            "--project-root",
            project,
            "--artifact-dir",
            artifact,
            runs,
        )

        self.assertEqual(partial.returncode, 1, partial.stdout + partial.stderr)
        self.assertIn("не покрыты записи дельты", partial.stdout)
        self.assertEqual(self.snapshot_tree(project), before_project)
        self.assertEqual(self.snapshot_tree(artifact), before_artifact)
        self.assertEqual(topic_a.read_bytes(), before_project[topic_a.relative_to(project).as_posix()])
        self.assertEqual(topic_b.read_bytes(), before_project[topic_b.relative_to(project).as_posix()])

        (runs / holder_name.replace(".md", ".json")).write_text(
            json.dumps(
                {
                    "ok": True,
                    "response": (
                        "---\n"
                        "- Первая позиция. [L5]\n"
                        "- Вторая позиция. [L6]\n"
                    ),
                }
            ),
            encoding="utf-8",
        )
        complete = self.run_script(
            "apply_update.py",
            "--dry",
            "--project-root",
            project,
            "--artifact-dir",
            artifact,
            runs,
        )

        self.assertEqual(complete.returncode, 0, complete.stdout + complete.stderr)
        self.assertEqual(self.snapshot_tree(project), before_project)
        self.assertEqual(self.snapshot_tree(artifact), before_artifact)

    def test_foreign_root_coverage_and_horizon_dry_are_read_only(self) -> None:
        project, artifact, topic_file, _ = self.foreign_fixture()
        sentinel = artifact / "coverage-gaps.tsv"
        sentinel.write_text("preexisting\n", encoding="utf-8")
        before_project = self.snapshot_tree(project)
        before_artifact = self.snapshot_tree(artifact)

        coverage = self.run_script(
            "check_coverage.py",
            "--live",
            "--project-root",
            project,
            "--artifact-dir",
            artifact,
        )
        self.assertEqual(coverage.returncode, 1)
        self.assertIn("typed records без topic: 1", coverage.stdout)
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "preexisting\n")

        horizon = self.run_script(
            "set_horizon.py", "--dry", "--project-root", project
        )
        self.assertEqual(horizon.returncode, 1)
        self.assertIn('"records_without_topic": 1', horizon.stdout)
        self.assertFalse((project / "_ops/chat-recall/topics/horizon.json").exists())
        self.assertEqual(self.snapshot_tree(project), before_project)
        self.assertEqual(self.snapshot_tree(artifact), before_artifact)
        self.assertEqual(topic_file.read_text(encoding="utf-8").count("Новое"), 0)

    def test_build_help_is_help_and_does_not_create_an_output_directory(self) -> None:
        result = self.run_script("build_update_tasks.py", "--help")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.root / "--help").exists())


if __name__ == "__main__":
    unittest.main()
