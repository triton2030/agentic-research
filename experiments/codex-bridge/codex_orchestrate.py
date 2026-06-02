#!/usr/bin/env python3
"""codex-bridge orchestrator — флот параллельных Codex-воркеров.

Claude — оркестратор: он генерирует список file-disjoint задач, этот скрипт гонит
их параллельно через AsyncCodex с лимитом concurrency и собирает сводку.

Каждый воркер: sandbox=workspace-write, cwd=корень проекта — он РЕДАКТИРУЕТ файлы.
Биллинг идёт через ChatGPT-аккаунт (env вычищен от API-ключей).

КОНТРАКТ (обязателен, иначе гонки и потеря данных):
  • Задачи должны быть FILE-DISJOINT — два воркера не правят один файл.
  • Git — сеть безопасности: коммить/стейдж до запуска, чтобы можно было откатить.
  • НЕ верь самоотчётам воркеров — оркестратор обязан перепроверить результат
    (git diff, тесты, или отдельный проход codex_review.py по изменениям).

Вход (--tasks FILE или stdin) — JSON-массив:
  [
    {"id": "t1", "prompt": "что сделать", "files": ["path/a.md"], "cwd": "опц"},
    ...
  ]
  prompt — обязателен; id, files, cwd — опциональны. files добавляется в промпт
  как жёсткое ограничение «правь только эти файлы».

Выход (stdout) — JSON-массив результатов по задачам; прогресс — в stderr.
Код возврата 0 только если ВСЕ задачи завершились успешно.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from pathlib import Path

from cbcommon import scrub_billing_env


def _files_constraint(files: list[str]) -> str:
    joined = ", ".join(files)
    return (
        f"Тебе разрешено создавать и редактировать ТОЛЬКО эти файлы: {joined}. "
        f"Не трогай никакие другие файлы. Если задача требует иного — опиши это в ответе, но не делай.\n\n"
    )


async def _run_one(codex, sem, task: dict, defaults: dict) -> dict:
    from openai_codex import ApprovalMode, Sandbox  # импорт после scrub_billing_env

    tid = str(task.get("id", "?"))
    cwd = task.get("cwd") or defaults["cwd"]
    prompt = task["prompt"]
    if task.get("files"):
        prompt = _files_constraint(task["files"]) + prompt

    async with sem:
        t0 = time.monotonic()
        try:
            thread = await codex.thread_start(
                cwd=cwd,
                sandbox=Sandbox.workspace_write,
                approval_mode=ApprovalMode.auto_review,
                model=defaults["model"],
            )
            result = await thread.run(prompt)
            dt = int((time.monotonic() - t0) * 1000)
            status = str(getattr(result, "status", ""))
            ok = status.endswith("completed") and not result.error
            print(f"[orch] {'✓' if ok else '✗'} {tid} ({dt}мс)"
                  + ("" if ok else f" — {result.error}"), file=sys.stderr)
            return {
                "id": tid,
                "ok": ok,
                "status": status,
                "error": str(result.error) if result.error else None,
                "response": result.final_response,
                "duration_ms": dt,
                "usage": str(getattr(result, "usage", None)),
            }
        except Exception as exc:  # noqa: BLE001 — одна упавшая задача не валит флот
            dt = int((time.monotonic() - t0) * 1000)
            print(f"[orch] ✗ {tid} — исключение: {exc}", file=sys.stderr)
            return {"id": tid, "ok": False, "status": "exception", "error": str(exc),
                    "response": None, "duration_ms": dt, "usage": None}


async def _run_fleet(tasks: list[dict], defaults: dict, concurrency: int) -> list[dict]:
    from openai_codex import AsyncCodex, CodexConfig

    sem = asyncio.Semaphore(concurrency)
    async with AsyncCodex(CodexConfig(cwd=defaults["cwd"])) as codex:
        return await asyncio.gather(*(_run_one(codex, sem, t, defaults) for t in tasks))


def main() -> int:
    parser = argparse.ArgumentParser(description="Флот параллельных Codex-воркеров под оркестрацией Claude.")
    parser.add_argument("--tasks", help="JSON-файл со списком задач (иначе читается из stdin).")
    parser.add_argument("--project", default=None, help="Корень проекта = cwd воркеров (по умолчанию текущая папка).")
    parser.add_argument("--concurrency", type=int, default=6, help="Сколько воркеров одновременно (волны). По умолчанию 6.")
    parser.add_argument("--model", help="Модель Codex (по умолчанию из ~/.codex/config.toml).")
    parser.add_argument("--dry-run", action="store_true", help="Показать план задач, НЕ запуская Codex (не тратит кредиты).")
    args = parser.parse_args()

    import os
    project = str(Path(args.project or os.getcwd()).expanduser().resolve())

    raw = Path(args.tasks).read_text() if args.tasks else sys.stdin.read()
    try:
        tasks = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"[orch] невалидный JSON задач: {exc}", file=sys.stderr)
        return 2
    if not isinstance(tasks, list) or not tasks:
        print("[orch] ожидается непустой JSON-массив задач.", file=sys.stderr)
        return 2
    bad = [i for i, t in enumerate(tasks) if not isinstance(t, dict) or not t.get("prompt")]
    if bad:
        print(f"[orch] задачи без обязательного поля prompt: индексы {bad}", file=sys.stderr)
        return 2

    defaults = {"cwd": project, "model": args.model}

    if args.dry_run:
        print(f"[orch dry-run] {len(tasks)} задач, concurrency={args.concurrency}, project={project}", file=sys.stderr)
        for t in tasks:
            print(f"  - {t.get('id', '?')}: {t['prompt'][:80].strip()}…  files={t.get('files')}", file=sys.stderr)
        return 0

    removed = scrub_billing_env()
    print(f"[orch] старт: {len(tasks)} задач, лимит {args.concurrency} одновременно, project={project}"
          + (f" | вырезано из env: {', '.join(removed)}" if removed else " | env чист"), file=sys.stderr)

    results = asyncio.run(_run_fleet(tasks, defaults, args.concurrency))

    ok = sum(1 for r in results if r.get("ok"))
    print(f"[orch] готово: {ok}/{len(results)} успешно", file=sys.stderr)
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0 if ok == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
