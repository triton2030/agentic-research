"""Router form of the planning checker, rule by rule (brief of 2026-09-25).

Numbered comments name the rule of the brief each test class covers.  Legacy
behaviour is covered by test_check_plans_legacy.py; LegacyEquivalenceTests
also compares legacy outcomes with the previous checker while it exists.
"""

from __future__ import annotations

import importlib.util
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Callable
from urllib.parse import quote


WORK = Path(__file__).parent
REPO = WORK.parents[3]
CHECKER_PATH = REPO / "skills" / "shared" / "1planning" / "portable" / "scripts" / "check_plans.py"
PREVIOUS_CHECKER_PATH = REPO / "skills" / "1plan-map" / "versions" / "installed-2026-09-09" / "scripts" / "check_plans.py"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


check_plans = _load("check_plans_router", CHECKER_PATH)

RECALL = "recall-54ae274cd85c4525b4f3e79af41e3127"
EPIC_LINK = "[[_ops/plans/эпики/Экспорт/epic - Экспорт]]"
TASK_LINK = "[[_ops/plans/эпики/Экспорт/task - CSV]]"

# The router pair below is the reusable example of the form.
ROUTER_EPIC = f"""---
тип: эпик
описание: "Студия выгружает заказы в CSV"
область: "Экспорт"
статус: ◽ в очереди
порядок: 1
запуск: true
health: не проверено
ранний-индикатор: "Первая выгрузка открывается в таблице"
зависит-от: []
допуск: "_ops/chat-recall/2026-09-25-120000-Claude-demo.md#{RECALL}"
задач: 1
задачи: ["{TASK_LINK}"]
задач-готово: 0
evidence: ""
обновлено: 2026-09-25
---

# Экспорт

## Цель

Студия выгружает свои заказы в CSV и открывает файл в таблице без правок.

- [Цель проекта](<../../../GOAL.md>) — ради неё Студия получает данные без ручного переноса.
- [Решение владельца](<../../../chat-recall/2026-09-25-120000-Claude-demo.md#{RECALL}>) — граница: только CSV и только выгрузка.

## Не входит

Импорт заказов и форматы, кроме CSV.

## Порядок

1. [[_ops/plans/эпики/Экспорт/task - CSV|CSV]] — формат файла и кнопка выгрузки.

## Готово, когда

- [ ] Выгрузка реальной Студии открывается в таблице без правок.
"""

TASK_FRONTMATTER = f"""---
тип: задача
эпик: "{EPIC_LINK}"
допуск: эпик
режим: execution
статус: ◽ в очереди
порядок: 1
подзадач: 2
подзадач-готово: 0
evidence: ""
обновлено: 2026-09-25
вопрос: ""
---
"""

READ_BLOCK = f"""- [Формат — колонки](<../../../../_docs/Экспорт/Формат.md#Колонки>) — порядок и имена колонок.
- [[_docs/Экспорт/Формат#Кодировка]] — почему UTF-8 с BOM.
- [Слова владельца](<../../../chat-recall/2026-09-25-120000-Claude-demo.md#{RECALL}>) — зачем Студии выгрузка.
"""

TASK_BODY = f"""
# CSV

## Цель

Студия скачивает заказы одним CSV-файлом.

## Прочитать

{READ_BLOCK}
## Не входит

Импорт CSV обратно.

## Готово, когда

- [ ] Файл открывается в таблице без правок.
- [ ] Колонки совпадают с [форматом](<../../../../_docs/Экспорт/Формат.md#колонки>).
"""

ROUTER_TASK = TASK_FRONTMATTER + TASK_BODY

FORMAT_DOC = """---
description: "Формат выгрузки заказов"
---
# Формат

## Колонки

Номер, дата, сумма.

## Кодировка

UTF-8 с BOM.

## Кто чем владеет: Студия

Студия.

## Итог

Первый.

## Итог

Второй.

Строка с блоком ^blk-1

```md
## Скрытый заголовок
```
"""

RECALL_DOC = f"""# Chat recall — 2026-09-25 — Claude demo

### {RECALL}

* 2026-09-25T12:00:00+05:00 — "Студии нужна выгрузка заказов в CSV" — type: решение
"""

QUESTION = """---
тип: вопрос
статус: открыт
касается: "[[_ops/plans/эпики/Экспорт/task - CSV]]"
адресат: "Founder"
срок: ""
ответ-опора: ""
обновлено: 2026-09-25
---
{sections}"""

BASES_YAML = "views:\n  - type: table\n    name: Plans\n"


class RouterProject:
    """A temporary project holding the example router epic and task."""

    def __init__(self, root: Path):
        self.root = root
        self.plans = root / "_ops" / "plans"
        self.epic_dir = self.plans / "эпики" / "Экспорт"
        self.epic = self.epic_dir / "epic - Экспорт.md"
        self.task = self.epic_dir / "task - CSV.md"
        self.docs = root / "_docs" / "Экспорт"
        recall = root / "_ops" / "chat-recall" / "2026-09-25-120000-Claude-demo.md"
        for folder in (self.epic_dir, self.docs, recall.parent):
            folder.mkdir(parents=True, exist_ok=True)
        (root / "_ops" / "GOAL.md").write_text("# Goal\n\nСтудия выгружает заказы.\n", encoding="utf-8")
        for base in ("Дашборд.base", "Планы.base"):
            (self.plans / base).write_text(BASES_YAML, encoding="utf-8")
        (self.docs / "Формат.md").write_text(FORMAT_DOC, encoding="utf-8")
        (self.docs / "Два слова.md").write_text("# Два слова\n", encoding="utf-8")
        recall.write_text(RECALL_DOC, encoding="utf-8")
        self.epic.write_text(ROUTER_EPIC, encoding="utf-8")
        self.task.write_text(ROUTER_TASK, encoding="utf-8")

    def edit(self, path: Path, old: str, new: str) -> None:
        text = path.read_text(encoding="utf-8")
        if old not in text:
            raise AssertionError(f"{old!r} is not in {path.name}")
        path.write_text(text.replace(old, new, 1), encoding="utf-8")

    def read_links(self, *lines: str) -> None:
        """Replace the task's Прочитать list with the given lines."""

        self.task.write_text(ROUTER_TASK.replace(READ_BLOCK, "".join(line + "\n" for line in lines)), encoding="utf-8")

    def messages(self) -> list[str]:
        return [issue.message for issue in check_plans.validate_root(self.root).issues]


def _line_of(path: Path, fragment: str) -> int:
    lines = path.read_text(encoding="utf-8").splitlines()
    return next(index for index, line in enumerate(lines, 1) if fragment in line)


class RouterTestCase(unittest.TestCase):
    def setUp(self) -> None:
        holder = tempfile.TemporaryDirectory()
        self.addCleanup(holder.cleanup)
        self.project = RouterProject(Path(holder.name))

    def assertValid(self) -> None:
        self.assertEqual(self.project.messages(), [])

    def assertMessage(self, fragment: str) -> list[str]:
        messages = self.project.messages()
        self.assertTrue(any(fragment in message for message in messages), f"{fragment!r} not in {messages!r}")
        return messages


class FormDetectionTests(RouterTestCase):
    """Rule 1: the exact H2 sequence tells the forms apart."""

    def test_example_router_pair_is_valid_and_detected(self) -> None:
        report = check_plans.validate_root(self.project.root)
        self.assertEqual([issue.message for issue in report.issues], [])
        forms = {doc.path.name: (doc.form, doc.exact_form) for doc in report.project.docs}
        self.assertEqual(forms, {"epic - Экспорт.md": ("router", True), "task - CSV.md": ("router", True)})

    def test_unknown_task_sequence_is_one_error_naming_both_forms(self) -> None:
        self.project.edit(self.project.task, "## Не входит", "## Вне рамки")
        messages = self.project.messages()
        h2 = [message for message in messages if message.startswith("H2 sections")]
        self.assertEqual(len(h2), 1, messages)
        self.assertIn("['Цель', 'Прочитать', 'Не входит', 'Готово, когда'] (router form)", h2[0])
        self.assertIn("['Задача', 'Зачем', 'Цель', 'Критерии приёмки', 'Основания', 'Подзадачи', 'Состояние'] (legacy form)", h2[0])
        # The titles lean to the router form: no advice to add legacy fields.
        self.assertFalse([message for message in messages if "эпик-снимок" in message or "траектория" in message], messages)

    def test_unknown_epic_sequence_is_one_error_naming_both_forms(self) -> None:
        self.project.edit(self.project.epic, "## Порядок", "## Очередь")
        messages = self.project.messages()
        h2 = [message for message in messages if message.startswith("H2 sections")]
        self.assertEqual(len(h2), 1, messages)
        self.assertIn("['Цель', 'Не входит', 'Порядок', 'Готово, когда'] (router form)", h2[0])
        self.assertIn("['Зачем', 'Цель', 'Основания', 'Границы', 'Критерии завершения', 'Аппетит', 'Состояние'] (legacy form)", h2[0])
        self.assertFalse([message for message in messages if "основания" in message], messages)

    def test_router_sections_must_not_be_empty(self) -> None:
        self.project.edit(self.project.task, "Импорт CSV обратно.\n", "")
        self.assertMessage("section 'Не входит' must not be empty")

    def test_question_documents_are_unchanged(self) -> None:
        folder = self.project.plans / "вопросы"
        folder.mkdir()
        question = folder / "Кодировка.md"
        question.write_text(QUESTION.format(sections="## Вопрос\n\nКакая?\n\n## Влияние\n\nФормат.\n\n## Варианты\n\nUTF-8.\n\n## Ответ\n"), encoding="utf-8")
        self.assertValid()
        question.write_text(QUESTION.format(sections="## Вопрос\n\nКакая?\n\n## Ответ\n"), encoding="utf-8")
        self.assertEqual(
            self.project.messages(),
            ["H2 sections must be exactly ['Вопрос', 'Влияние', 'Варианты', 'Ответ'] in order; got ['Вопрос', 'Ответ']"],
        )


LEGACY_EPIC = """---
тип: эпик
описание: "Исход {name}"
область: "Область результата"
статус: ◽ в очереди
порядок: {order}
запуск: true
health: не проверено
ранний-индикатор: "Ранний сигнал"
основания: ["docs/decision.md"]
зависит-от: []
допуск: "Решение владельца"
задач: 1
задачи: ["[[_ops/plans/эпики/{name}/task - {task}]]"]
задач-готово: 0
evidence: ""
обновлено: 2026-09-08
---
# {name}

## Зачем

Причина эпика.

## Цель

Наблюдаемый результат.

## Основания

docs/decision.md задаёт правило.

## Границы

Входит только эта работа.

## Критерии завершения

Результат проверен целиком.

## Аппетит

Одна неделя.

## Состояние

Работа ещё не начата.
"""

LEGACY_TASK = """---
тип: задача
эпик: "[[_ops/plans/эпики/{epic}/epic - {epic}]]"
допуск: эпик
эпик-снимок: "{snapshot}"
траектория: "Критерий и способ"
режим: execution
статус: ◽ в очереди
порядок: {order}
подзадач: 3
подзадач-готово: 0
evidence: ""
обновлено: 2026-09-08
вопрос: ""
---
# {name}

## Задача

Один наблюдаемый результат.

## Зачем

Причина задачи; [пример ссылки](<нет такого файла.md#Нет>) и [[нет такой заметки]] не проверяются.

## Цель

Результат задачи.

## Критерии приёмки

Проверка принимает результат.

## Основания

Применимое решение.

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


def write_legacy_pair(root: Path, name: str = "Архив", task: str = "Старая", order: int = 2) -> tuple[Path, Path]:
    """Write a valid legacy epic and task; their bodies hold unresolved links."""

    for folder in (root / "_ops" / "plans", root / "docs"):
        folder.mkdir(parents=True, exist_ok=True)
    goal = root / "_ops" / "GOAL.md"
    if not goal.exists():
        goal.write_text("# Goal\n\nKeep the map truthful.\n", encoding="utf-8")
    for base in ("Дашборд.base", "Планы.base"):
        path = root / "_ops" / "plans" / base
        if not path.exists():
            path.write_text(BASES_YAML, encoding="utf-8")
    (root / "docs" / "decision.md").write_text("# Decision\n\nRule one.\n", encoding="utf-8")
    folder = root / "_ops" / "plans" / "эпики" / name
    folder.mkdir(parents=True)
    epic = folder / f"epic - {name}.md"
    epic.write_text(LEGACY_EPIC.format(name=name, task=task, order=order), encoding="utf-8")
    digest, report = check_plans.snapshot_path(root, epic.relative_to(root).as_posix())
    assert digest and report.ok, [issue.message for issue in report.issues]
    task_path = folder / f"task - {task}.md"
    task_path.write_text(LEGACY_TASK.format(epic=name, name=task, snapshot=digest, order=1), encoding="utf-8")
    return epic, task_path


class LegacySideBySideTests(RouterTestCase):
    """Rule 2: legacy files keep their checks and get no link checks."""

    def test_legacy_pair_beside_router_pair(self) -> None:
        epic, task = write_legacy_pair(self.project.root)
        self.assertValid()
        forms = {doc.path.name: doc.form for doc in check_plans.validate_root(self.project.root).project.docs}
        self.assertEqual(forms[epic.name], "legacy")
        self.assertEqual(forms[task.name], "legacy")

    def test_legacy_checks_still_apply(self) -> None:
        _, task = write_legacy_pair(self.project.root)
        text = task.read_text(encoding="utf-8").replace("траектория: \"Критерий и способ\"\n", "")
        task.write_text(text.replace("- [ ] Первое", "- [x] Первое", 1), encoding="utf-8")
        messages = self.project.messages()
        self.assertIn("missing required field 'траектория'", messages)
        self.assertTrue(any("requires non-empty evidence" in message for message in messages), messages)


class RouterTaskTests(RouterTestCase):
    """Rule 3: a router task."""

    REQUIRED = ("тип", "эпик", "допуск", "режим", "статус", "порядок", "подзадач", "подзадач-готово", "evidence", "обновлено")

    def write_task(self, text: str) -> None:
        self.project.task.write_text(text, encoding="utf-8")

    def test_required_fields(self) -> None:
        for key in self.REQUIRED:
            with self.subTest(field=key):
                line = next(line for line in ROUTER_TASK.splitlines(keepends=True) if line.startswith(f"{key}:"))
                self.write_task(ROUTER_TASK.replace(line, "", 1))
                self.assertMessage(f"missing required field {key!r}")

    def test_question_field_is_optional(self) -> None:
        self.write_task(ROUTER_TASK.replace('вопрос: ""\n', ""))
        self.assertValid()

    def test_value_rules_stay_as_today(self) -> None:
        cases = {
            "режим: execution": ("режим: sprint", "field 'режим' must be execution or wayfinding"),
            "порядок: 1": ("порядок: 0", "field 'порядок' must be a positive integer"),
            'вопрос: ""': ("вопрос: null", "optional field 'вопрос' must be a wikilink or empty string"),
            "статус: ◽ в очереди": ("статус: начато", "task status is outside the shared status dictionary"),
            "допуск: эпик": ('допуск: ""', "field 'допуск' must not be empty"),
            "подзадач: 2": ("подзадач: -1", "field 'подзадач' must be non-negative"),
        }
        for old, (new, message) in cases.items():
            with self.subTest(old=old):
                self.write_task(ROUTER_TASK.replace(old, new, 1))
                self.assertMessage(message)

    def test_legacy_only_fields_are_rejected(self) -> None:
        for key, value in (("эпик-снимок", '"' + "0" * 64 + '"'), ("траектория", '"Критерий и способ"')):
            with self.subTest(field=key):
                self.write_task(ROUTER_TASK.replace("режим: execution\n", f"режим: execution\n{key}: {value}\n"))
                self.assertMessage(f"legacy-only field {key!r} must be absent from a router task")

    def test_checkboxes_only_in_done_section(self) -> None:
        self.project.edit(self.project.task, "одним CSV-файлом.\n", "одним CSV-файлом.\n\n- [ ] Лишний чекбокс\n")
        self.project.edit(self.project.task, "# CSV\n", "# CSV\n\n- [x] Чекбокс до разделов\n")
        messages = self.project.messages()
        for label in ("- [ ] Лишний чекбокс", "- [x] Чекбокс до разделов"):
            line = _line_of(self.project.task, label)
            self.assertIn(f"line {line}: checkbox outside 'Готово, когда'; a router task keeps its checkboxes there only", messages)
        # Stray boxes are not done-checks: the counters still see two.
        self.assertFalse([message for message in messages if "подзадач" in message], messages)

    def test_done_section_needs_checkboxes_with_text(self) -> None:
        done = "- [ ] Файл открывается в таблице без правок.\n- [ ] Колонки совпадают с [форматом](<../../../../_docs/Экспорт/Формат.md#колонки>).\n"
        self.write_task(ROUTER_TASK.replace(done, "Файл открывается в таблице без правок.\n"))
        self.assertMessage("section 'Готово, когда' must contain at least one checkbox")
        self.write_task(ROUTER_TASK.replace("- [ ] Файл открывается в таблице без правок.", "- [ ]"))
        line = _line_of(self.project.task, "- [ ]")
        self.assertEqual(self.project.messages(), [f"line {line}: 'Готово, когда' checkbox has empty text"])

    def test_report_callouts_are_rejected_anywhere(self) -> None:
        report = "> [!note]- Отчёт\n> статус 2026-09-25: сделано\n> доказательство: коммит abc123\n"
        self.project.edit(self.project.task, "- [ ] Файл открывается в таблице без правок.\n", "- [ ] Файл открывается в таблице без правок.\n" + report)
        self.project.edit(self.project.task, "одним CSV-файлом.\n", "одним CSV-файлом.\n\n> [!NOTE]+ Отчет\n> статус 2026-09-25: начато\n")
        messages = self.project.messages()
        for marker in ("> [!note]- Отчёт", "> [!NOTE]+ Отчет"):
            line = _line_of(self.project.task, marker)
            self.assertIn(f"line {line}: a report callout does not belong in a router task; the report goes to the final message and the commit", messages)

    def test_counters_follow_done_section_in_validation_and_sync(self) -> None:
        self.project.edit(self.project.task, "подзадач: 2\nподзадач-готово: 0\n", "подзадач: 0\nподзадач-готово: 5\n")
        self.project.edit(self.project.task, "- [ ] Файл открывается", "- [x] Файл открывается")
        messages = self.project.messages()
        self.assertIn("подзадач must equal checkbox count (2)", messages)
        self.assertIn("подзадач-готово must equal checked checkbox count (1)", messages)
        body = self.project.task.read_text(encoding="utf-8").split("---\n", 2)[2]
        report, changed = check_plans.sync_root(self.project.root)
        self.assertEqual([issue.message for issue in report.issues], [])
        self.assertEqual(changed, 1)
        text = self.project.task.read_text(encoding="utf-8")
        self.assertIn("подзадач: 2\nподзадач-готово: 1\n", text)
        self.assertEqual(text.split("---\n", 2)[2], body)

    def test_closure_rules(self) -> None:
        closed = ROUTER_TASK.replace("статус: ◽ в очереди", "статус: ✅ готово")
        self.project.edit(self.project.epic, "задач-готово: 0", "задач-готово: 1")
        self.write_task(closed.replace('evidence: ""', 'evidence: "коммит abc123"'))
        self.assertMessage("closed task requires every 'Готово, когда' checkbox checked (0 of 2)")
        checked = closed.replace("- [ ]", "- [x]").replace("подзадач-готово: 0", "подзадач-готово: 2")
        self.write_task(checked)
        self.assertEqual(self.project.messages(), ["closed task requires non-empty evidence"])
        self.write_task(checked.replace('evidence: ""', 'evidence: "—"'))
        self.assertEqual(self.project.messages(), ["closed task requires non-empty evidence"])
        self.write_task(checked.replace('evidence: ""', 'evidence: "коммит abc123"'))
        self.assertValid()
        self.project.edit(self.project.epic, "задач-готово: 1", "задач-готово: 0")
        self.write_task(ROUTER_TASK.replace('evidence: ""', 'evidence: "рано"'))
        self.assertEqual(self.project.messages(), ["task evidence must stay empty until the task is accepted"])

    def test_read_section_needs_a_link(self) -> None:
        self.project.read_links("Документ о формате выгрузки.")
        self.assertEqual(self.project.messages(), ["section 'Прочитать' must contain at least one link"])
        self.project.read_links("- [[_docs/Экспорт/Формат#Кодировка]] — почему UTF-8 с BOM.")
        self.assertValid()
        self.project.read_links("- [Формат](<../../../../_docs/Экспорт/Формат.md>) — весь документ.")
        self.assertValid()

    def test_visible_text_budget(self) -> None:
        limit = check_plans.ROUTER_TASK_MAX_CHARS
        self.assertEqual(limit, 3500)
        link = "[Формат](<../../../../_docs/Экспорт/Формат.md#Колонки>)"
        body = "\n# CSV\n\n## Цель\n\n{goal}\n\n## Прочитать\n\n- " + link + " — колонки.\n\n## Не входит\n\nИмпорт.\n\n## Готово, когда\n\n- [ ] Файл открывается.\n"
        frontmatter = TASK_FRONTMATTER.replace("подзадач: 2", "подзадач: 1")
        # Independent count: the destination is dropped, the link text stays.
        base = len(body.format(goal="").replace(link, "Формат").strip())
        at_limit = "ж" * (limit - base)
        self.write_task(frontmatter + body.format(goal=at_limit))
        self.assertValid()
        self.write_task(frontmatter + body.format(goal=at_limit + "ж"))
        self.assertEqual(
            self.project.messages(),
            [
                f"router task has {limit + 1} visible characters, over the limit of {limit}: a router links to "
                'documentation instead of retelling it, so shorten the "why" notes or split the task'
            ],
        )

    def test_link_destinations_do_not_count(self) -> None:
        name = "export-format-" + "x" * 150
        (self.project.docs / f"{name}.md").write_text("# Длинное имя\n", encoding="utf-8")
        lines = [f"- [Ф{index}](<../../../../_docs/Экспорт/{name}.md>) — зачем." for index in range(20)]
        lines += [f"- [[_docs/Экспорт/{name}|В{index}]] — зачем." for index in range(20)]
        self.project.read_links(*lines)
        self.assertGreater(len(self.project.task.read_text(encoding="utf-8")), 2 * check_plans.ROUTER_TASK_MAX_CHARS)
        self.assertValid()


class RouterEpicTests(RouterTestCase):
    """Rule 4: a router epic."""

    def test_grounds_fields_are_rejected(self) -> None:
        for key in ("основания", "канон"):
            with self.subTest(field=key):
                # A missing path shows the field is rejected, not validated as grounds.
                self.project.epic.write_text(ROUTER_EPIC.replace("зависит-от: []\n", f'зависит-от: []\n{key}: ["docs/нет.md"]\n'), encoding="utf-8")
                self.assertEqual(self.project.messages(), [f"legacy-only field {key!r} must be absent from a router epic"])

    def test_other_fields_as_today(self) -> None:
        cases = {
            'описание: "Студия выгружает заказы в CSV"\n': ("", "missing required field 'описание'"),
            "health: не проверено": ("health: 🟣", "field 'health' must be 🟢, 🟠, 🔴 or не проверено"),
            "запуск: true": ("запуск: null", "field 'запуск' must be boolean"),
        }
        for old, (new, message) in cases.items():
            with self.subTest(old=old):
                self.project.epic.write_text(ROUTER_EPIC.replace(old, new, 1), encoding="utf-8")
                self.assertMessage(message)

    def test_goal_links_a_ground(self) -> None:
        grounds = (
            "- [Цель проекта](<../../../GOAL.md>) — ради неё Студия получает данные без ручного переноса.\n"
            f"- [Решение владельца](<../../../chat-recall/2026-09-25-120000-Claude-demo.md#{RECALL}>) — граница: только CSV и только выгрузка.\n"
        )
        message = (
            "section 'Цель' must link at least one ground — an owner decision, principle or the project goal — "
            "that shaped the epic's goal, boundary or order"
        )
        self.project.edit(self.project.epic, grounds, "- Основание названо словами, без ссылки.\n")
        self.assertEqual(self.project.messages(), [message])
        # A link in another section does not ground the goal.
        self.project.edit(self.project.epic, "Импорт заказов и форматы, кроме CSV.", "Импорт заказов и форматы, кроме CSV; см. [цель проекта](<../../../GOAL.md>).")
        self.assertEqual(self.project.messages(), [message])
        # One wikilink in «Цель» is enough.
        self.project.edit(self.project.epic, "- Основание названо словами, без ссылки.\n", "- [[_ops/GOAL|Цель проекта]] — зачем выгрузка.\n")
        self.assertValid()

    def test_order_needs_a_list_item(self) -> None:
        self.project.edit(self.project.epic, "1. [[_ops/plans/эпики/Экспорт/task - CSV|CSV]] — формат файла и кнопка выгрузки.", "Сначала [[_ops/plans/эпики/Экспорт/task - CSV|CSV]].")
        self.assertEqual(self.project.messages(), ["section 'Порядок' must contain at least one list item"])

    def test_order_links_every_task_of_the_folder(self) -> None:
        second = self.project.epic_dir / "task - Кодировка.md"
        second.write_text(ROUTER_TASK.replace("# CSV", "# Кодировка").replace("порядок: 1", "порядок: 2"), encoding="utf-8")
        self.project.edit(self.project.epic, "задач: 1", "задач: 2")
        self.project.edit(self.project.epic, f'задачи: ["{TASK_LINK}"]', f'задачи: ["{TASK_LINK}","[[_ops/plans/эпики/Экспорт/task - Кодировка]]"]')
        self.assertEqual(self.project.messages(), ["section 'Порядок' does not link task 'task - Кодировка.md'"])
        # A link from another section does not order the work.
        self.project.edit(self.project.epic, "открывает файл в таблице без правок.\n", "открывает файл в таблице без правок; см. [[_ops/plans/эпики/Экспорт/task - Кодировка]].\n")
        self.assertEqual(self.project.messages(), ["section 'Порядок' does not link task 'task - Кодировка.md'"])
        # A relative Markdown link resolving to the task file counts.
        self.project.edit(self.project.epic, "кнопка выгрузки.\n", "кнопка выгрузки.\n2. [Кодировка](<task - Кодировка.md>) — BOM для таблиц.\n")
        self.assertValid()

    def test_epic_body_links_are_checked(self) -> None:
        self.project.edit(self.project.epic, "## Не входит\n\n", "## Не входит\n\nСм. [решение](<../../../../_docs/Нет.md>).\n")
        self.assertMessage("link target does not exist: '../../../../_docs/Нет.md'")


class LinkTests(RouterTestCase):
    """Rule 5: body links resolve; code holds no links."""

    def test_markdown_link_targets(self) -> None:
        self.project.read_links(
            "- [Сайт](https://example.com/x) — внешний.",
            "- [Почта](mailto:studio@example.com) — внешний.",
            "- [Хранилище](obsidian://open?vault=mavo&file=x) — внешний.",
            "- [Два слова](../../../../_docs/Экспорт/Два%20слова.md) — %20.",
            "- [Два слова](<../../../../_docs/Экспорт/Два слова.md>) — скобки.",
            "- [Папка](<../../../../_docs/Экспорт/>) — папка.",
            '- [С подписью](<../../../../_docs/Экспорт/Формат.md> "Формат") — title.',
            "- ![Схема](<../../../../_docs/Экспорт/Два слова.md>) — картинка тоже ссылка.",
        )
        self.assertValid()
        cases = {
            "- [Нет](<../../../../_docs/Нет.md>) — нет.": "link target does not exist: '../../../../_docs/Нет.md'",
            "- [Вне](<../../../../../вне.md>) — вне.": "link target is outside the project root: '../../../../../вне.md'",
            "- [Абсолютный](</etc/hosts>) — вне.": "link target is outside the project root: '/etc/hosts'",
            "- [Пусто]() — пусто.": "link '[Пусто]()' has an empty destination",
            "- [Строка](decision.md:3) — не схема.": "link target does not exist: 'decision.md:3'",
        }
        for line, message in cases.items():
            with self.subTest(line=line):
                self.project.read_links(line)
                self.assertEqual(self.project.messages(), [f"line {_line_of(self.project.task, line)}: {message}"])

    def test_fragments_match_headings_slugs_and_blocks(self) -> None:
        (self.project.docs / "script.py").write_text("print('ok')\n", encoding="utf-8")
        doc = "../../../../_docs/Экспорт/Формат.md"
        self.project.read_links(
            f"- [a](<{doc}#КОДИРОВКА>) — регистр.",
            f"- [b](<{doc}#Кто   чем владеет:  Студия>) — пробелы.",
            f"- [c]({doc}#кто-чем-владеет-студия) — slug GitHub.",
            f"- [d]({doc}#итог-1) — повтор заголовка.",
            f"- [e](<{doc}#Кто чем владеет Студия>) — без двоеточия, как у Obsidian.",
            f"- [f]({doc}#{quote('Колонки')}) — URL-кодирование.",
            f"- [g]({doc}#^blk-1) — блок.",
            f"- [h](<../../../chat-recall/2026-09-25-120000-Claude-demo.md#{RECALL}>) — цитата владельца.",
            "- [i](#Цель) — этот файл.",
            "- [j](../../../../_docs/Экспорт/script.py#L1) — не Markdown: якорь не проверяется.",
        )
        self.assertValid()
        cases = {
            f"- [a](<{doc}#Нет такого>) — нет.": f"link '{doc}#Нет такого' points to a missing heading in _docs/Экспорт/Формат.md",
            f"- [b]({doc}#L3) — номер строки.": f"link '{doc}#L3' points to a missing heading in _docs/Экспорт/Формат.md",
            f"- [c](<{doc}#Скрытый заголовок>) — в коде.": "points to a missing heading in _docs/Экспорт/Формат.md",
            f"- [d]({doc}#^нет) — блок.": f"link '{doc}#^нет' points to a missing block in _docs/Экспорт/Формат.md",
            "- [e](#Нет) — этот файл.": "link '#Нет' points to a missing heading in _ops/plans/эпики/Экспорт/task - CSV.md",
        }
        for line, message in cases.items():
            with self.subTest(line=line):
                self.project.read_links(line)
                messages = self.project.messages()
                self.assertEqual(len(messages), 1, messages)
                self.assertTrue(messages[0].startswith(f"line {_line_of(self.project.task, line)}: "), messages)
                self.assertIn(message, messages[0])

    def test_wikilinks_resolve_like_obsidian(self) -> None:
        for folder in ("Другое", "А", "Б"):
            (self.project.root / "_docs" / folder).mkdir()
        (self.project.root / "_docs" / "Другое" / "Уникальная заметка.md").write_text("# Заметка\n", encoding="utf-8")
        (self.project.root / "_docs" / "А" / "Дубль.md").write_text("# А\n", encoding="utf-8")
        (self.project.root / "_docs" / "Б" / "Дубль.md").write_text("# Б\n", encoding="utf-8")
        (self.project.docs / "схема.png").write_bytes(b"\x89PNG\r\n")
        self.project.read_links(
            "- [[_docs/Экспорт/Формат]] — путь от корня.",
            "- [[_docs/Экспорт/Формат.md|с расширением]] — .md в ссылке.",
            "- [[Уникальная заметка]] — уникальное имя.",
            "- [[уникальная заметка]] — имя в другом регистре.",
            "- [[Экспорт/Формат#Колонки|колонки]] — хвост пути.",
            "- [[Формат#Кто чем владеет Студия]] — заголовок.",
            f"- [[2026-09-25-120000-Claude-demo#{RECALL}]] — цитата владельца.",
            "- [[_docs/Экспорт/Формат#^blk-1]] — блок.",
            "- [[#Не входит]] — этот файл.",
            "- [[../../../../_docs/Экспорт/Формат]] — относительный путь.",
            "- ![[схема.png]] — вставка картинки.",
            "- ![[_docs/Экспорт/Формат#Колонки]] — вставка раздела.",
        )
        self.assertValid()
        cases = {
            "- [[Нет такой]] — нет.": "wikilink '[[Нет такой]]' is broken",
            "- [[Дубль]] — два файла.": "wikilink '[[Дубль]]' is ambiguous (2 files match)",
            "- [[_docs/Экспорт/Формат#Нет]] — нет раздела.": "wikilink '[[_docs/Экспорт/Формат#Нет]]' points to a missing heading in _docs/Экспорт/Формат.md",
            "- ![[нет.png]] — нет картинки.": "wikilink '![[нет.png]]' is broken",
            "- [[#Нет]] — нет в этом файле.": "wikilink '[[#Нет]]' points to a missing heading in _ops/plans/эпики/Экспорт/task - CSV.md",
        }
        for line, message in cases.items():
            with self.subTest(line=line):
                self.project.read_links(line)
                self.assertEqual(self.project.messages(), [f"line {_line_of(self.project.task, line)}: {message}"])

    def test_links_in_code_are_ignored(self) -> None:
        self.project.read_links(
            "- [[_docs/Экспорт/Формат]] — настоящая ссылка.",
            "- Пример: `[нет](нет.md)` и `` [[нет]] `` — в коде.",
            "",
            "```md",
            "[нет](нет.md) [[нет]]",
            "```",
            "",
            "~~~",
            "[нет](нет.md) [[нет]]",
            "~~~",
        )
        self.assertValid()

    def test_link_text_may_wrap_across_lines(self) -> None:
        self.project.read_links("- [Формат —", "  колонки](<../../../../_docs/Экспорт/Нет.md>) — перенос строки.")
        self.assertEqual(self.project.messages(), [f"line {_line_of(self.project.task, '- [Формат —')}: link target does not exist: '../../../../_docs/Экспорт/Нет.md'"])

    def test_frontmatter_links_are_checked_as_before(self) -> None:
        self.project.edit(self.project.task, EPIC_LINK, "[[missing epic]]")
        self.assertMessage("эпик: broken wikilink")


ASSETS = REPO / "skills" / "shared" / "1planning" / "portable" / "assets"


def _fill_template(text: str) -> str:
    """Fill a shipped template: link destinations point at GOAL, other placeholders get text."""

    text = text.replace("{{YYYY-MM-DD}}", "2026-09-25").replace("{{Эпик}}", "Экспорт")
    text = re.sub(r"\(<\{\{[^}]*\}\}>\)", "(<../../../GOAL.md>)", text)
    return re.sub(r"\{\{.*?\}\}", "Заполненное содержание", text, flags=re.S)


@unittest.skipUnless((ASSETS / "epic-template.md").is_file() and (ASSETS / "task-template.md").is_file(), "router templates are not present")
class ShippedTemplateTests(unittest.TestCase):
    """The shipped router templates, once filled, pass the checker."""

    def test_filled_templates_pass(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            plans = root / "_ops" / "plans"
            epic_dir = plans / "эпики" / "Экспорт"
            epic_dir.mkdir(parents=True)
            (root / "_ops" / "GOAL.md").write_text("# Цель\n\nВыгрузка заказов.\n", encoding="utf-8")
            for base in ("Дашборд.base", "Планы.base"):
                source = ASSETS / "map" / base
                (plans / base).write_text(source.read_text(encoding="utf-8") if source.is_file() else BASES_YAML, encoding="utf-8")
            epic = _fill_template((ASSETS / "epic-template.md").read_text(encoding="utf-8"))
            self.assertIn('допуск: ""\n', epic)
            self.assertIn("## Порядок\n\n", epic)
            epic = epic.replace('допуск: ""\n', 'допуск: "решение владельца 2026-09-25"\n', 1)
            epic = epic.replace("## Порядок\n\n", "## Порядок\n\n1. [[_ops/plans/эпики/Экспорт/task - CSV|CSV]] — выгрузка.\n", 1)
            (epic_dir / "epic - Экспорт.md").write_text(epic, encoding="utf-8")
            task = _fill_template((ASSETS / "task-template.md").read_text(encoding="utf-8"))
            (epic_dir / "task - CSV.md").write_text(task, encoding="utf-8")
            # A temporary project: --sync only sets the epic's task counters.
            report, changed = check_plans.sync_root(root)
            self.assertEqual([issue.message for issue in report.issues], [])
            self.assertEqual(changed, 1)
            report = check_plans.validate_root(root)
            self.assertEqual([issue.message for issue in report.issues], [])
            forms = {doc.path.name: (doc.form, doc.exact_form) for doc in report.project.docs}
            self.assertEqual(forms, {"epic - Экспорт.md": ("router", True), "task - CSV.md": ("router", True)})


class CliTests(RouterTestCase):
    """Rule 6: the CLI is unchanged; --sync runs only in temporary projects."""

    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(CHECKER_PATH), "--root", str(self.project.root), *args],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_root_sync_and_snapshot(self) -> None:
        result = self.run_cli()
        self.assertEqual((result.returncode, result.stdout), (0, "OK\n"), result.stderr)
        self.project.edit(self.project.task, "подзадач: 2", "подзадач: 7")
        result = self.run_cli()
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stderr, "_ops/plans/эпики/Экспорт/task - CSV.md: derived: подзадач must equal checkbox count (2)\n")
        result = self.run_cli("--sync")
        self.assertEqual((result.returncode, result.stdout), (0, "OK (synchronized 1 file(s))\n"), result.stderr)
        result = self.run_cli("--snapshot", "_ops/plans/эпики/Экспорт/epic - Экспорт.md")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertRegex(result.stdout, r"^[0-9a-f]{64}\n$")

    def test_bad_invocation_exits_2(self) -> None:
        result = subprocess.run([sys.executable, str(CHECKER_PATH), "--root", str(self.project.root / "нет")], text=True, capture_output=True, check=False)
        self.assertEqual(result.returncode, 2)

    def test_legacy_task_under_router_epic_can_be_reconciled(self) -> None:
        """Judgment call: --snapshot works for a router epic, so a legacy task left under it stays fixable."""

        root = self.project.root
        (root / "docs").mkdir()
        (root / "docs" / "decision.md").write_text("# Decision\n", encoding="utf-8")
        self.project.edit(self.project.epic, "кнопка выгрузки.\n", "кнопка выгрузки.\n2. [[_ops/plans/эпики/Экспорт/task - Старая|Старая]] — прежняя форма.\n")
        self.project.edit(self.project.epic, "задач: 1", "задач: 2")
        self.project.edit(self.project.epic, f'задачи: ["{TASK_LINK}"]', f'задачи: ["{TASK_LINK}","[[_ops/plans/эпики/Экспорт/task - Старая]]"]')
        epic = self.project.epic.relative_to(root).as_posix()

        def write_legacy(snapshot: str) -> None:
            text = LEGACY_TASK.format(epic="Экспорт", name="Старая", snapshot=snapshot, order=2)
            (self.project.epic_dir / "task - Старая.md").write_text(text, encoding="utf-8")

        digest, report = check_plans.snapshot_path(root, epic)
        self.assertTrue(report.ok, [issue.message for issue in report.issues])
        write_legacy(digest)
        self.assertValid()
        self.project.edit(self.project.epic, "открывает файл в таблице без правок.\n", "открывает файл в таблице без правок и потерь.\n")
        self.assertEqual(self.project.messages(), ["эпик-снимок is stale for an unfinished task"])
        digest, _ = check_plans.snapshot_path(root, epic)
        write_legacy(digest)
        self.assertValid()


def _normalise_h2(lines: list[str]) -> list[str]:
    return [re.sub(r"H2 sections must be exactly .* in order; got ", "H2 sections must be exactly <forms> in order; got ", line) for line in lines]


@unittest.skipUnless(PREVIOUS_CHECKER_PATH.is_file(), "the previous 1plan-map checker is not present")
class LegacyEquivalenceTests(unittest.TestCase):
    """Rule 2: legacy files get the previous checker's issues, in the same order.

    The one intended difference is the H2 message, which now names both forms.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.previous = _load("check_plans_previous", PREVIOUS_CHECKER_PATH)

    def outcomes(self, root: Path) -> tuple[list[str], list[str]]:
        old = self.previous.validate_root(root)
        new = check_plans.validate_root(root)
        return [issue.format(old.root) for issue in old.issues], [issue.format(new.root) for issue in new.issues]

    def mutations(self) -> list[tuple[str, Callable[[Path, Path, Path], None]]]:
        def replace(which: str, old: str, new: str, count: int = 1) -> Callable[[Path, Path, Path], None]:
            def apply(root: Path, epic: Path, task: Path) -> None:
                path = epic if which == "epic" else task
                text = path.read_text(encoding="utf-8")
                assert old in text, (which, old)
                path.write_text(text.replace(old, new, count), encoding="utf-8")

            return apply

        cases: list[tuple[str, Callable[[Path, Path, Path], None]]] = [("valid", lambda root, epic, task: None)]
        with tempfile.TemporaryDirectory() as folder:
            epic, task = write_legacy_pair(Path(folder))
            texts = {"epic": epic.read_text(encoding="utf-8"), "task": task.read_text(encoding="utf-8")}
        for which, text in texts.items():
            frontmatter = text.split("---\n", 2)[1]
            for line in frontmatter.splitlines(keepends=True):
                key = line.split(":", 1)[0]
                cases.append((f"{which} without {key}", replace(which, line, "")))
                cases.append((f"{which} {key} null", replace(which, line, f"{key}: null\n")))
                cases.append((f"{which} {key} list", replace(which, line, f"{key}: []\n")))
        cases += [
            ("task sections swapped", replace("task", "## Основания", "## Зачем")),
            ("task Канон title", replace("task", "## Основания", "## Канон")),
            ("task without Состояние", replace("task", "## Состояние\n\nСледующий ход.\n", "")),
            ("task Состояние renamed to a router title", replace("task", "## Состояние", "## Готово, когда")),
            ("task empty Цель", replace("task", "Результат задачи.\n", "")),
            ("epic sections swapped", replace("epic", "## Границы", "## Аппетит")),
            ("epic Канон title", replace("epic", "## Основания", "## Канон")),
            ("epic Порядок title", replace("epic", "## Аппетит", "## Порядок")),
            ("epic canon field", replace("epic", "основания: [", "канон: [")),
            ("epic missing grounds file", replace("epic", 'основания: ["docs/decision.md"]', 'основания: ["docs/none.md"]')),
            ("checked without evidence", replace("task", "- [ ] Первое", "- [x] Первое")),
            ("report removed", replace("task", "> [!note]- Отчёт\n> статус 2026-09-08: не начато\n> доказательство:\n\n- [ ] Второе", "- [ ] Второе")),
            ("two subtasks", replace("task", "- [ ] Третье достигнутое состояние\n> [!note]- Отчёт\n> статус 2026-09-08: не начато\n> доказательство:\n", "")),
            ("bad report date", replace("task", "статус 2026-09-08: не начато", "статус 2026-13-08: не начато")),
            ("closed task open boxes", replace("task", "статус: ◽ в очереди", "статус: ✅ готово")),
            ("closed task all boxes", lambda root, epic, task: task.write_text(task.read_text(encoding="utf-8").replace("статус: ◽ в очереди", "статус: ✅ готово").replace("- [ ]", "- [x]").replace("> доказательство:", "> доказательство: коммит abc"), encoding="utf-8")),
            ("active task, queued epic", replace("task", "статус: ◽ в очереди", "статус: 🔨 в работе")),
            ("closed epic", replace("epic", "статус: ◽ в очереди", "статус: ✅ готово")),
            ("stale snapshot", lambda root, epic, task: (root / "docs" / "decision.md").write_text("changed\n", encoding="utf-8")),
            ("derived counters", replace("task", "подзадач: 3", "подзадач: 4")),
            ("broken epic link", replace("task", "[[_ops/plans/эпики/Архив/epic - Архив]]", "[[нет]]")),
        ]
        return cases

    def test_mutated_legacy_pair_matches_previous_checker(self) -> None:
        failing = 0
        for name, mutate in self.mutations():
            with self.subTest(mutation=name), tempfile.TemporaryDirectory() as folder:
                root = Path(folder)
                epic, task = write_legacy_pair(root)
                mutate(root, epic, task)
                old, new = self.outcomes(root)
                self.assertEqual(_normalise_h2(new), _normalise_h2(old))
                failing += bool(old)
        self.assertGreater(failing, 80, "the mutations must actually break legacy files")

    def test_sync_writes_the_same_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            roots = [Path(first) / "p", Path(second) / "p"]
            for root in roots:
                _, task = write_legacy_pair(root)
                task.write_text(task.read_text(encoding="utf-8").replace("подзадач: 3", "подзадач: 0").replace("- [ ] Первое", "- [x] Первое").replace("> доказательство:", "> доказательство: коммит abc", 1), encoding="utf-8")
            old_report, old_changed = self.previous.sync_root(roots[0])
            new_report, new_changed = check_plans.sync_root(roots[1])
            self.assertEqual((new_changed, [issue.message for issue in new_report.issues]), (old_changed, [issue.message for issue in old_report.issues]))
            self.assertEqual(old_changed, 1)
            files = [sorted((path.relative_to(root), path.read_bytes()) for path in root.rglob("*") if path.is_file()) for root in roots]
            self.assertEqual(files[0], files[1])


if __name__ == "__main__":
    unittest.main()
