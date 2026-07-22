---
description: "Minimal non-leading briefs for named profiles, untyped expert lenses and md-scout."
---

# Brief Templates

Read immediately before a fresh-eyes spawn.

## Brief Contract

Give the decision, why it matters, exact artifact paths, evidence/unknown,
scope and forbidden side effects. For tool-heavy roles add one line naming the
project-specific tool and its purpose.

Do not give a hypothesis-conclusion, investigative sequence, checklist,
hotspots, native role recap, desired verdict or rigid output schema. Named
profiles already own their method. An untyped lens additionally needs a compact
professional stance, not a fake identity.

## Named Critic Or Auditor

```text
Что проверить: {one decision or question}.
Now doing: {current work; include when trajectory/business context matters}.
Why: {outcome that depends on the answer}.
Где смотреть: {exact raw files, diff or artifact paths}.
Уже известно: {evidence or none}. Неизвестно: {material gap}.
Границы: in — {scope}; out — {scope}; side effects — {none/read-only/etc.}.
Доступный local tool: {one relevant tool and purpose, or omit}.
```

Select the profile through the native `Agent` tool's exact `subagent_type`; do
not restate its native contract in the brief.

## Untyped Expert Lens

```text
Ты независимый эксперт с линзой «{perspective}».

Профессиональная позиция: защищаешь {value}; не доверяешь {typical blind spot};
предпочитаешь {principle/trade-off}. Не наследуй вывод основного агента.

Решение: {one question}. Зачем: {dependent outcome}.
Где смотреть: {raw paths}. Evidence/unknown: {facts and gap}.
Границы: in — {scope}; out — {scope}; только чтение.
```

Label the return by perspective, never by an unavailable named profile.

## `md-scout`

```text
Corpus: {root}. Только чтение.
Вопрос: {one retrieval question}.
Scope: {paths/includes/exclusions}.
Решение, которое зависит от packet: {owner decision}.
Уже известно: {evidence or none}. Неизвестно: {gap}.
Вне scope: {boundary}. Relevant local route: {optional one-line hint}.
```

Main context verifies addresses and owns the verdict.
