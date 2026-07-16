---
description: Runtime-слой агента — где живут критические ограничения, валидация и approvals; почему prompt-only защита хрупка.
---

# Agents — Runtime Layer

Снимок на 20 мая 2026. Снято с `wisdom-agents.md` при function-split refactor.

Здесь принципы про слой исполнения агента: где живут schema, validation,
approvals, hooks, sandbox и orient-before-act. Tool design — отдельный
файл `tool-design.md`. Multi-agent runtime — `multi-agent.md`. Memory —
`memory.md`. Evaluation — `evaluation.md`. Model-specific deltas —
`knowledge/wisdom-gpt-5.6.md`, `knowledge/wisdom-claude-opus-4.7.md`.

## Проверено

- Качество агента определяется не одним prompt, а всей рабочей средой: инструкциями, контекстом, правами, форматами вывода, памятью, мониторингом и eval-петлями.
- Schema + validation + approval сильнее свободного reasoning там, где агент влияет на файлы, доступы, внешние системы или другие необратимые действия.
- Критические ограничения надёжнее держать в слое исполнения: hooks, sandbox, approvals и проверки после действия, а не только в тексте prompt.
- Reasoning и действие лучше разделять. Размышлять агент может свободно, а значимые действия должны идти через ограниченный и валидируемый слой.
- Anti-loop policy должна быть правилом исполнения: после повторяющихся неудач агент обязан сменить стратегию, сделать replan или эскалировать.
- High-risk роли по умолчанию лучше делать read-only или с жёсткой эскалацией перед опасными шагами.
- Uncertainty и human checkpoints — часть зрелой архитектуры, а не косметическое дополнение.

## Ground Before Action

- Агент не должен отвечать из training prior, когда локальный owner-контекст
  может изменить маршрут, объём, запрет или проверку.
- До существенного действия нужен дешёвый read-before-write: актуальные
  инструкции, owner-файл, критерии, граф зависимостей или ближайший контекст.
- Паттерн защищает от `vacuum-default`, `stale-anchor`, `obvious-skip`,
  `domain-bypass` и `frame capture`.
- Реализация этого принципа живёт в instruction/runtime layer: `AGENTS.md`,
  `_ops/GOAL.md`, owner/rule checks, hooks и живые routing skills. Wisdom держит
  принцип, а не операционную схему.

## Рабочие Гипотезы

- Зрелость агентной системы растёт не от длины prompt, а от качества runtime-layer: validation, hooks, approvals, logging и ясного разделения ответственности.
- Чем важнее роль агента, тем полезнее делать её уже, scope-ограниченной и менее автономной по умолчанию.

## Опоры

- https://openai.com/index/introducing-the-model-spec/
  Instruction hierarchy, роли и приоритеты правил.

- `/knowledge/guides/perfect-system-prompts.md`
  Устойчивые правила по устройству стабильного instruction layer.

- `/knowledge/practical-guides/hooks-runtime-guardrails.md`
  Операционная памятка по hooks как внешнему слою контроля.
