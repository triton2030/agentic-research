# codex-bridge — правда под-проекта

Под-проект `experiments/`. Правь субтри от этого файла и `README.md`, не от
корневого AGENTS.

## Что это

Вызов Codex из Claude Code: ревьюер (read-only) и флот воркеров (workspace-write)
под оркестрацией Claude. Backend здесь; декларативный скилл — `~/.claude/skills/1codex/`.

## Инварианты (не ломать)

- **Биллинг через аккаунт.** `cbcommon.scrub_billing_env()` вызывается ДО запуска
  любого codex-процесса. Не убирай и не обходи — это защита от ухода на платный
  API. Любой новый вход (скрипт/режим) обязан звать его первым.
- **Ревьюер пишать не должен.** `codex_review.py` — всегда `Sandbox.read_only` +
  `ApprovalMode.deny_all`.
- **Воркер пишет под контрактом.** `codex_orchestrate.py` — `workspace_write` +
  `auto_review`; file-disjoint задачи, git как откат, перепроверка результатов.
  Контракт описан в `README.md`, продублирован в скилле и в промпте воркера.

## Карта файлов

- `cbcommon.py` — общая биллинг-гигиена (одна правда).
- `codex_review.py` — ревьюер/консультант, поиск и рендер транскрипта Claude.
- `codex_orchestrate.py` — асинхронный пул воркеров (`AsyncCodex` + semaphore).
- `requirements.txt` — `openai-codex`. venv в `.venv/` (git-ignored).

## Проверка

`--dry-run` есть у обоих скриптов — гоняет рендер/план без трат. Реальные
прогоны тратят кредиты аккаунта; тестируй на временных подпапках (`_ftest/`,
`_wtest/` — git-ignored) и чисти за собой.
