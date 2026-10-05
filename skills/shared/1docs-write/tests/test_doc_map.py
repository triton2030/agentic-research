"""CLI contract tests; run with python3 -m unittest discover -s this-directory."""

from contextlib import redirect_stderr, redirect_stdout
import io
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "portable/scripts/doc_map.py"


class DocumentMapTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()

    def document(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def run_map(self, root=None, *options):
        return subprocess.run(
            [sys.executable, str(SCRIPT), str(root or self.root), *options],
            text=True, capture_output=True, check=False,
        )

    def run_map_with_unreadable_directory(self, blocked, *options):
        """Exercise the CLI with deterministic read failure, even as root."""
        original_iterdir = Path.iterdir
        visited = []

        def guarded_iterdir(folder):
            visited.append(folder)
            if folder == blocked:
                raise PermissionError(f"Cannot read {folder}")
            return original_iterdir(folder)

        stdout, stderr = io.StringIO(), io.StringIO()
        argv = [str(SCRIPT), str(self.root), *options]
        with patch.object(Path, "iterdir", guarded_iterdir), patch.object(sys, "argv", argv):
            with redirect_stdout(stdout), redirect_stderr(stderr):
                with self.assertRaises(SystemExit) as exited:
                    runpy.run_path(str(SCRIPT), run_name="__main__")
        return subprocess.CompletedProcess(
            argv, exited.exception.code, stdout.getvalue(), stderr.getvalue(),
        ), visited

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

    def test_instructions_do_not_require_valid_cards(self):
        self.document("AGENTS.md", "# Instructions\n")
        self.document("nested/CLAUDE.md", "---\naliases: [broken\n---\n")
        result = self.run_map()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertIn("AGENTS.md | \\[instruction\\] | —", result.stdout)
        self.assertIn("nested/CLAUDE.md | \\[instruction\\] | —", result.stdout)
        self.assertIn("Issues: 0", result.stdout)

    def test_instructions_show_valid_description_without_validating_aliases(self):
        self.document("AGENTS.md", '---\ndescription: "Agent | guide"\n---\n')
        self.document("nested/CLAUDE.md", "---\ndescription: Claude guide\naliases: 42\n---\n")
        result = self.run_map()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertIn("AGENTS.md | Agent \\| guide | —", result.stdout)
        self.assertIn("nested/CLAUDE.md | Claude guide | —", result.stdout)
        self.assertIn("Issues: 0", result.stdout)

    def test_invalid_instruction_cards_fall_back_without_issues(self):
        for header in ("description: 42", 'description: " "', "- item", "description: [broken", "description: text"):
            with self.subTest(header=header):
                closing = "" if header == "description: text" else "---\n"
                self.document("CLAUDE.md", f"---\n{header}\n{closing}")
                result = self.run_map()
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stderr, "")
                self.assertIn("CLAUDE.md | \\[instruction\\] | —", result.stdout)

    def test_excludes_repeat_and_prune_directory_names_before_traversal(self):
        self.document(".obsidian/bad.md", "# No card\n")
        self.document("nested/.obsidian/bad.md", "# No card\n")
        self.document("ignored.tmp", "Non-Markdown")
        self.document(".hidden.md", "---\ndescription: Visible\naliases: []\n---\n")
        # Cycles are listed without traversal even without an exclusion.
        (self.root / ".obsidian/loop").symlink_to(self.root, target_is_directory=True)
        result = self.run_map(None, "--exclude", ".obsidian", "--exclude", "*.tmp")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn(".obsidian", result.stdout)
        self.assertNotIn("ignored.tmp", result.stdout)
        self.assertIn(".hidden.md", result.stdout)
        self.assertIn("Entries: 2", result.stdout)

    def test_excluded_unreadable_directory_is_never_opened(self):
        blocked = self.root / ".obsidian"
        self.document(".obsidian/bad.md", "# No card\n")
        for options in ((), ("--folder-summary",)):
            with self.subTest(options=options):
                result, visited = self.run_map_with_unreadable_directory(
                    blocked, "--exclude", ".obsidian", *options,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stderr, "")
                self.assertNotIn(blocked, visited)
                self.assertNotIn(".obsidian", result.stdout)
                self.assertIn("Entries: 0", result.stdout)

    def test_unreadable_directory_remains_visible_with_summary(self):
        blocked = self.root / "blocked"
        blocked.mkdir()
        for options in ((), ("--folder-summary",), ("--folder-summary", "--chars")):
            with self.subTest(options=options):
                result, visited = self.run_map_with_unreadable_directory(blocked, *options)
                self.assertEqual(result.returncode, 1)
                self.assertIn(blocked, visited)
                self.assertIn("| blocked/ | — | — |", result.stdout)
                self.assertIn("Incomplete traversal:", result.stderr)
                self.assertIn("Entries: 1. Issues: 1.", result.stdout)
                if "--folder-summary" in options:
                    self.assertIn("summary unreadable", result.stdout)

    def test_unreadable_root_remains_visible_with_summary(self):
        result, _ = self.run_map_with_unreadable_directory(self.root, "--folder-summary")
        self.assertEqual(result.returncode, 1)
        self.assertIn("| ./ | — | — | \\[summary unreadable\\] |", result.stdout)
        self.assertIn("Incomplete traversal:", result.stderr)
        self.assertIn("Entries: 0. Issues: 1.", result.stdout)

    def test_excludes_match_root_relative_paths(self):
        self.document("a/cache/bad.md", "# No card\n")
        self.document("b/cache/good.md", "---\ndescription: Kept\naliases: []\n---\n")
        self.document("a/omit.markdown", "# No card\n")
        result = self.run_map(None, "--exclude", "a/cache", "--exclude", "a/*.markdown")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("a/cache", result.stdout)
        self.assertNotIn("omit.markdown", result.stdout)
        self.assertIn("b/cache/good.md", result.stdout)

    def test_chars_are_code_points_without_bom_with_normalized_newlines(self):
        text = "---\ndescription: Текст\naliases: []\n---\nЖ🙂е\u0301\nend\n"
        path = self.document("doc.md", "")
        path.write_bytes(("\ufeff" + text.replace("\n", "\r\n", 2).replace("end\n", "end\r")).encode("utf-8"))
        self.document("CLAUDE.md", "🙂\n")
        self.document("asset.bin", "ignored")
        (self.root / "link.md").symlink_to(path)
        before = path.read_bytes()
        result = self.run_map(None, "--chars")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("| Chars |", result.stdout)
        self.assertIn(f"doc.md | Текст | \\[\\] | {len(text)} |", result.stdout)
        self.assertNotEqual(len(text), len(before))
        self.assertIn("CLAUDE.md | \\[instruction\\] | — | 2 |", result.stdout)
        self.assertIn("asset.bin | \\[non-Markdown\\] | — | — |", result.stdout)
        self.assertIn("link.md | \\[symlink; not followed\\] | — | — |", result.stdout)
        self.assertNotIn("Folder summary", result.stdout)
        self.assertEqual(before, path.read_bytes())

    def test_chars_are_available_when_yaml_is_malformed(self):
        text = "---\naliases: [broken\n---\n🙂\n"
        self.document("broken.md", text)
        result = self.run_map(None, "--chars")
        self.assertEqual(result.returncode, 1)
        self.assertIn(f"broken.md | \\[metadata unreadable\\] | — | {len(text)} |", result.stdout)

    def test_invalid_utf8_size_is_a_read_error_and_remains_visible(self):
        path = self.document("AGENTS.md", "")
        path.write_bytes(b"\xff")
        self.assertEqual(self.run_map().returncode, 0)
        result = self.run_map(None, "--chars")
        self.assertEqual(result.returncode, 1)
        self.assertIn("AGENTS.md | \\[instruction\\] | — | \\[text unreadable\\]", result.stdout)
        self.assertIn("AGENTS.md:", result.stderr)

    def test_folder_summary_counts_immediate_children_and_marks_mixed(self):
        card = "---\ndescription: Good\naliases: []\n---\n"
        self.document("README.md", card)
        self.document("mixed/file.md", card)
        self.document("mixed/sub/file.md", card)
        self.document("instructions/AGENTS.md", "# Instructions\n")
        self.document("instructions/CLAUDE.md", "# Instructions\n")
        (self.root / "instructions/sub").mkdir()
        self.document("only-files/doc.md", card)
        self.document("only-files/image.png", "asset")
        self.document("only-files/.obsidian/ignore.md", "no card")
        (self.root / "only-files/link").symlink_to(self.root, target_is_directory=True)
        result = self.run_map(None, "--folder-summary", "--exclude", ".obsidian")
        self.assertEqual(result.returncode, 0, result.stderr)
        for expected in (
            "./ | — | — | files: 1; dirs: 3; mixed |",
            "mixed/ | — | — | files: 1; dirs: 1; mixed |",
            "mixed/sub/ | — | — | files: 1; dirs: 0 |",
            "instructions/ | — | — | files: 0; dirs: 1 |",
            "instructions/sub/ | — | — | files: 0; dirs: 0 |",
            "only-files/ | — | — | files: 1; dirs: 0 |",
        ):
            self.assertIn(expected, result.stdout)
        self.assertEqual(result.stdout.count("; mixed"), 2)
        self.assertNotIn("| Chars |", result.stdout)
        self.assertIn("Issues: 0", result.stdout)

    def test_file_symlinks_do_not_count_in_folder_summary(self):
        target = self.document("target/doc.md", "---\ndescription: Good\naliases: []\n---\n")
        (self.root / "link.md").symlink_to(target)
        result = self.run_map(None, "--folder-summary")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("./ | — | — | files: 0; dirs: 1 |", result.stdout)
        self.assertIn("link.md | \\[symlink; not followed\\] | — | — |", result.stdout)
        self.assertNotIn("; mixed", result.stdout)

    def test_non_markdown_files_do_not_cause_mixed_summary(self):
        self.document(".DS_Store", "system data")
        self.document("image.png", "asset")
        self.document("AGENTS.md", "# Instructions\n")
        self.document("sub/doc.MARKDOWN", "---\ndescription: Good\naliases: []\n---\n")
        result = self.run_map(None, "--folder-summary")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("./ | — | — | files: 0; dirs: 1 |", result.stdout)
        self.assertIn("sub/ | — | — | files: 1; dirs: 0 |", result.stdout)
        self.assertIn(".DS\\_Store", result.stdout)
        self.assertNotIn("; mixed", result.stdout)

    def test_summary_and_chars_are_optional_and_composable_for_empty_root(self):
        default = self.run_map()
        self.assertNotIn("Chars", default.stdout)
        self.assertNotIn("Folder summary", default.stdout)
        self.assertNotIn("| ./ |", default.stdout)
        result = self.run_map(None, "--chars", "--folder-summary")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("| Chars | Folder summary |", result.stdout)
        self.assertIn("| ./ | — | — | — | files: 0; dirs: 0 |", result.stdout)
        self.assertIn("Entries: 0", result.stdout)

    def test_help_defines_size_and_exclusion_semantics(self):
        result = self.run_map(None, "--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        help_text = " ".join(result.stdout.split())
        for expected in ("--exclude GLOB", "--chars", "--folder-summary", "Unicode code points", "BOM", "CRLF and CR", "pruned before traversal", "fnmatch", "* crosses /", "[abc] is a character class", "trailing / in the glob never matches", "regular .md/.markdown files"):
            self.assertIn(expected, help_text)


if __name__ == "__main__":
    unittest.main()
