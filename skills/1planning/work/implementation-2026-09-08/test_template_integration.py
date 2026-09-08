"""Exercise the shipped templates and Bases together in an isolated project."""

import importlib.util
from pathlib import Path
import re
import shutil
import sys
import tempfile
import unittest


WORK = Path(__file__).resolve().parent
PACKAGES = WORK / "packages"
SCRIPT = PACKAGES / "1plan-map/scripts/check_plans.py"
spec = importlib.util.spec_from_file_location("template_checker", SCRIPT)
checker = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = checker
spec.loader.exec_module(checker)


def fill_template(path, replacements):
    text = path.read_text()
    for old, new in replacements.items():
        text = text.replace(old, new)
    return re.sub(r"\{\{.*?\}\}", "Заполненное содержание", text, flags=re.S)


class TemplateIntegration(unittest.TestCase):
    def test_shipped_assets_form_a_valid_project(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            plans = root / "_ops/plans"
            epic_dir = plans / "эпики/Экспорт"
            epic_dir.mkdir(parents=True)
            (root / "_ops/GOAL.md").write_text("# Цель\nСовместимая выгрузка.\n")
            for base in (PACKAGES / "1plan-map/assets/map").glob("*.base"):
                shutil.copy2(base, plans / base.name)
            epic = epic_dir / "epic - Экспорт.md"
            epic.write_text(fill_template(
                PACKAGES / "1plan-map/assets/epic-template.md",
                {'{{YYYY-MM-DD}}': '2026-09-08',
                 'допуск: ""': 'допуск: "решение владельца 2026-09-08"'},
            ))
            snapshot, report = checker.snapshot_path(root, str(epic.relative_to(root)))
            self.assertTrue(report.ok, [issue.message for issue in report.issues])
            self.assertRegex(snapshot, r"^[a-f0-9]{64}$")
            task = epic_dir / "task - CSV.md"
            task.write_text(fill_template(
                PACKAGES / "1plan-task/assets/task-template.md",
                {'{{YYYY-MM-DD}}': '2026-09-08', '{{Эпик}}': 'Экспорт',
                 '{{Снимок после сверки}}': snapshot},
            ))
            questions = plans / "вопросы"
            questions.mkdir()
            question = questions / "Импорт.md"
            question.write_text(fill_template(
                PACKAGES / "1plan-map/assets/question-template.md",
                {'{{YYYY-MM-DD}}': '2026-09-08',
                 '{{Путь эпика или задачи без .md}}': str(epic.relative_to(root).with_suffix(''))},
            ))
            report, changed = checker.sync_root(root)
            self.assertTrue(report.ok, [issue.message for issue in report.issues])
            self.assertEqual(changed, 1)
            self.assertTrue(checker.validate_root(root).ok)
            after, report = checker.snapshot_path(root, str(epic.relative_to(root)))
            self.assertTrue(report.ok)
            self.assertEqual(snapshot, after)
            report, changed = checker.sync_root(root)
            self.assertTrue(report.ok)
            self.assertEqual(changed, 0)


if __name__ == "__main__":
    unittest.main()
