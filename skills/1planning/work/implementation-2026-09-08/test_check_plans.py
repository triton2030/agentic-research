from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


WORK = Path(__file__).parent
CHECKER_PATH = WORK / "packages" / "1plan-map" / "scripts" / "check_plans.py"
SPEC = importlib.util.spec_from_file_location("check_plans", CHECKER_PATH)
assert SPEC and SPEC.loader
check_plans = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = check_plans
SPEC.loader.exec_module(check_plans)


EPIC_SECTIONS = """# {name}

## Зачем

Причина эпика.

## Цель

Наблюдаемый результат.

## Канон

docs/canon.md задаёт правило.

## Границы

Входит только эта работа.

## Критерии завершения

Результат проверен целиком.

## Аппетит

Одна неделя.

## Состояние

Работа ещё не начата.
"""

TASK_SECTIONS = """# {name}

## Задача

Один наблюдаемый результат.

## Зачем

Причина задачи.

## Цель

Результат задачи.

## Критерии приёмки

Проверка принимает результат.

## Канон

Применимое правило.

## Подзадачи

- [ ] Первое достигнутое состояние
> [!note]- Отчёт
> статус 2026-09-08: не начато
> доказательство:

- [ ] Второе достигнутое состояние
> [!note]- Отчёт
> статус 2026-09-08: не начато
> доказательство:

- [ ] Третье достигнутое состояние
> [!note]- Отчёт
> статус 2026-09-08: не начато
> доказательство:

## Состояние

Следующий ход.
"""


def _base_yaml() -> str:
    return "views:\n  - type: table\n    name: Plans\n"


class Fixture:
    def __init__(self, root: Path, *, name: str = "Alpha", task_name: str = "First"):
        self.root = root
        self.name = name
        self.task_name = task_name
        self.plans = root / "_ops" / "plans"
        self.epic_dir = self.plans / "эпики" / name
        self.epic = self.epic_dir / f"epic - {name}.md"
        self.task = self.epic_dir / f"task - {task_name}.md"
        (root / "_ops").mkdir(parents=True)
        self.plans.mkdir(parents=True)
        (root / "docs").mkdir()
        (root / "_ops" / "GOAL.md").write_text("# Goal\n\nKeep the map truthful.\n", encoding="utf-8")
        (root / "docs" / "canon.md").write_text("# Canon\n\nRule one.\n", encoding="utf-8")
        (self.plans / "Дашборд.base").write_text(_base_yaml(), encoding="utf-8")
        (self.plans / "Планы.base").write_text(_base_yaml(), encoding="utf-8")
        self.epic_dir.mkdir(parents=True)
        self.epic.write_text(self.epic_text(), encoding="utf-8")
        self.task.write_text(self.task_text(), encoding="utf-8")
        digest, report = check_plans.snapshot_path(root, self.epic.relative_to(root).as_posix())
        if report.issues or digest is None:
            raise AssertionError([issue.message for issue in report.issues])
        self.task.write_text(self.task.read_text(encoding="utf-8").replace("SNAPSHOT", digest), encoding="utf-8")

    @property
    def epic_link(self) -> str:
        return f"[[_ops/plans/эпики/{self.name}/epic - {self.name}]]"

    @property
    def task_link(self) -> str:
        return f"[[_ops/plans/эпики/{self.name}/task - {self.task_name}]]"

    def epic_text(self, *, status: str = "◽ в очереди", derived: bool = True, evidence: str = "") -> str:
        tasks = f'["{self.task_link}"]' if derived else "[]"
        count = 1 if derived else 0
        return (
            "---\n"
            "тип: эпик\n"
            f"описание: \"Исход {self.name}\"\n"
            "область: \"Область результата\"\n"
            f"статус: {status}\n"
            "порядок: 1\n"
            "запуск: true\n"
            "health: не проверено\n"
            "ранний-индикатор: \"Ранний сигнал\"\n"
            "канон: [\"docs/canon.md\"]\n"
            "зависит-от: []\n"
            "допуск: \"Решение владельца\"\n"
            f"задач: {count}\n"
            f"задачи: {tasks}\n"
            "задач-готово: 0\n"
            f"evidence: \"{evidence}\"\n"
            "обновлено: 2026-09-08\n"
            "---\n"
            + EPIC_SECTIONS.format(name=self.name)
        )

    def task_text(self, *, status: str = "◽ в очереди", snapshot: str = "SNAPSHOT", derived: bool = True, evidence: str = "") -> str:
        count = 3 if derived else 0
        return (
            "---\n"
            "тип: задача\n"
            f"эпик: \"{self.epic_link}\"\n"
            "допуск: эпик\n"
            f"эпик-снимок: \"{snapshot}\"\n"
            "траектория: \"Критерий и способ\"\n"
            "режим: execution\n"
            f"статус: {status}\n"
            "порядок: 1\n"
            f"подзадач: {count}\n"
            "подзадач-готово: 0\n"
            f"evidence: \"{evidence}\"\n"
            "обновлено: 2026-09-08\n"
            "вопрос: \"\"\n"
            "---\n"
            + TASK_SECTIONS.format(name=self.task_name)
        )


def _messages(report: check_plans.Report) -> str:
    return "\n".join(issue.message for issue in report.issues)


class CheckerTests(unittest.TestCase):
    def make_fixture(self, **kwargs: object) -> tuple[tempfile.TemporaryDirectory[str], Fixture]:
        holder: tempfile.TemporaryDirectory[str] = tempfile.TemporaryDirectory()
        return holder, Fixture(Path(holder.name), **kwargs)

    def test_valid_pair_new_names_and_cli(self) -> None:
        holder, _fixture = self.make_fixture(name="Имя нового эпика", task_name="Имя новой задачи")
        with holder:
            report = check_plans.validate_root(Path(holder.name))
            self.assertTrue(report.ok, _messages(report))
            result = subprocess.run(
                [sys.executable, str(CHECKER_PATH), "--root", holder.name],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_prefix_without_type_is_not_silently_skipped(self) -> None:
        holder, fixture = self.make_fixture()
        with holder:
            text = fixture.task.read_text(encoding="utf-8").replace("тип: задача\n", "", 1)
            fixture.task.write_text(text, encoding="utf-8")
            report = check_plans.validate_root(Path(holder.name))
            self.assertIn("missing required field 'тип'", _messages(report))

    def test_bad_parent_and_broken_link(self) -> None:
        holder, fixture = self.make_fixture()
        with holder:
            text = fixture.task.read_text(encoding="utf-8").replace(fixture.epic_link, "[[missing epic]]")
            fixture.task.write_text(text, encoding="utf-8")
            report = check_plans.validate_root(Path(holder.name))
            self.assertIn("эпик: broken wikilink", _messages(report))

    def test_section_order_and_checked_report_evidence(self) -> None:
        holder, fixture = self.make_fixture()
        with holder:
            text = fixture.task.read_text(encoding="utf-8").replace("## Канон", "## Зачем", 1)
            text = text.replace("- [ ] Первое", "- [x] Первое", 1)
            fixture.task.write_text(text, encoding="utf-8")
            report = check_plans.validate_root(Path(holder.name))
            messages = _messages(report)
            self.assertIn("H2 sections must be exactly", messages)
            self.assertIn("requires non-empty evidence", messages)

    def test_closed_task_and_epic_require_whole_evidence(self) -> None:
        holder, fixture = self.make_fixture()
        with holder:
            task = fixture.task.read_text(encoding="utf-8").replace("статус: ◽ в очереди", "статус: ✅ готово")
            task = task.replace("- [ ]", "- [x]")
            fixture.task.write_text(task, encoding="utf-8")
            report = check_plans.validate_root(Path(holder.name))
            self.assertIn("closed task requires non-empty evidence", _messages(report))

            epic = fixture.epic.read_text(encoding="utf-8").replace("статус: ◽ в очереди", "статус: ✅ готово")
            fixture.epic.write_text(epic, encoding="utf-8")
            report = check_plans.validate_root(Path(holder.name))
            messages = _messages(report)
            self.assertIn("closed epic requires non-empty evidence", messages)

    def test_snapshot_changes_with_intent_and_canon_but_not_derived_or_state(self) -> None:
        holder, fixture = self.make_fixture()
        with holder:
            root = Path(holder.name)
            original, report = check_plans.snapshot_path(root, fixture.epic.relative_to(root).as_posix())
            self.assertTrue(report.ok)
            assert original

            epic = fixture.epic.read_text(encoding="utf-8")
            epic = epic.replace("Причина эпика.", "Другая причина эпика.")
            fixture.epic.write_text(epic, encoding="utf-8")
            changed, _ = check_plans.snapshot_path(root, fixture.epic.relative_to(root).as_posix())
            self.assertNotEqual(original, changed)

            fixture.epic.write_text(fixture.epic_text(), encoding="utf-8")
            epic = fixture.epic.read_text(encoding="utf-8")
            epic = epic.replace("статус: ◽ в очереди", "статус: 🔨 в работе")
            epic = epic.replace("health: не проверено", "health: 🟢")
            epic = epic.replace("обновлено: 2026-09-08", "обновлено: 2026-09-09")
            epic = epic.replace("задач: 1", "задач: 99").replace("задачи: [\"" + fixture.task_link + "\"]", "задачи: []")
            epic = epic.replace("Работа ещё не начата.", "Состояние изменено.")
            fixture.epic.write_text(epic, encoding="utf-8")
            stable, _ = check_plans.snapshot_path(root, fixture.epic.relative_to(root).as_posix())
            self.assertEqual(original, stable)

            (root / "docs" / "canon.md").write_text("# Canon\n\nRule two.\n", encoding="utf-8")
            changed_again, _ = check_plans.snapshot_path(root, fixture.epic.relative_to(root).as_posix())
            self.assertNotEqual(original, changed_again)

    def test_stale_snapshot_is_data_error(self) -> None:
        holder, fixture = self.make_fixture()
        with holder:
            (Path(holder.name) / "docs" / "canon.md").write_text("changed\n", encoding="utf-8")
            report = check_plans.validate_root(Path(holder.name))
            self.assertIn("эпик-снимок is stale", _messages(report))

    def test_sync_changes_only_derived_fields_and_handles_unindented_lists(self) -> None:
        holder, fixture = self.make_fixture()
        with holder:
            root = Path(holder.name)
            fixture.epic.write_text(fixture.epic_text(derived=False).replace("задачи: []", "задачи:\n- old-link\n"), encoding="utf-8")
            before_task = fixture.task.read_bytes()
            before_goal = (root / "_ops" / "GOAL.md").read_bytes()
            result, changed = check_plans.sync_root(root)
            self.assertTrue(result.ok, _messages(result))
            self.assertEqual(changed, 1)
            self.assertEqual(fixture.task.read_bytes(), before_task)
            self.assertEqual((root / "_ops" / "GOAL.md").read_bytes(), before_goal)
            updated_epic = fixture.epic.read_text(encoding="utf-8")
            self.assertIn(f'задачи: ["{fixture.task_link}"]', updated_epic)
            self.assertNotIn("old-link", updated_epic)
            self.assertIn("Причина эпика.", updated_epic)

    def test_sync_refuses_to_write_on_nonderived_error(self) -> None:
        holder, fixture = self.make_fixture()
        with holder:
            root = Path(holder.name)
            fixture.task.write_text(fixture.task.read_text(encoding="utf-8").replace("траектория: \"Критерий и способ\"", "траектория: null"), encoding="utf-8")
            fixture.epic.write_text(fixture.epic_text(derived=False), encoding="utf-8")
            before_epic = fixture.epic.read_bytes()
            before_task = fixture.task.read_bytes()
            report, changed = check_plans.sync_root(root)
            self.assertFalse(report.ok)
            self.assertEqual(changed, 0)
            self.assertEqual(fixture.epic.read_bytes(), before_epic)
            self.assertEqual(fixture.task.read_bytes(), before_task)

    def test_blocking_dependency_and_duplicate_root_key(self) -> None:
        holder, fixture = self.make_fixture()
        with holder:
            root = Path(holder.name)
            dep_dir = fixture.plans / "эпики" / "Dependency"
            dep_dir.mkdir()
            dep = dep_dir / "epic - Dependency.md"
            dep.write_text(fixture.epic_text().replace("{name}", "Dependency") if "{name}" in fixture.epic_text() else fixture.epic_text(), encoding="utf-8")
            # Replace the copied fixture text with a correctly named second epic.
            dep.write_text(
                fixture.epic_text().replace(f"# {fixture.name}", "# Dependency").replace(f'описание: "Исход {fixture.name}"', 'описание: "Исход Dependency"').replace(f"epic - {fixture.name}", "epic - Dependency"),
                encoding="utf-8",
            )
            epic = fixture.epic.read_text(encoding="utf-8")
            epic = epic.replace("зависит-от: []", 'зависит-от: ["[[_ops/plans/эпики/Dependency/epic - Dependency]]"]')
            epic = epic.replace("статус: ◽ в очереди", "статус: 🔨 в работе")
            fixture.epic.write_text(epic, encoding="utf-8")
            task = fixture.task.read_text(encoding="utf-8").replace("статус: ◽ в очереди", "статус: 🔨 в работе")
            fixture.task.write_text(task, encoding="utf-8")
            report = check_plans.validate_root(root)
            self.assertIn("unfinished necessary epic dependency", _messages(report))

            (root / "_ops" / "plans" / "Дашборд.base").write_text("views:\n  - type: table\nтип: эпик\nтип: задача\n", encoding="utf-8")
            report = check_plans.validate_root(root)
            self.assertIn("duplicate root YAML key", _messages(report))

    def test_short_stem_ambiguity_includes_nonplan_markdown(self) -> None:
        holder, fixture = self.make_fixture()
        with holder:
            root = Path(holder.name)
            (root / "notes").mkdir()
            (root / "notes" / f"epic - {fixture.name}.md").write_text("# unrelated\n", encoding="utf-8")
            question_dir = fixture.plans / "вопросы"
            question_dir.mkdir()
            question = question_dir / "question.md"
            question.write_text(
                "---\n"
                "тип: вопрос\n"
                "статус: открыт\n"
                f"касается: \"[[epic - {fixture.name}]]\"\n"
                "адресат: \"Owner\"\n"
                "срок: \"\"\n"
                "ответ-опора: \"\"\n"
                "обновлено: 2026-09-08\n"
                "---\n"
                "## Вопрос\n\nНужно решение.\n\n## Влияние\n\nЕсть влияние.\n\n## Варианты\n\nЕсть варианты.\n\n## Ответ\n",
                encoding="utf-8",
            )
            report = check_plans.validate_root(root)
            self.assertIn("касается: ambiguous wikilink", _messages(report))

    def test_null_and_unhashable_enum_values_are_reported(self) -> None:
        fields = {
            "тип": "тип: null\n",
            "статус": "статус: []\n",
            "health": "health: {}\n",
            "режим": "режим: []\n",
        }
        for field, replacement in fields.items():
            with self.subTest(field=field):
                holder, fixture = self.make_fixture()
                with holder:
                    path = fixture.task if field in {"тип", "статус", "режим"} else fixture.epic
                    text = path.read_text(encoding="utf-8")
                    line_replacement = replacement
                    old_prefix = field + ": "
                    start = next(line for line in text.splitlines(keepends=True) if line.startswith(old_prefix))
                    text = text.replace(start, line_replacement, 1)
                    path.write_text(text, encoding="utf-8")
                    report = check_plans.validate_root(Path(holder.name))
                    self.assertFalse(report.ok)

    def test_evidence_dash_does_not_close_whole(self) -> None:
        holder, fixture = self.make_fixture()
        with holder:
            task = fixture.task.read_text(encoding="utf-8").replace("статус: ◽ в очереди", "статус: ✅ готово").replace("evidence: \"\"", "evidence: \"—\"").replace("- [ ]", "- [x]")
            fixture.task.write_text(task, encoding="utf-8")
            report = check_plans.validate_root(Path(holder.name))
            self.assertIn("closed task requires non-empty evidence", _messages(report))


if __name__ == "__main__":
    unittest.main()
