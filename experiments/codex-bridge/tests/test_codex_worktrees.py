"""Изоляция воркеров и закрытие волны — на настоящем git, без Codex и трат.

Проверяется то, ради чего изоляция и вводилась: атрибуция правок, отбраковка
записи вне allowlist, сохранность работы при конфликте и полнота уборки.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import codex_worktrees as wt


def git(cwd: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", *args], cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True
    )
    return proc.stdout.strip()


class WorktreeIsolationTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.project = Path(self._tmp.name).resolve() / "repo"
        self.project.mkdir()
        git(self.project, "init", "-b", "main")
        git(self.project, "config", "user.email", "test@example.com")
        git(self.project, "config", "user.name", "test")
        (self.project / "a.md").write_text("A\n")
        (self.project / "b.md").write_text("B\n")
        git(self.project, "add", "-A")
        git(self.project, "commit", "-m", "init")
        self.base = git(self.project, "rev-parse", "HEAD")
        # Деревья тестов уводим из ~/.codex-bridge, чтобы прогон не трогал рабочие.
        self._home = wt.FLEET_WORKTREE_HOME
        wt.FLEET_WORKTREE_HOME = Path(self._tmp.name) / "worktrees"

    def tearDown(self) -> None:
        wt.FLEET_WORKTREE_HOME = self._home
        self._tmp.cleanup()

    def make_tree(self, run_id: str, task_id: str) -> wt.WorkerTree:
        return wt.create_worker_tree(self.project, run_id, task_id, base=self.base)

    def test_worker_tree_is_a_separate_checkout_on_its_own_branch(self) -> None:
        tree = self.make_tree("run1", "t1")
        self.assertTrue((tree.path / "a.md").exists())
        self.assertNotEqual(tree.path.resolve(), self.project.resolve())
        self.assertEqual(git(tree.path, "rev-parse", "--abbrev-ref", "HEAD"), tree.branch)

    def test_changes_are_attributed_per_worker(self) -> None:
        """Ради этого изоляция и вводилась: в shared-дереве правку одного воркера
        нельзя отличить от правки другого — union-чек проходит у обоих."""
        t1 = self.make_tree("run1", "t1")
        t2 = self.make_tree("run1", "t2")
        (t1.path / "a.md").write_text("A changed by t1\n")
        (t2.path / "b.md").write_text("B changed by t2\n")

        wt.collect_changes(t1, {"a.md"})
        wt.collect_changes(t2, {"b.md"})
        self.assertEqual(t1.changed_files, ("a.md",))
        self.assertEqual(t2.changed_files, ("b.md",))
        self.assertEqual(t1.out_of_scope_files, ())
        self.assertEqual(t2.out_of_scope_files, ())

    def test_orchestrator_writing_in_main_tree_does_not_touch_workers(self) -> None:
        """Оркестратор пишет recall и планы, пока волна идёт. Раньше это валило
        scope волны (68% записей out_of_scope в замере 2026-08-14)."""
        tree = self.make_tree("run1", "t1")
        (self.project / "_ops").mkdir()
        (self.project / "_ops" / "recall.md").write_text("цитата владельца\n")
        (tree.path / "a.md").write_text("A changed\n")

        wt.collect_changes(tree, {"a.md"})
        self.assertEqual(tree.changed_files, ("a.md",))
        self.assertNotIn("_ops/recall.md", tree.changed_files)

    def test_out_of_scope_write_is_discarded_with_the_tree(self) -> None:
        """Запись вне allowlist в проект не попадает: она остаётся в дереве и
        уезжает с ним. В shared-режиме её пришлось бы откатывать руками."""
        tree = self.make_tree("run1", "t1")
        (tree.path / "a.md").write_text("A changed\n")
        (tree.path / "b.md").write_text("ЛИШНЕЕ\n")
        (tree.path / "node_modules").mkdir()
        (tree.path / "node_modules" / "junk.js").write_text("x" * 100)

        wave = wt.close_wave(
            self.project, [tree], {"a.md"}, run_id="run1", integrate=True, cleanup=True
        )
        self.assertEqual(wave["integration_status"], "integrated")
        self.assertIn("b.md", tree.out_of_scope_files)
        self.assertEqual((self.project / "a.md").read_text(), "A changed\n")
        self.assertEqual((self.project / "b.md").read_text(), "B\n")
        self.assertFalse((self.project / "node_modules").exists())

    def test_close_wave_integrates_and_cleans_up(self) -> None:
        t1 = self.make_tree("run1", "t1")
        t2 = self.make_tree("run1", "t2")
        (t1.path / "a.md").write_text("A by t1\n")
        (t2.path / "b.md").write_text("B by t2\n")

        wave = wt.close_wave(
            self.project, [t1, t2], {"a.md", "b.md"}, run_id="run1", integrate=True, cleanup=True
        )
        self.assertEqual(sorted(wave["merged"]), ["t1", "t2"])
        self.assertEqual(wave["conflicts"], [])
        self.assertTrue(wave["cleanup_done"])
        self.assertEqual((self.project / "a.md").read_text(), "A by t1\n")
        self.assertEqual((self.project / "b.md").read_text(), "B by t2\n")

        # Ни дерева, ни ветки, ни записи в git — уборка полная.
        self.assertFalse(t1.path.exists())
        self.assertFalse(t2.path.exists())
        listed = git(self.project, "worktree", "list")
        self.assertNotIn("codex-fleet", listed)
        branches = git(self.project, "branch", "--list", "codex-fleet/*")
        self.assertEqual(branches, "")

    def test_merge_commit_keeps_attribution_after_cleanup(self) -> None:
        """Деревья убраны, но кто писал файл — видно в истории."""
        tree = self.make_tree("run1", "рефактор-шапки")
        (tree.path / "a.md").write_text("A changed\n")
        wt.close_wave(self.project, [tree], {"a.md"}, run_id="run1", integrate=True, cleanup=True)
        log = git(self.project, "log", "--oneline", "-3")
        self.assertIn("рефактор-шапки", log)

    def test_conflict_keeps_the_work_and_the_branch(self) -> None:
        """Потеря правок дороже висящего дерева: конфликт откатывает merge, но
        ветка воркера остаётся, и работу можно забрать руками."""
        tree = self.make_tree("run1", "t1")
        (tree.path / "a.md").write_text("версия воркера\n")
        # База уехала: тот же файл изменён в основном дереве после старта волны.
        (self.project / "a.md").write_text("версия оркестратора\n")
        git(self.project, "commit", "-am", "main moved")

        wave = wt.close_wave(
            self.project, [tree], {"a.md"}, run_id="run1", integrate=True, cleanup=True
        )
        self.assertEqual(wave["integration_status"], "conflict")
        self.assertEqual(wave["conflicts"], ["t1"])
        self.assertIn(tree.branch, wave["kept_branches"])
        # Работа цела в ветке, основное дерево не испорчено недомердженным.
        self.assertEqual((self.project / "a.md").read_text(), "версия оркестратора\n")
        self.assertEqual(git(self.project, "show", f"{tree.branch}:a.md"), "версия воркера")
        self.assertEqual(git(self.project, "status", "--porcelain"), "")

    def test_empty_worker_is_not_a_failure(self) -> None:
        tree = self.make_tree("run1", "t1")
        wave = wt.close_wave(
            self.project, [tree], {"a.md"}, run_id="run1", integrate=True, cleanup=True
        )
        self.assertEqual(wave["integration_status"], "integrated")
        self.assertEqual(wave["merged"], [])
        self.assertEqual(tree.integration_status, "empty")
        self.assertFalse(tree.path.exists())

    def test_hold_mode_keeps_trees_and_branches(self) -> None:
        """`--no-integrate`: работа зафиксирована в ветке, но в проект не забрана —
        оркестратор смотрит сам."""
        tree = self.make_tree("run1", "t1")
        (tree.path / "a.md").write_text("A changed\n")
        wave = wt.close_wave(
            self.project, [tree], {"a.md"}, run_id="run1", integrate=False, cleanup=False
        )
        self.assertEqual(wave["integration_status"], "held")
        self.assertTrue(tree.path.exists())
        self.assertEqual((self.project / "a.md").read_text(), "A\n")


if __name__ == "__main__":
    unittest.main()
