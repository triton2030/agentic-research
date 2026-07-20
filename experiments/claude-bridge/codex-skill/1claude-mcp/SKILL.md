---
name: 1claude-mcp
description: >-
  Когда нужен независимый review, second opinion или совет принципиально другой
  model family — либо пользователь просит Claude, Opus или Fable — вызови Claude
  advisor. Native Codex fresh eyes → `1fresh-eyes`.
---

# Claude Advisor

## Outcome

Получить один компактный, evidence-backed взгляд Claude через managed
`claude_ask`. Codex остаётся owner scope, проверки, синтеза и ответа
пользователю; Claude — внешний советник, не acceptance owner. Никогда не запускай
сырой `claude` subprocess и не восстанавливай старые run/thread/tmux tools.

## Default Path

1. Выбери `opus_advisor` по умолчанию. `fable_advisor` оставь для самых сложных
   long-horizon, multi-system или high-stakes решений.
2. Передай реальный project/worktree `cwd` и короткий self-contained prompt:
   outcome, текущий claim/decision, точные sources, material boundaries,
   требуемое evidence, output и stop condition. Не копируй сырой chat dump.
3. Вызови один blocking `claude_ask`. Он может работать несколько минут;
   продолжай тот же host call, не запускай параллельный retry или polling.
4. Прочитай `requested_model`, `resolved_model`, `warnings` и `session_id`.
   Fable → Opus — успешное изменение model resolution, если оно явно видно в
   result; не выдумывай причину.
5. Проверь существенные claims локально и синтезируй ответ как мнение Claude,
   а не как собственный доказанный verdict.

Рабочая форма brief:

```xml
<role>External role and authority.</role>
<task>Exact deliverable and stop condition.</task>
<claim>Decision, plan, diff, or risk to challenge.</claim>
<sources>Exact local paths or public URLs to inspect.</sources>
<boundaries>Investigate/do-not-modify instruction and accepted native authority.</boundaries>
<evidence>Required facts, gaps, and uncertainty.</evidence>
<output>Verdict first; compact handoff.</output>
```

## Sessions, Paths, And Skills

- Продолжай полезный разговор, передавая returned `session_id` и тот же `cwd`.
  Для blind review, другой ветки/проекта или независимого мнения начни fresh call
  без `session_id`.
- Несколько Codex agents могут параллельно держать отдельные Claude sessions:
  не переиспользуй чужой UUID; каждый caller хранит собственный `session_id`.
- Ручной `add_dirs` не нужен. Advisor может читать любой OS-accessible локальный
  путь; macOS privacy permissions всё ещё могут закрыть Desktop/Documents/другие
  protected zones.
- Claude сохраняет native tools, Bash/Edit/Write, settings, skills, hooks и MCP.
  Bridge сам добавляет поведенческую инструкцию исследовать и не менять state,
  но технического read-only sandbox нет: остаточный риск записи/удаления принят
  owner-ом для personal-local advisor.
- Когда outcome зависит от конкретного Claude skill, прямо попроси вызвать его;
  финальный self-report сам по себе не является structured tool-event proof.

## External And Billing Boundaries

`claude_ask` честно помечен `openWorld`: named local material будет отправлено в
Anthropic Claude service. Если host требует отдельное external-data approval,
назови точный scope и продолжай только после подтверждения пользователя. Не
анонимизируй owners и не обходи gate. Cancellation до dispatch означает, что
Claude run не стартовал; это не timeout Bridge.

Bridge удаляет уже присутствующие явные API/provider route env vars и в том же
environment требует `claude.ai` / `firstParty` subscription auth. Он не сканирует
native settings как hostile config и не имеет API/provider fallback. Не
подставляй key/token/base URL и не меняй billing route ради восстановления.
Детали account setup и Usage credits читай в owner-файле
[`subscription-billing.md`](/Users/triton/Documents/GitHub/agentic-research/experiments/claude-bridge/docs/subscription-billing.md)
только при auth/billing diagnosis — не загружай его в обычный advisor call.

## Conditional Routes And Stop

- Необычно сложный Fable brief или fallback →
  [fable-agent-prompting.md](references/fable-agent-prompting.md).
- Тонкая настройка обычного Opus review →
  [opus-agent-prompting.md](references/opus-agent-prompting.md).
- Tool missing/stale, approval, auth, malformed output или cancellation →
  [mcp-failure-handling.md](references/mcp-failure-handling.md).

Stop после одного bounded result и локальной проверки нужных claims. Если tool
не виден, уже открытая Codex task может держать старую MCP schema: проверь в
fresh task. Не объявляй Claude review выполненным без terminal result.
