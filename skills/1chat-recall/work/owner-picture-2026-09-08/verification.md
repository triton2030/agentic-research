# Проверка — 2026-09-08, v3

## Тесты пакета на черновике

- `draft/claude`: `python3 -m unittest discover -s tests -p 'test_chat_*.py' -q` — 122 OK.
- `draft/codex`: тот же прогон — 125 OK.
- Изменены два теста топологии в обоих runtime (см. intent.md «tests»).

## Корпус и указатель Codex

`chat_digest.py --check --strict` на корпусе с посторонним файлом
`psychologist-thread.md` и `.txt` — «OK: 6 записей без diagnostics» (оба
варианта игнорируются проверкой).

## Первичный источник по Codex

`codex exec resume <SESSION_ID>` — developers.openai.com (guides/text, «Resume a
non-interactive session»); `learn.chatgpt.com/docs/non-interactive-mode`.
Не проверено: поведение занятого треда, событие `thread.started` в `--json`.

## Живой прогон психолога на реальном корпусе

Дописывается: `Agent` с ролью `draft/claude/agents/psychologist.md`,
`TARGET_PROJECT_ROOT` = этот репо (319 файлов), вопрос 1 — граница вопроса
владельцу по одному выводу; вопрос 2 — `SendMessage` тому же агенту.
