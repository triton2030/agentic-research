---
description: "Условные правила для instruction files, skills, prompts, hooks и runtime guardrails."
read-before-edit:
  - "[[AGENTS.md]]"
  - "[[_ops/AGENTS.md]]"
  - "[[_ops/GOAL.md]]"
  - "[[_ops/project-graph.md]]"
edit-after-edit:
  - "[[AGENTS.md]]"
  - "[[_ops/AGENTS.md]]"
  - "[[_ops/project-graph.md]]"
---

# Instruction And Runtime Rules

Trigger: правишь `AGENTS.md`, `CLAUDE.md`, `SKILL.md`, prompt, hook, runtime
guardrail, `config.toml`, skill reference или модельный baseline.

Owner: wording держит `1instruction-layer`; механизм и folder/runtime contract
держит `1folder-contract`; `SKILL.md`/metadata держит `1skill-architect`;
GOAL-sync держит `1goal` + `1folder-contract`.

Check: правило меняет следующий ход агента, не дублирует skill body, не держит
дорогой запрет prompt-only, не расходится с `GPT-5.5` / `Claude Opus 4.7`.

## Instruction Files

- Root `AGENTS.md` — routing, local owner map, красные линии и короткие triggers.
- Папочный `AGENTS.md` нужен только при уникальном owner-е, риске или проверке
  зоны; boilerplate без отличия не создавать.
- Живой `SKILL.md` выигрывает конфликт с root-инструкцией.
- В instruction file не класть историю, обоснование, examples или редкую глубину.
  Оставляй trigger и ссылку на owner.
- Model-delta правка означает добавить новое правило и удалить или сузить старое,
  которое толкает сильные модели в лишний процесс, defensive repetition,
  автоматический fan-out или устаревший baseline.

## Surfaces

- Codex редактирует Codex-поверхности.
- Claude instruction/runtime surfaces читать можно, редактировать только по
  отдельной явной просьбе именно на эти surfaces.
- Claude skills можно редактировать только по явной просьбе и через
  `1skill-architect`.
- Новые/изменяемые skill-поверхности писать на русском; английский оставлять
  для кода, команд, API/tool names, путей, handles, цитат, model/product names
  и trigger words.

## Перед Правкой

- Для instruction/skill/prompt work читать ближайший `wisdom-*` и один
  релевантный guide/practical guide.
- Для Codex skill-структуры сверяться с текущими официальными OpenAI Agent
  Skills docs; `agents/openai.yaml` — optional metadata/policy surface.
- Для hooks/runtime сначала читать живой owner, текущую схему и
  `knowledge/practical-guides/hooks-runtime-guardrails.md`; не писать ключи из
  памяти.
- Prompt enforcement не считать guardrail: дорогой запрет держит hook,
  validator, permission, checkpoint или test.
