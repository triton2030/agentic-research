"""След моста снаружи run_dir — единственное, чего не видит остальной набор.

Полтора месяца всё было зелёным, пока владелец не показал скриншот телефона:
список проектов Codex состоял из имён наших задач. Эти тесты держат сам датчик.
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import codex_footprint as fp


class OrphanThreadTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.sessions = self.root / "sessions" / "2026" / "08" / "18"
        self.sessions.mkdir(parents=True)
        self.addCleanup(self._tmp.cleanup)

    def write(self, name: str, *, cwd: str, originator: str = fp.BRIDGE_ORIGINATOR) -> None:
        meta = {"payload": {"id": name, "cwd": cwd, "originator": originator}}
        (self.sessions / f"rollout-2026-08-18T14-00-00-{name}.jsonl").write_text(
            json.dumps(meta) + "\n", encoding="utf-8"
        )

    def scan(self) -> list[dict[str, str]]:
        return fp.orphan_threads(self.root / "sessions")

    def test_dead_cwd_of_our_run_is_an_orphan(self) -> None:
        self.write("t-dead", cwd=str(self.root / "снесённое-дерево"))
        self.assertEqual([t["thread_id"] for t in self.scan()], ["t-dead"])

    def test_live_cwd_is_not_an_orphan(self) -> None:
        self.write("t-live", cwd=str(self.root))
        self.assertEqual(self.scan(), [])

    def test_someone_elses_thread_is_never_ours_to_clean(self) -> None:
        """Чужие чаты владельца датчик не считает и подавно не архивирует."""
        self.write("t-desktop", cwd=str(self.root / "нет"), originator="Codex Desktop")
        self.assertEqual(self.scan(), [])

    def test_corrupt_file_does_not_break_the_scan(self) -> None:
        (self.sessions / "rollout-2026-08-18T14-00-00-broken.jsonl").write_text("{не json")
        self.write("t-dead", cwd=str(self.root / "нет"))
        self.assertEqual([t["thread_id"] for t in self.scan()], ["t-dead"])

    def test_missing_store_is_empty_not_an_error(self) -> None:
        self.assertEqual(fp.orphan_threads(self.root / "нет-такого"), [])


class DeadProjectEntryTests(unittest.TestCase):
    def test_only_vanished_paths_are_counted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = root / "config.toml"
            config.write_text(
                f'model = "gpt-5.6-sol"\n\n'
                f'[projects."{root}"]\ntrust_level = "trusted"\n\n'
                f'[projects."{root}/нет"]\ntrust_level = "trusted"\n',
                encoding="utf-8",
            )
            self.assertEqual(fp.dead_project_entries(config), [f"{root}/нет"])

    def test_missing_config_is_empty_not_an_error(self) -> None:
        self.assertEqual(fp.dead_project_entries(Path("/нет/такого/config.toml")), [])


class DoctorRenderTests(unittest.TestCase):
    def test_footprint_is_printed_even_when_the_engine_is_silent(self) -> None:
        """Скан локальный: молчащий движок не имеет права спрятать наш мусор."""
        import codex_preflight as pre

        text = pre.render({
            "engine": {"binary_source": "chatgpt-app"},
            "error": "движок не ответил",
            "footprint": {"orphan_threads": 2, "orphan_thread_samples": ["/нет"],
                          "dead_project_entries": 7},
            "warnings": [],
        })
        self.assertIn("тредов на удалённых папках — 2", text)
        self.assertIn("archive --orphaned", text)


if __name__ == "__main__":
    unittest.main()
