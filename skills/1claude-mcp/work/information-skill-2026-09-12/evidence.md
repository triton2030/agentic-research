# Информационный скил Claude — 2026-09-12

## Основание и граница

Текущие слова владельца: `_ops/chat-recall/2026-09-11-234848-codex-01a091cc.md:15-18`.
Скил — информационный ресурс с гибким выбором возможностей, а не обязательный
advisor workflow. Предпочтения моделей, особенности промптов и условия чтения
references сохранены. Владелец прямо разрешил исполнение и изменения файлов.
Исходник перед этой переработкой сохранён в `before/`.

## Карта изменения

| Смысл | Решение |
| --- | --- |
| Предпочтения моделей | Сохранены; Fable уточнён до доступного Fable 5.1, medium |
| Независимое мнение и unnamed second opinion | Сохранены как один из случаев использования и trigger |
| Prompt knowledge | Сохранены контекст, цель, материалы, независимость; обязательные три секции и число ограничений сняты |
| Исполнение | Native claude_code system prompt вместо трёх строк advisor; prompt передаётся без advisor XML wrapper |
| Возможности | One-shot, parallel, session control, inspection сохранены; добавлен справочник native SDK API с доступностью и условиями |
| Процедуры | Отдельные stage-references заменены четырьмя справочниками по решениям агента |
| Recovery/evidence | Сохранены реальные границы: terminal, model, truncation, resume, lifetime, state after cancellation |
| Среда | Subscription route и clean settings сохранены; _advisor в profile — legacy model selector |

## Проверки

- 42 deterministic tests проходят с final native system prompt.
- Реальный fresh MCP: Opus Max изменил только целевой исходник в тестовой
  папке; независимый Node import проверил sum(2,3) === 5.
- Реальная managed session Fable 5.1 Medium выполнила read-only review;
  исходник побайтово сохранился. Session остановлена.
- Upgrade SDK 0.3.263 → 0.3.268 и Claude Code 2.1.263 → 2.1.268:
  clean install с omit=optional; live suite проверила parallel isolation,
  resume, follow-up, steer, stop и native cancellation/process cleanup.
  Дополнительные High/Max/Fable calls успешны.
- Hono обновлён внутри допустимого dependency range; npm audit: 0 vulnerabilities.
- В test receipt writer воспроизведено изменение прав существующей parent
  directory; исправление сохраняет её права и требует private output directory.
- Три независимых review: intent, instructions, trajectory. Исправлены обе
  существенные находки: unnamed second-opinion trigger и await Promise в той
  же functions.exec cell после yield_control. Остальных material findings нет.
- quick_validate valid; local links разрешаются; installed package совпадает
  с experiments/claude-bridge/codex-skill/1claude-mcp.

## Дополнительные возможности и границы доказательства

Native supportedModels показал Fable 5.1 и Opus 5 с доступными effort;
getContextUsage(summary) вернул окно 1M и структурированную оценку заполнения.
Эти read-only probes не делали модельный запрос. Возможности смены модели,
fork, structured output, checkpoints и usage catalog подтверждены sdk.d.ts;
не заявлены как новые MCP-поля и не прошли отдельные live acceptance cases.

snapshot:false применяет native prompt и при resume старого advisor-разговора.
Цена — отказ от сохранённого system-prompt snapshot: стабильность кэша/префикса
не доказана, SDK рекомендует snapshot:true для стабильного промпта. Такой
resume всё равно сохраняет прежний разговор и не является независимым мнением.

Fresh Codex host discovery не запускался: проверен свежий MCP subprocess.
Текущая открытая задача держит старую callable schema; требуется переподключение
MCP или новая задача Codex. Проверки показывают работоспособность конкретных
случаев, не статистический рост качества.

## Источники

- https://github.com/anthropics/claude-agent-sdk-typescript/blob/main/CHANGELOG.md
- https://code.claude.com/docs/en/model-config
- https://code.claude.com/docs/en/agent-sdk/modifying-system-prompts
- установленный SDK 0.3.268: sdk.d.ts

## Компактные live receipts

```json
[
  {
    "case": "implementation",
    "session_id": "abee109e-579e-4e56-b0e0-b572acfef426",
    "requested_model": "opus",
    "requested_effort": "max",
    "resolved_model": "claude-opus-5",
    "file": "/var/folders/mr/ft3j0yjx6w5_191wrt58_45m0000gn/T/claude-native-task-fUKqJp/sum.mjs"
  },
  {
    "case": "read-only-review",
    "session_id": "8247e3e8-7312-4329-8a91-64ed83a3f974",
    "requested_model": "fable",
    "requested_effort": "medium",
    "resolved_model": "claude-fable-5-1",
    "file_unchanged": true,
    "terminal": {
      "kind": "success",
      "duration_ms": 9992,
      "num_turns": 3
    }
  }
]
```


## Уточнение о параллельных агентах

По реплике владельца `_ops/chat-recall/2026-09-11-234848-codex-01a091cc.md:19`
в tools-and-sessions добавлен условный раздел о нескольких Claude-агентах.
Он сохраняет независимость от модели/effort, сочетание Opus/Fable, обработку
первого завершения, обмен выводами через ведущего и продолжение разговоров.
Указаны фактические границы: четыре live leases, idle занимает слот, steer
прерывает turn, wait_any собирается из observe. Источник лимита —
`experiments/claude-bridge/src/claude-session.js:184`; поведение остальных
операций уже проверено описанными выше tests/live cases. Изменился только текст;
validator, diff-check и installed parity проверены повторно.
