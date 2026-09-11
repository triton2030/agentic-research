# Выбор моделей — 2026-09-11

Адресная правка: пользователь задал Opus High по умолчанию и для документов,
Opus Max для кода, Fable Medium для умной или важной работы. Подтвердил
приоритет Fable, включая документы и код.
Источник: `_ops/chat-recall/2026-09-11-234848-codex-01a091cc.md:15-16`.

Изменены runtime policy, MCP schemas и согласованные preparation/acceptance
references. Сохранены subscription auth, native sessions, clean launch,
inspection/control, ограничение результатов и отказ при подмене модели.
Сняты Opus-only и default xhigh на основании текущего заказа.

Источники SDK: установленный sdk.d.ts, Options.effort и model;
https://code.claude.com/docs/en/model-config (проверено 2026-09-11).
`claude-opus-5-high` передаётся как model claude-opus-5 + effort high.

Проверки:
- 42 детерминированных теста прошли; включены fresh Fable, resume,
  несовпадение запрошенного семейства и fallback, MCP JSON schemas.
- Свежий MCP subprocess: discovery всех четырёх tools, реальные blocking
  Opus High/Max и managed Fable Medium; session после проверки остановлена.
- Три независимых проверяющих: intent, instructions, trajectory.
  Общая находка о Non-Claude исправлена на модели вне Opus 5/Fable 5.
- quick_validate: valid; git diff --check: clean; installed package совпадает
  с experiments/claude-bridge/codex-skill/1claude-mcp, включая metadata.

Ограничение: fresh Codex host не запускался. Текущая задача сохраняет старую
callable schema. Новый MCP процесс подтверждён, но обновление инструментов
в интерфейсе Codex требует переподключения MCP или новой задачи.
Проверка короткими ответами доказывает доступность режимов, не качество
работы над документами или кодом.

## Live receipts

```json
[
  {
    "discovery": [
      {
        "name": "claude_ask",
        "profile": {
          "type": "string",
          "enum": [
            "opus_advisor",
            "fable_advisor"
          ]
        },
        "effort": {
          "type": "string",
          "enum": [
            "medium",
            "high",
            "xhigh",
            "max"
          ]
        }
      },
      {
        "name": "claude_session",
        "profile": {
          "description": "Fresh-session model profile.",
          "type": "string",
          "enum": [
            "opus_advisor",
            "fable_advisor"
          ]
        },
        "effort": {
          "description": "Fresh-session effort; defaults to high for Opus and medium for Fable.",
          "type": "string",
          "enum": [
            "medium",
            "high",
            "xhigh",
            "max"
          ]
        }
      },
      {
        "name": "claude_observe"
      },
      {
        "name": "claude_sessions"
      }
    ]
  },
  {
    "case": "opus-high",
    "text": "ROUTING_OK",
    "session_id": "ae13488d-94c4-445c-aa7a-8825d441a558",
    "requested_model": "opus",
    "requested_effort": "high",
    "resolved_model": "claude-opus-5",
    "duration_ms": 1308,
    "warnings": []
  },
  {
    "case": "opus-max",
    "text": "ROUTING_OK",
    "session_id": "8f35c082-68ed-41c3-b7d9-cbfd235fbbaf",
    "requested_model": "opus",
    "requested_effort": "max",
    "resolved_model": "claude-opus-5",
    "duration_ms": 1126,
    "warnings": []
  },
  {
    "case": "fable-medium",
    "session_id": "36b44c8e-40fa-4cd6-b682-c1e1cea72d82",
    "state": "idle",
    "cursor": 10,
    "changed": true,
    "last_activity_age_ms": 0,
    "direction": "Claude finished and is ready for a follow-up",
    "active_tool": null,
    "thinking_tokens": null,
    "background_tasks": 0,
    "possibly_stalled": false,
    "requested_model": "fable",
    "requested_effort": "medium",
    "resolved_model": "claude-fable-5",
    "terminal": {
      "kind": "success",
      "duration_ms": 1886,
      "num_turns": 1
    },
    "warnings": [],
    "events": [],
    "messages": [
      {
        "cursor": 1,
        "role": "user",
        "text": "Reply only FABLE_OK. Do not use tools or change any files."
      },
      {
        "cursor": 10,
        "role": "assistant",
        "text": "FABLE_OK"
      }
    ]
  }
]
```
