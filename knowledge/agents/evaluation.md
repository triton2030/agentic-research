---
description: Оценка агента — trajectory eval, observable acceptance criteria, multi-channel audit, cross-family judge и manual prototype first.
---

# Agents — Evaluation

Снимок на 20 мая 2026. Снято с `wisdom-agents.md` при function-split refactor.

Здесь принципы про оценку агента: что считать evidence, как чинить, где
проверять траекторию, не только финал. Runtime guarantees — `runtime-layer.md`.
Memory effectiveness — `memory.md`.

## Проверено

- Оценивать нужно не только финальный ответ, но и траекторию: какие гипотезы строились, где агент повторялся, как менял план и на каких доказательствах основывал вывод.
- Acceptance criteria сильнее всего работают там, где они observable, unambiguous и non-bypassable. Self-report не считается evidence.
- Testable in isolation применимо не только к тестам: каждое важное требование лучше проверять отдельным наблюдаемым сигналом.
- Ограничения для агентов полезно различать по типу: formatting, semantic и tool. Это помогает проверять и чинить ровно тот слой, где агент ошибается.
- Для серьёзного agent audit слаб один judge-канал: надёжнее сочетать deterministic checks, rubric review и security/scope review; при нехватке evidence честнее вернуть `unknown` или `escalate`, чем симулировать уверенность.
- Self-eval скилла лучше делать второй рабочей модельной семьёй (`GPT` ↔ `Claude`): same-family judge даёт self-enhancement bias.
- Перед автоматизацией пайплайна — собрать один пример руками. Без manual prototype скилл-обёртка кодифицирует ошибки, которые ещё не пойманы.

## Опоры

- https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
  Prompt engineering guidance: явность инструкций, scope, tool policy.

- `/knowledge/practical-guides/how-to-write-skills/`
  Authoring canon, checklist, platform-deltas и research evidence для self-eval против.
