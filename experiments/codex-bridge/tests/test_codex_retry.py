from __future__ import annotations

import asyncio
import json
import sys
import tempfile
import unittest
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

import codex_retry  # noqa: E402


class ArchivedRpcError(Exception):
    """Форма ошибки движка: код -32600 + текст. Повторяет JsonRpcError SDK."""

    def __init__(self, code: int, message: str) -> None:
        super().__init__(f"JSON-RPC error {code}: {message}")
        self.code = code
        self.message = message


class IsArchivedErrorTests(unittest.TestCase):
    """Предикат держится на двух опорах: текст движка не контракт, а код -32600
    может уехать в другой класс. Достаточно любой одной."""

    def test_text_alone_is_enough(self) -> None:
        self.assertTrue(codex_retry.is_archived_error(Exception("session x is archived")))

    def test_code_alone_is_enough(self) -> None:
        self.assertTrue(codex_retry.is_archived_error(ArchivedRpcError(-32600, "bad state")))

    def test_unrelated_failure_is_not_archived(self) -> None:
        self.assertFalse(codex_retry.is_archived_error(ArchivedRpcError(-32603, "internal")))
        self.assertFalse(codex_retry.is_archived_error(Exception("boom")))


class _FakeCodex:
    """Движок, в котором тред `t-1` архивирован, пока его не поднимут."""

    def __init__(self, archived: set[str], *, unarchive_fails: bool = False) -> None:
        self.archived = archived
        self.unarchive_fails = unarchive_fails
        self.unarchive_calls: list[str] = []
        self.resume_calls: list[str] = []

    def resume(self, thread_id: str) -> str:
        self.resume_calls.append(thread_id)
        if thread_id in self.archived:
            raise ArchivedRpcError(-32600, f"session {thread_id} is archived")
        return f"thread:{thread_id}"

    def thread_unarchive(self, thread_id: str) -> None:
        self.unarchive_calls.append(thread_id)
        if self.unarchive_fails:
            raise RuntimeError("движок отказал в подъёме")
        self.archived.discard(thread_id)


def _events(run_dir: Path) -> list[dict]:
    path = run_dir / "events.jsonl"
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


class ResumeThreadTests(unittest.TestCase):
    """Ремонтный круг штатно приходит к архивному треду: волна, которая его
    прогрела, сама его и архивировала на закрытии. Без подъёма он умирал до
    начала работы (замеры волн 9 и 10, 2026-09-01: потеряны 3 задачи из 4)."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.run_dir = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_archived_thread_is_raised_and_resume_repeated(self) -> None:
        codex = _FakeCodex({"t-1"})
        thread, unarchived = codex_retry.resume_thread(
            codex, "t-1", lambda: codex.resume("t-1"), run_dir=self.run_dir,
        )
        self.assertEqual(thread, "thread:t-1")
        self.assertTrue(unarchived)
        self.assertEqual(codex.unarchive_calls, ["t-1"])
        self.assertEqual(codex.resume_calls, ["t-1", "t-1"])
        logged = [e for e in _events(self.run_dir) if e["event"] == "thread_unarchived"]
        self.assertEqual(len(logged), 1)
        self.assertEqual(logged[0]["thread_id"], "t-1")

    def test_live_thread_costs_nothing(self) -> None:
        codex = _FakeCodex(set())
        thread, unarchived = codex_retry.resume_thread(
            codex, "t-1", lambda: codex.resume("t-1"), run_dir=self.run_dir,
        )
        self.assertEqual(thread, "thread:t-1")
        self.assertFalse(unarchived)
        self.assertEqual(codex.unarchive_calls, [])
        self.assertEqual(codex.resume_calls, ["t-1"])
        self.assertEqual(_events(self.run_dir), [])

    def test_unrelated_failure_is_not_swallowed(self) -> None:
        def op():
            raise RuntimeError("движок недоступен")

        codex = _FakeCodex(set())
        with self.assertRaises(RuntimeError):
            codex_retry.resume_thread(codex, "t-1", op, run_dir=self.run_dir)
        self.assertEqual(codex.unarchive_calls, [])

    def test_failed_unarchive_surfaces_the_resume_error(self) -> None:
        """Наружу идёт ошибка resume — воркер умер на ней; провал подъёма
        остаётся в журнале, а не подменяет причину."""
        codex = _FakeCodex({"t-1"}, unarchive_fails=True)
        with self.assertRaises(ArchivedRpcError):
            codex_retry.resume_thread(
                codex, "t-1", lambda: codex.resume("t-1"), run_dir=self.run_dir,
            )
        failed = [e for e in _events(self.run_dir) if e["event"] == "thread_unarchive_failed"]
        self.assertEqual(len(failed), 1)
        self.assertIn("отказал", failed[0]["error"])

    def test_async_mirror_raises_the_thread_too(self) -> None:
        codex = _FakeCodex({"t-1"})

        async def op():
            return codex.resume("t-1")

        class _AsyncCodex:
            def __init__(self, inner: _FakeCodex) -> None:
                self.inner = inner

            async def thread_unarchive(self, thread_id: str) -> None:
                self.inner.thread_unarchive(thread_id)

        thread, unarchived = asyncio.run(
            codex_retry.resume_thread_async(
                _AsyncCodex(codex), "t-1", op, run_dir=self.run_dir,
                fields={"worker": "w1"},
            )
        )
        self.assertEqual(thread, "thread:t-1")
        self.assertTrue(unarchived)
        logged = [e for e in _events(self.run_dir) if e["event"] == "thread_unarchived"]
        self.assertEqual(logged[0]["worker"], "w1")


if __name__ == "__main__":
    unittest.main()
