---
name: 1chat-recall
description: Восстанавливает точные сообщения и ответы пользователя из текущей Claude Code-сессии. Используй перед долгоживущим документом или решением, после compaction, при просьбе вспомнить сказанное ранее либо когда формулировки, числа и ограничения пользователя нельзя надёжно пересказывать по памяти.
allowed-tools: Bash(${CLAUDE_SKILL_DIR}/scripts/chat_recall.py *)
---

# Claude Chat Recall

Восстанавливай пользовательский ввод из JSONL-транскрипта именно текущей Claude Code-сессии. Не используй model memory как доказательство слов пользователя.

## Контракт

- Источник только один: transcript, однозначно найденный по `${CLAUDE_SESSION_ID}` внутри `${CLAUDE_CONFIG_DIR:-~/.claude}/projects`.
- Возвращай только прямые human messages и проверенные ответы на `AskUserQuestion`.
- Сохраняй точные text blocks из сообщений со screenshot/image; непрочитанное image content отражай как record-level omission и непустой `warnings`.
- Исключай skill expansion, tool results, task notifications, assistant text и записи других сессий.
- Следуй ancestry активной ветки от последнего прямого сообщения пользователя; отброшенные rewind-ветки не смешивай с текущей.
- По умолчанию исключай текущий turn, потому что он уже виден в контексте вызова.
- При неоднозначном transcript, повреждённой ancestry или неизвестной схеме останавливайся с ошибкой. Не подменяй evidence догадкой и не ищи соседнюю сессию.
- Скрипт read-only: он не меняет transcript, не обращается к сети и не сохраняет summary.

## Быстрый маршрут

Сначала запроси последние пять доступных записей:

```bash
"${CLAUDE_SKILL_DIR}/scripts/chat_recall.py" --session-id "${CLAUDE_SESSION_ID}" read
```

Если нужен конкретный факт, не загружай весь чат — ищи фрагмент и затем раскрывай найденную запись:

```bash
"${CLAUDE_SKILL_DIR}/scripts/chat_recall.py" --session-id "${CLAUDE_SESSION_ID}" search "точный фрагмент"
"${CLAUDE_SKILL_DIR}/scripts/chat_recall.py" --session-id "${CLAUDE_SESSION_ID}" show u-0123456789ab
```

Для exhaustive-проверки перед важным документом или решением запроси полный JSON:

```bash
"${CLAUDE_SKILL_DIR}/scripts/chat_recall.py" --session-id "${CLAUDE_SESSION_ID}" --json read --limit all
```

Считай выборку полной только когда `returned == total` и `warnings` пуст. Для диагностики добавь глобальный `--verbose`.

## Scope и provenance

- `--scope user` — прямые сообщения плюс ответы на `AskUserQuestion`; это default.
- `--scope messages` — только прямые сообщения пользователя.
- `--scope questions` — только структурированные ответы пользователя.
- Прямое сообщение можно цитировать как слова пользователя.
- При непустом `warnings` не называй exhaustive-выборку полной: текстовые блоки точны, но image content не извлечён.
- `Пользователь выбрал вариант: ...` означает выбор agent-authored label, а не дословную реплику пользователя.
- Только `Ответ пользователя: ...` внутри question record является свободным текстом пользователя.
- Сам вопрос `AskUserQuestion` написан Claude; не превращай его формулировку в утверждение пользователя.

Опцию `--include-current-turn` используй только когда текущий prompt тоже является предметом проверки.

## Если просят сохранить

Чтение никогда не разрешает запись. Только после явной просьбы сохранить summary прочитай [контракт сохранения](references/saved-summary-contract.md) и следуй ему. Без явной просьбы ничего не создавай и не обновляй.
