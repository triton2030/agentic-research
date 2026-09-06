"""CLI contract tests; run with python3 -m unittest discover -s this-directory."""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "portable/scripts/doc_map.py"


class DocumentMapTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def document(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def run_map(self, root=None):
        return subprocess.run(
            [sys.executable, str(SCRIPT), str(root or self.root)],
            text=True, capture_output=True, check=False,
        )

    def test_nested_map_reads_yaml_variants_and_preserves_files(self):
        self.document("Роль/Цель.md", '\ufeff---\ndescription: >-\n  Доступ к\n  заявке.\naliases:\n  - "вечная ссылка"\n  - accessToken\n---\nBODY MUST NOT APPEAR\n')
        self.document(".hidden.MD", '---\ndescription: "Имя: значение | другое"\naliases: ["user_id", "ссылка"]\n---\n')
        self.document("image.png", "Not Markdown")
        (self.root / "empty").mkdir()
        before = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        result = self.run_map()
        self.assertEqual(result.returncode, 0, result.stderr)
        for expected in ("Роль/Цель.md", "Доступ к заявке.", "вечная ссылка; accessToken", "empty/", ".hidden.MD", "image.png", "non-Markdown", "Имя: значение \\| другое"):
            self.assertIn(expected, result.stdout)
        self.assertNotIn("BODY MUST NOT APPEAR", result.stdout)
        self.assertEqual(before, {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*") if p.is_file()})

    def test_missing_invalid_and_malformed_metadata_remain_visible(self):
        self.document("missing.md", "# No header\n")
        self.document("invalid.md", "---\ndescription: 42\naliases: word\n---\n")
        self.document("broken.md", "---\naliases: [oops\n---\n")
        self.document("unclosed.md", "---\ndescription: text\n")
        self.document("good.md", "---\ndescription: Good\naliases: []\n---\n")
        result = self.run_map()
        self.assertEqual(result.returncode, 1)
        for name in ("missing.md", "invalid.md", "broken.md", "unclosed.md", "good.md"):
            self.assertIn(name, result.stdout)
        self.assertIn("Good | \\[\\]", result.stdout)
        self.assertIn("broken.md:", result.stderr)
        self.assertIn("unclosed frontmatter", result.stderr)

    def test_empty_aliases_valid_but_missing_aliases_not_valid(self):
        path = self.document("doc.md", "---\ndescription: Good\naliases: []\n---\n")
        self.assertEqual(self.run_map().returncode, 0)
        path.write_text("---\ndescription: Good\n---\n", encoding="utf-8")
        self.assertEqual(self.run_map().returncode, 1)

    def test_symlink_cycle_is_listed_without_traversal(self):
        (self.root / "loop").symlink_to(self.root, target_is_directory=True)
        result = self.run_map()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("loop", result.stdout)
        self.assertIn("symlink; not followed", result.stdout)
        self.assertIn("Entries: 1", result.stdout)

    def test_empty_root_and_invalid_root(self):
        self.assertIn("Entries: 0", self.run_map().stdout)
        result = self.run_map(self.root / "missing")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")

    def test_yaml_scalar_list_and_code_like_tags_are_not_metadata(self):
        for index, header in enumerate(("hello", "- entry", "!!python/object/apply:builtins.print [EXECUTED]")):
            self.document(f"bad-{index}.md", f"---\n{header}\n---\n")
        result = self.run_map()
        self.assertEqual(result.returncode, 1)
        self.assertNotIn("EXECUTED", result.stdout)
        self.assertEqual(result.stdout.count("metadata unreadable"), 3)


if __name__ == "__main__":
    unittest.main()
