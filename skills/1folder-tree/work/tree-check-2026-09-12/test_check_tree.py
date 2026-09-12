import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

OWNER = Path(__file__).resolve().parents[3] / 'shared/1folder-tree/portable'
spec = importlib.util.spec_from_file_location('check_tree', OWNER / 'scripts/check_tree.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class CheckTree(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.root = self.base / 'База со пробелами'
        self.root.mkdir()
        (self.root / 'Товар').mkdir()
        (self.root / 'Товар/Цена.md').write_text('PRIVATE_SENTINEL')
        self.out = self.base / 'result'

    def call(self, *flags):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return m.main([str(self.root), '--output-dir', str(self.out), *flags])

    def fake_run(self, command, **kwargs):
        self.assertNotEqual(Path(kwargs['cwd']), self.out)
        self.assertEqual(command[command.index('-C') + 1], kwargs['cwd'])
        self.assertEqual(list(Path(kwargs['cwd']).iterdir()), [])
        self.assertNotIn('shell', kwargs)
        self.assertIn('model_reasoning_effort="low"', command)
        self.assertEqual(command[command.index('-m') + 1], 'gpt-5.6-sol')
        self.assertNotIn('PRIVATE_SENTINEL', kwargs['input'])
        self.assertIn(m.SKILL.read_text(), kwargs['input'])
        kwargs['stdout'].write(json.dumps({'type': 'item.completed', 'item': {'type': 'agent_message'}}) + '\n')
        kwargs['stdout'].write(json.dumps({'type': 'turn.completed', 'usage': {'input_tokens': 1}}) + '\n')
        (self.out / 'response.md').write_text('Проверка завершена.')
        return subprocess.CompletedProcess(command, 0)

    def test_snapshot_reads_no_contents_and_does_not_follow_links(self):
        outside = self.base / 'outside'
        outside.mkdir()
        (outside / 'must-not-appear').touch()
        (self.root / 'link').symlink_to(outside, target_is_directory=True)
        (self.root / 'Строка\n$(touch BAD).md').touch()
        (self.root / '.git').mkdir()
        (self.root / '.git/hidden').touch()
        with patch.object(Path, 'read_text', side_effect=AssertionError('content read')):
            data = m.snapshot(self.root, ['.git'], 100)
        paths = [e['path'] for e in data['entries']]
        self.assertIn('link', paths)
        self.assertFalse(any('must-not-appear' in p for p in paths))
        self.assertEqual(data['excluded'], ['.git'])
        self.assertEqual(json.loads(json.dumps(data)), data)

    def test_dry_run_no_model_and_no_project_content(self):
        with patch.object(m.subprocess, 'run', side_effect=AssertionError('model called')):
            self.assertEqual(self.call('--dry-run'), 0)
        prompt = (self.out / 'prompt.txt').read_text()
        self.assertNotIn('PRIVATE_SENTINEL', prompt)
        self.assertIn(m.SKILL.read_text(), prompt)

    def test_output_inside_root_and_existing_output_rejected(self):
        self.out = self.root / 'report'
        self.assertEqual(self.call('--dry-run'), 1)
        self.assertFalse(self.out.exists())
        self.out = self.base / 'already-there'
        self.out.mkdir()
        (self.out / 'keep').write_text('keep')
        self.assertEqual(self.call('--dry-run'), 1)
        self.assertEqual((self.out / 'keep').read_text(), 'keep')

    def test_limit_and_read_failure_are_not_partial_success(self):
        self.assertEqual(self.call('--dry-run', '--max-entries', '1'), 1)
        self.assertFalse(self.out.exists())
        with patch.object(m.os, 'scandir', side_effect=PermissionError('denied')):
            self.assertEqual(self.call('--dry-run'), 1)
        with self.assertRaises(ValueError):
            m.snapshot(self.root, ['*'], 0)

    def test_completed_run_preserves_input(self):
        with patch.object(m.shutil, 'which', return_value='/test/codex'), patch.object(m.subprocess, 'run', side_effect=self.fake_run):
            self.assertEqual(self.call(), 0)
        self.assertEqual((self.root / 'Товар/Цена.md').read_text(), 'PRIVATE_SENTINEL')
        self.assertEqual((self.out / 'report.md').read_text().strip(), 'Проверка завершена.')
        self.assertEqual(json.loads((self.out / 'run.json').read_text())['status'], 'completed')

    def test_tool_actions_and_missing_completion_rejected(self):
        p = self.base / 'events'
        for event in [{'type': 'item.started', 'item': {'type': 'command_execution'}}, {'type': 'turn.failed'}, {'type': 'turn.started'}]:
            p.write_text(json.dumps(event) + '\n')
            with self.assertRaises(ValueError):
                m.verified_usage(p)

    def test_timeout_is_failure(self):
        with patch.object(m.shutil, 'which', return_value='/test/codex'), patch.object(m.subprocess, 'run', side_effect=subprocess.TimeoutExpired('codex', 1)):
            self.assertEqual(self.call('--timeout', '1'), 1)
        self.assertEqual(json.loads((self.out / 'run.json').read_text())['status'], 'failed')
        self.assertFalse((self.out / 'report.md').exists())

if __name__ == '__main__':
    unittest.main()
