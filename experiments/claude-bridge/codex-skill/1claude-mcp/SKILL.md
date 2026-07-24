---
name: 1claude-mcp
description: >-
  Когда нужно независимое ревью, второе мнение или совет другой model family —
  либо явный вызов Claude, Opus или Fable — вызови advisor. Не для вопросов о
  Claude; native Codex review → `1fresh-eyes`.
---

# Claude Advisor

## Outcome

Получить один компактный evidence-backed взгляд Claude через `claude_ask`.
Codex остаётся owner scope, проверки, синтеза и ответа пользователю; Claude —
внешний советник, не acceptance owner.

## Default Path

1. Выбери `opus_advisor` (`claude-opus-5`) по умолчанию. `fable_advisor`
   (`claude-fable-5`) оставь для самых сложных long-horizon, multi-system или
   high-stakes решений.
2. Передай реальный project/worktree `cwd` и короткий self-contained brief:
   outcome; claim/decision; точные paths или URLs; material boundaries; evidence
   bar; compact verdict-first output; stop condition. Не копируй сырой chat dump.
3. Вызови один blocking `claude_ask`. Он может работать несколько минут;
   продолжай тот же host call, не запускай polling или параллельный retry.
4. Прочитай `requested_model`, `resolved_model`, `warnings` и `session_id`.
   Fable → Opus — успешное изменение model resolution, если оно явно видно в
   result; не выдумывай причину.
5. Проверь существенные claims локально и синтезируй ответ как мнение Claude,
   а не как собственный доказанный verdict.

## Sessions, Paths, And Skills

- Продолжай полезный разговор через returned `session_id` и тот же `cwd`.
  Native session сохраняет свою модель: resume profile её не переключает. Для
  blind review, другой ветки/проекта или нового frame начни fresh call.
- Несколько Codex agents могут параллельно держать отдельные Claude sessions:
  не переиспользуй чужой UUID; каждый caller хранит собственный `session_id`.
- Ручной `add_dirs` не нужен. Claude сохраняет session-local native tools,
  settings, skills, hooks, MCP, deferred tool discovery и доступ к любому
  OS-accessible пути. Точный tool set зависит от runtime; не копируй в brief
  статический каталог. Инструкция исследовать и не менять state —
  поведенческая, не read-only sandbox.
- Когда outcome зависит от конкретного Claude skill, tool или orchestration
  mode, читай [claude-native-tools.md](references/claude-native-tools.md).

## External And Billing Boundaries

`claude_ask` отправляет переданный prompt и прочитанный material в Anthropic.
Следуй host approval; не обходи его, но и не изобретай дополнительный запрет на
локальные/project files после разрешения scope.

Не подставляй API key/token/provider/base URL ради recovery. При auth или billing
ошибке читай единственный owner-файл
[`subscription-billing.md`](/Users/triton/Documents/GitHub/agentic-research/experiments/claude-bridge/docs/subscription-billing.md)
— не загружай его в обычный advisor call.

## Conditional Routes And Stop

- Сложный Fable brief или model-resolution mismatch →
  [fable-agent-prompting.md](references/fable-agent-prompting.md).
- Когда качество Opus review зависит от роли, sources или output shape →
  [opus-agent-prompting.md](references/opus-agent-prompting.md).
- Конкретный Claude `Skill`, MCP capability, subagent, monitor или workflow →
  [claude-native-tools.md](references/claude-native-tools.md).
- Tool missing/stale, approval, auth, malformed output или cancellation →
  [mcp-failure-handling.md](references/mcp-failure-handling.md).

Stop после одного bounded result и локальной проверки material claims. Не
объявляй Claude review выполненным без terminal result.
