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

    def make_tree(self, run_id: str, task_id: str, allowlist: set[str] | None = None) -> wt.WorkerTree:
        # Как в проде: снимок «что лежало до старта» — последний шаг подготовки,
        # после создания дерева и провижининга (`open_wave`).
        tree = wt.create_worker_tree(
            self.project, run_id, task_id, base=self.base, allowlist=allowlist or set()
        )
        wt.snapshot_preexisting(tree)
        return tree

    def test_worker_tree_is_a_separate_checkout_on_its_own_branch(self) -> None:
        tree = self.make_tree("run1", "t1", {"a.md"})
        self.assertTrue((tree.path / "a.md").exists())
        self.assertNotEqual(tree.path.resolve(), self.project.resolve())
        self.assertEqual(git(tree.path, "rev-parse", "--abbrev-ref", "HEAD"), tree.branch)

    def test_changes_are_attributed_per_worker(self) -> None:
        """Ради этого изоляция и вводилась: в shared-дереве правку одного воркера
        нельзя отличить от правки другого — union-чек проходит у обоих."""
        t1 = self.make_tree("run1", "t1", {"a.md"})
        t2 = self.make_tree("run1", "t2", {"b.md"})
        (t1.path / "a.md").write_text("A changed by t1\n")
        (t2.path / "b.md").write_text("B changed by t2\n")

        wt.collect_changes(t1)
        wt.collect_changes(t2)
        self.assertEqual(t1.changed_files, ("a.md",))
        self.assertEqual(t2.changed_files, ("b.md",))
        self.assertEqual(t1.out_of_scope_files, ())
        self.assertEqual(t2.out_of_scope_files, ())

    def test_orchestrator_writing_in_main_tree_does_not_touch_workers(self) -> None:
        """Оркестратор пишет recall и планы, пока волна идёт. Раньше это валило
        scope волны (68% записей out_of_scope в замере 2026-08-14)."""
        tree = self.make_tree("run1", "t1", {"a.md"})
        (self.project / "_ops").mkdir()
        (self.project / "_ops" / "recall.md").write_text("цитата владельца\n")
        (tree.path / "a.md").write_text("A changed\n")

        wt.collect_changes(tree)
        self.assertEqual(tree.changed_files, ("a.md",))
        self.assertNotIn("_ops/recall.md", tree.changed_files)

    def test_out_of_scope_write_holds_the_whole_worker(self) -> None:
        """Запись вне списка в проект не попадает вообще — ни лишнее, ни то, что
        рядом: воркер мог опереться на лишний файл, и половина работы дала бы
        сломанное состояние. Вся работа — включая внесписочную, на которую он
        мог опереться, — фиксируется в ветке; дерево при уборке сносится."""
        tree = self.make_tree("run1", "t1", {"a.md"})
        (tree.path / "a.md").write_text("A changed\n")
        (tree.path / "b.md").write_text("ЛИШНЕЕ\n")
        (tree.path / "node_modules").mkdir()
        (tree.path / "node_modules" / "junk.js").write_text("x" * 100)

        wave = wt.close_wave(
            self.project, [tree], run_id="run1", integrate=True, cleanup=True
        )
        self.assertEqual(wave["integration_status"], "partial")
        self.assertEqual(wave["held"], ["t1"])
        self.assertIn("b.md", tree.out_of_scope_files)
        # В проекте не изменилось ничего, мусор воркера туда не уехал.
        self.assertEqual((self.project / "a.md").read_text(), "A\n")
        self.assertEqual((self.project / "b.md").read_text(), "B\n")
        self.assertFalse((self.project / "node_modules").exists())
        # Работа цела ЦЕЛИКОМ и адресуема через ветку: ручной разбор возможен,
        # даже когда дерево уже снесено уборкой.
        self.assertIn(tree.branch, wave["kept_branches"])
        self.assertFalse(tree.path.exists())
        self.assertEqual(git(self.project, "show", f"{tree.branch}:a.md"), "A changed")
        self.assertEqual(git(self.project, "show", f"{tree.branch}:b.md"), "ЛИШНЕЕ")

    def test_only_out_of_scope_work_is_preserved_not_dropped_as_empty(self) -> None:
        """Воркер, писавший только вне списка, — не «пустой»: до этой проверки
        его правки не коммитились вовсе и гибли вместе с деревом при уборке."""
        tree = self.make_tree("run1", "t1", {"a.md"})
        (tree.path / "b.md").write_text("всё мимо списка\n")

        wave = wt.close_wave(
            self.project, [tree], run_id="run1", integrate=True, cleanup=True
        )
        self.assertEqual(tree.integration_status, "held_out_of_scope")
        self.assertIn(tree.branch, wave["kept_branches"])
        self.assertEqual((self.project / "b.md").read_text(), "B\n")
        self.assertEqual(git(self.project, "show", f"{tree.branch}:b.md"), "всё мимо списка")

    def test_worker_touching_another_workers_file_is_out_of_scope(self) -> None:
        """Каждому дереву — СВОЙ список, не union волны. С union правка соседнего
        файла проходила как своя, и атрибуция, ради которой изоляция и вводилась,
        снова становилась недоказуемой."""
        t1 = self.make_tree("run1", "t1", {"a.md"})
        (t1.path / "a.md").write_text("свой файл\n")
        (t1.path / "b.md").write_text("файл соседа\n")

        wt.collect_changes(t1)
        self.assertEqual(t1.out_of_scope_files, ("b.md",))

    def test_no_integrate_never_deletes_unmerged_work(self) -> None:
        """`--no-integrate` + уборка = потерянные правки. Поэтому коммит идёт
        всегда, а деревья при незабранной работе не удаляются."""
        tree = self.make_tree("run1", "t1", {"a.md"})
        (tree.path / "a.md").write_text("A changed\n")

        wave = wt.close_wave(
            self.project, [tree], run_id="run1", integrate=False, cleanup=True
        )
        self.assertEqual(wave["integration_status"], "held")
        # Работа зафиксирована в ветке — даже при заказанной уборке.
        self.assertEqual(git(self.project, "show", f"{tree.branch}:a.md"), "A changed")
        self.assertIn(tree.branch, wave["kept_branches"])
        self.assertEqual((self.project / "a.md").read_text(), "A\n")

    def test_failed_worker_is_not_merged_but_is_preserved(self) -> None:
        """Статус хода — шлюз интеграции: полуфабрикат упавшего воркера в проект
        не едет, но и не теряется."""
        tree = self.make_tree("run1", "t1", {"a.md"})
        tree.worker_ok = False
        (tree.path / "a.md").write_text("полуфабрикат\n")

        wave = wt.close_wave(
            self.project, [tree], run_id="run1", integrate=True, cleanup=True
        )
        self.assertEqual(tree.integration_status, "held_failed_worker")
        self.assertEqual(wave["held"], ["t1"])
        self.assertEqual((self.project / "a.md").read_text(), "A\n")
        self.assertEqual(git(self.project, "show", f"{tree.branch}:a.md"), "полуфабрикат")

    def test_cleanup_done_is_a_fact_not_a_request(self) -> None:
        """`cleanup_done` обещан скилом как предъявляемый след закрытия волны.
        Если он равен просьбе, а не результату, след ничего не доказывает."""
        tree = self.make_tree("run1", "t1", {"a.md"})
        (tree.path / "a.md").write_text("A changed\n")
        wave = wt.close_wave(
            self.project, [tree], run_id="run1", integrate=True, cleanup=False
        )
        self.assertFalse(wave["cleanup_done"])
        self.assertFalse(wave["cleanup_requested"])
        self.assertTrue(tree.path.exists())

    def test_close_wave_integrates_and_cleans_up(self) -> None:
        t1 = self.make_tree("run1", "t1", {"a.md"})
        t2 = self.make_tree("run1", "t2", {"b.md"})
        (t1.path / "a.md").write_text("A by t1\n")
        (t2.path / "b.md").write_text("B by t2\n")

        wave = wt.close_wave(
            self.project, [t1, t2], run_id="run1", integrate=True, cleanup=True
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
        tree = self.make_tree("run1", "рефактор-шапки", {"a.md"})
        (tree.path / "a.md").write_text("A changed\n")
        wt.close_wave(
            self.project, [tree], run_id="run1", integrate=True, cleanup=True)
        log = git(self.project, "log", "--oneline", "-3")
        self.assertIn("рефактор-шапки", log)

    def test_conflict_keeps_the_work_and_the_branch(self) -> None:
        """Потеря правок дороже висящего дерева: конфликт откатывает merge, но
        ветка воркера остаётся, и работу можно забрать руками."""
        tree = self.make_tree("run1", "t1", {"a.md"})
        (tree.path / "a.md").write_text("версия воркера\n")
        # База уехала: тот же файл изменён в основном дереве после старта волны.
        (self.project / "a.md").write_text("версия оркестратора\n")
        git(self.project, "commit", "-am", "main moved")

        wave = wt.close_wave(
            self.project, [tree], run_id="run1", integrate=True, cleanup=True
        )
        self.assertEqual(wave["integration_status"], "conflict")
        self.assertEqual(wave["conflicts"], ["t1"])
        self.assertIn(tree.branch, wave["kept_branches"])
        # Работа цела в ветке, основное дерево не испорчено недомердженным.
        self.assertEqual((self.project / "a.md").read_text(), "версия оркестратора\n")
        self.assertEqual(git(self.project, "show", f"{tree.branch}:a.md"), "версия воркера")
        self.assertEqual(git(self.project, "status", "--porcelain"), "")

    def test_empty_worker_is_not_a_failure(self) -> None:
        tree = self.make_tree("run1", "t1", {"a.md"})
        wave = wt.close_wave(
            self.project, [tree], run_id="run1", integrate=True, cleanup=True
        )
        self.assertEqual(wave["integration_status"], "integrated")
        self.assertEqual(wave["merged"], [])
        self.assertEqual(tree.integration_status, "empty")
        self.assertFalse(tree.path.exists())

    def test_worker_own_commit_is_not_lost(self) -> None:
        """Воркер закоммитил сам (вопреки контракту): diff от подвижного HEAD
        видел «пустоту» и force-delete уносил его коммит в dangling. Diff от
        base_commit волны видит работу."""
        tree = self.make_tree("run1", "t1", {"a.md"})
        (tree.path / "a.md").write_text("сам закоммитил\n")
        git(tree.path, "add", "a.md")
        git(tree.path, "commit", "-m", "worker own commit")

        wave = wt.close_wave(
            self.project, [tree], run_id="run1", integrate=True, cleanup=True
        )
        self.assertEqual(wave["merged"], ["t1"])
        self.assertEqual((self.project / "a.md").read_text(), "сам закоммитил\n")

    def test_merge_takes_recorded_commit_not_branch_tip(self) -> None:
        """Между аудитом изменений и merge на ветку мог лечь чужой коммит:
        merge tip-а внёс бы его в проект как работу воркера. Вливается только
        записанный SHA; уехавшая вперёд ветка не удаляется."""
        tree = self.make_tree("run1", "t1", {"a.md"})
        (tree.path / "a.md").write_text("audited\n")
        wt.collect_changes(tree)
        wt.commit_worker_tree(tree, message="m")
        (tree.path / "late.md").write_text("контрабанда\n")
        git(tree.path, "add", "late.md")
        git(tree.path, "commit", "-m", "late")

        wt.integrate_worker_tree(self.project, tree)
        self.assertEqual(tree.integration_status, "merged")
        self.assertEqual((self.project / "a.md").read_text(), "audited\n")
        self.assertFalse((self.project / "late.md").exists())
        wt.remove_worker_tree(self.project, tree)
        self.assertEqual(tree.cleanup_status, "branch_ahead")

    def test_rewritten_head_holds_integration(self) -> None:
        """reset/rebase ниже базы волны делает merge контрабандой: он принёс бы
        разницу историй как работу воркера. Такой воркер удерживается."""
        (self.project / "a.md").write_text("v2\n")
        git(self.project, "commit", "-am", "v2")
        base2 = git(self.project, "rev-parse", "HEAD")
        tree = wt.create_worker_tree(
            self.project, "run1", "t1", base=base2, allowlist={"a.md"}
        )
        (tree.path / "a.md").write_text("работа\n")
        git(self.project, "reset", "--hard", self.base)

        wave = wt.close_wave(
            self.project, [tree], run_id="run1", integrate=True, cleanup=True
        )
        self.assertEqual(tree.integration_status, "held_base_rewritten")
        self.assertEqual((self.project / "a.md").read_text(), "A\n")
        self.assertIn(tree.branch, wave["kept_branches"])

    def test_gitignored_new_allowlist_file_is_not_lost(self) -> None:
        """Разрешённый новый файл может сам попадать под .gitignore: без
        отдельного прохода по allowlist он гиб как «мусор», а прогон честно
        рапортовал empty."""
        (self.project / ".gitignore").write_text("dist/\n")
        git(self.project, "add", ".gitignore")
        git(self.project, "commit", "-m", "ignore dist")
        base = git(self.project, "rev-parse", "HEAD")
        tree = wt.create_worker_tree(
            self.project, "run1", "t1", base=base, allowlist={"dist/out.md"}
        )
        (tree.path / "dist").mkdir()
        (tree.path / "dist" / "out.md").write_text("артефакт\n")

        wave = wt.close_wave(
            self.project, [tree], run_id="run1", integrate=True, cleanup=True
        )
        self.assertEqual(wave["merged"], ["t1"])
        self.assertEqual((self.project / "dist" / "out.md").read_text(), "артефакт\n")

    def test_hook_dirtied_tree_is_held(self) -> None:
        """post-checkout hook пачкает дерево до старта воркера — его правки
        вливались бы как работа воркера. Такое дерево удерживается."""
        hook = self.project / ".git" / "hooks" / "post-checkout"
        hook.write_text("#!/bin/sh\nprintf 'written by hook\\n' > a.md\n")
        hook.chmod(0o755)
        tree = self.make_tree("run1", "t1", {"a.md"})
        self.assertIn("a.md", tree.preexisting)

        wave = wt.close_wave(
            self.project, [tree], run_id="run1", integrate=True, cleanup=True
        )
        self.assertEqual(tree.integration_status, "held_dirty_birth")
        self.assertEqual((self.project / "a.md").read_text(), "A\n")
        self.assertIn(tree.branch, wave["kept_branches"])

    def test_hook_artifact_outside_allowlist_does_not_hold_the_worker(self) -> None:
        """Боевая волна 20260814T085606Z: hook породил один посторонний файл в
        каждом дереве, и все три воркера были удержаны как out_of_scope — 8
        готовых файлов не влились. Чужой файл, лежавший до старта, работой
        воркера не считается."""
        hook = self.project / ".git" / "hooks" / "post-checkout"
        hook.write_text("#!/bin/sh\nmkdir -p probes\nprintf 'png\\n' > probes/warp.png\n")
        hook.chmod(0o755)
        tree = self.make_tree("run1", "t1", {"a.md"})
        self.assertIn("probes/warp.png", tree.preexisting)
        (tree.path / "a.md").write_text("работа воркера\n")

        wave = wt.close_wave(
            self.project, [tree], run_id="run1", integrate=True, cleanup=True
        )
        self.assertEqual(tree.out_of_scope_files, ())
        self.assertEqual(wave["merged"], ["t1"])
        self.assertEqual((self.project / "a.md").read_text(), "работа воркера\n")
        self.assertFalse((self.project / "probes" / "warp.png").exists())

    def test_symlink_outside_the_tree_does_not_hold_the_worker(self) -> None:
        """Живой случай: воркер подменил установку линком `node_modules` на
        соседнее дерево. `.gitignore` с завершающим слэшем такой линк не ловит,
        git считает его записью вне allowlist — и вся работа воркера уходила на
        ручной разбор. Ссылка наружу не забирается и волну не удерживает."""
        (self.project / ".gitignore").write_text("node_modules/\n")
        git(self.project, "add", "-A")
        git(self.project, "commit", "-m", "ignore")
        self.base = git(self.project, "rev-parse", "HEAD")
        neighbour = Path(self._tmp.name) / "neighbour_modules"
        neighbour.mkdir()
        (neighbour / "pkg.txt").write_text("dep\n")

        tree = self.make_tree("run1", "t1", {"a.md"})
        (tree.path / "node_modules").symlink_to(neighbour)
        (tree.path / "a.md").write_text("работа воркера\n")

        wave = wt.close_wave(
            self.project, [tree], run_id="run1", integrate=True, cleanup=True
        )
        self.assertNotIn("node_modules", tree.changed_files)
        self.assertEqual(tree.out_of_scope_files, ())
        self.assertEqual(wave["merged"], ["t1"])
        self.assertEqual((self.project / "a.md").read_text(), "работа воркера\n")
        self.assertFalse((self.project / "node_modules").exists())

    def test_setup_touching_an_owned_file_refuses_the_wave_before_any_turn(self) -> None:
        """Подготовка тронула файл из списка задачи — отличить кодогенерацию от
        работы воркера в нём уже нечем, и дальше по коду это `held_dirty_birth`,
        то есть задача, оплаченная полностью и мёртвая. Отказ идёт до первого
        хода: деревьев и веток после него не остаётся."""
        def setup(trees: list[wt.WorkerTree]) -> None:
            for tree in trees:
                (tree.path / "a.md").write_text("сгенерировано подготовкой\n")

        with self.assertRaises(wt.WorktreeError) as caught:
            wt.open_wave(
                self.project, "run1", [("t1", {"a.md"})], base=self.base, setup=setup
            )
        self.assertIn("a.md", str(caught.exception))
        self.assertEqual(git(self.project, "branch", "--list", "codex-fleet/*"), "")
        self.assertEqual(len(git(self.project, "worktree", "list").splitlines()), 1)

    def test_setup_failure_abandons_every_tree_of_the_wave(self) -> None:
        """Красная подготовка ОДНОГО дерева отменяет волну целиком: полволны
        изолировать нельзя, а выкладка стоит сотни МБ на дерево."""
        def setup(trees: list[wt.WorkerTree]) -> None:
            (trees[0].path / "ok.txt").write_text("готово\n")
            raise wt.WorktreeError("npm ci упал в t2")

        with self.assertRaises(wt.WorktreeError):
            wt.open_wave(
                self.project,
                "run1",
                [("t1", {"a.md"}), ("t2", {"b.md"}), ("t3", {"a.md"})],
                base=self.base,
                setup=setup,
            )
        self.assertEqual(git(self.project, "branch", "--list", "codex-fleet/*"), "")
        self.assertEqual(len(git(self.project, "worktree", "list").splitlines()), 1)

    def test_interrupt_during_setup_leaves_no_trees_behind(self) -> None:
        """Подготовка — произвольный shell на минуты: Ctrl-C в ней не должен
        оставлять N полных выкладок проекта молча."""
        def setup(trees: list[wt.WorkerTree]) -> None:
            raise KeyboardInterrupt

        with self.assertRaises(KeyboardInterrupt):
            wt.open_wave(
                self.project,
                "run1",
                [("t1", {"a.md"}), ("t2", {"b.md"})],
                base=self.base,
                setup=setup,
            )
        self.assertEqual(git(self.project, "branch", "--list", "codex-fleet/*"), "")
        self.assertEqual(len(git(self.project, "worktree", "list").splitlines()), 1)

    def test_red_gate_keeps_project_untouched_and_work_in_branches(self) -> None:
        """Проверка — ворота ПЕРЕД проектом. Красная проверка не вливает ничего:
        основная ветка та же, работа цела в ветке воркера, дерево убрано."""
        tree = self.make_tree("run1", "t1", {"a.md"})
        (tree.path / "a.md").write_text("работа воркера\n")
        head_before = git(self.project, "rev-parse", "HEAD")
        seen: list[Path] = []

        def gate(path: Path) -> tuple[bool, dict]:
            seen.append(path)
            # Проверка видит уже слитое состояние, а не исходное.
            self.assertEqual((path / "a.md").read_text(), "работа воркера\n")
            return False, {"status": "failed", "checks": [{"command": "false"}]}

        wave = wt.close_wave(
            self.project, [tree], run_id="run1", integrate=True, cleanup=True, gate=gate
        )
        self.assertEqual(seen and seen[0].name, "_integration")
        self.assertEqual(git(self.project, "rev-parse", "HEAD"), head_before)
        self.assertEqual((self.project / "a.md").read_text(), "A\n")
        self.assertEqual(wave["merged"], [])
        self.assertEqual(tree.integration_status, "held_verify_failed")
        self.assertIn(tree.branch, wave["kept_branches"])
        self.assertEqual(wave["verification"]["status"], "failed")
        self.assertFalse((wt.FLEET_WORKTREE_HOME / "run1" / "_integration").exists())

    def test_green_gate_merges_after_verification(self) -> None:
        """Зелёная проверка пускает работу в проект, ветки воркеров убираются."""
        tree = self.make_tree("run1", "t1", {"a.md"})
        (tree.path / "a.md").write_text("проверено\n")

        wave = wt.close_wave(
            self.project, [tree], run_id="run1", integrate=True, cleanup=True,
            gate=lambda path: (True, {"status": "passed", "checks": []}),
        )
        self.assertEqual(wave["merged"], ["t1"])
        self.assertEqual((self.project / "a.md").read_text(), "проверено\n")
        self.assertEqual(wave["kept_branches"], [])
        self.assertTrue(wave["verified_before_merge"])
        branches = git(self.project, "branch", "--list", f"{wt.BRANCH_PREFIX}/run1/integration")
        self.assertEqual(branches.strip(), "")

    def test_open_wave_rolls_back_partially_opened_wave(self) -> None:
        """Полволны изолировать нельзя: отказ на втором дереве убирает первое
        целиком — деревья, ветки, записи git."""
        blocker = wt.FLEET_WORKTREE_HOME / "run1" / "t2"
        blocker.mkdir(parents=True)
        with self.assertRaises(wt.WorktreeError):
            wt.open_wave(
                self.project, "run1", [("t1", {"a.md"}), ("t2", {"b.md"})], base=self.base
            )
        self.assertFalse((wt.FLEET_WORKTREE_HOME / "run1" / "t1").exists())
        self.assertEqual(git(self.project, "branch", "--list", "codex-fleet/*"), "")

    def test_hold_mode_keeps_trees_and_branches(self) -> None:
        """`--no-integrate`: работа зафиксирована в ветке, но в проект не забрана —
        оркестратор смотрит сам."""
        tree = self.make_tree("run1", "t1", {"a.md"})
        (tree.path / "a.md").write_text("A changed\n")
        wave = wt.close_wave(
            self.project, [tree], run_id="run1", integrate=False, cleanup=False
        )
        self.assertEqual(wave["integration_status"], "held")
        self.assertTrue(tree.path.exists())
        self.assertEqual((self.project / "a.md").read_text(), "A\n")

    def test_cleanup_names_the_orphaned_worker_threads(self) -> None:
        """Дерево снесли — карточка проекта Codex ведёт в никуда; тред назван на уборку."""
        tree = self.make_tree("run1", "t1", {"a.md"})
        tree.thread_id = "019f-aaa"
        (tree.path / "a.md").write_text("A by t1\n")

        wave = wt.close_wave(
            self.project, [tree], run_id="run1", integrate=True, cleanup=True
        )
        self.assertEqual(wave["threads_orphaned"], ["019f-aaa"])
        self.assertEqual(wave["workers"][0]["thread_id"], "019f-aaa")

    def test_kept_tree_keeps_its_thread(self) -> None:
        """Пока папка жива, карточка рабочая — убирать нечего."""
        tree = self.make_tree("run1", "t1", {"a.md"})
        tree.thread_id = "019f-bbb"
        (tree.path / "a.md").write_text("A by t1\n")

        wave = wt.close_wave(
            self.project, [tree], run_id="run1", integrate=True, cleanup=False
        )
        self.assertEqual(wave["threads_orphaned"], [])
        self.assertTrue(tree.path.exists())


if __name__ == "__main__":
    unittest.main()
