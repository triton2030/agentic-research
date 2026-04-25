# Official Codex Skills Patterns

Снимок обновлён 25 апреля 2026.

Этот guide фиксирует, как OpenAI пишет Codex skills в официальных источниках.
Основан только на:
- Codex docs (`Agent Skills`)
- Codex use case (`Save workflows as skills`)
- OpenAI blog (`Using skills to accelerate OSS maintenance`)
- официальных репозиториях `openai/skills`, `openai/openai-agents-python`, `openai/openai-agents-js`

Нужен не как общий канон по скиллам, а как опора по стилю и форме именно официального Codex corpus.

## Что OpenAI Говорит Напрямую

- Skills в Codex — это **authoring format for reusable workflows**, а не просто тематические заметки.
- Базовый механизм — **progressive disclosure**:
  - сначала Codex видит metadata
  - потом при активации грузит `SKILL.md`
  - потом читает `references/` или запускает `scripts/` только по мере надобности
- Для implicit invocation критичен `description`: docs прямо говорят писать его с **clear scope and boundaries**.
- `openai/skills` теперь прямо позиционирован как **Skills Catalog for Codex**: `.system` skills автоматически установлены в свежем Codex, `.curated` и `.experimental` ставятся через `$skill-installer`.
- Системный `skill-creator` формулирует жёстче: для решения о вызове Codex видит `name` и `description`; body грузится только после trigger. Поэтому всё знание "когда использовать" должно быть во frontmatter `description`, а не только в секции body.
- Официальный use case рекомендует не таскать длинные промпты между тредами, а превращать повторяемую работу в skill.
- Официальный blog показывает целевой паттерн для production:
  - `AGENTS.md` задаёт обязательные repo rules
  - `.agents/skills/` держит repo-local workflows
  - `scripts/` и `references/` обслуживают детерминированные и длинные части workflow

## Что Делает Живой Официальный Корпус

- Просмотрено 66 официальных `SKILL.md`:
  - `openai/skills`: 45
  - `openai-agents-python/.agents/skills`: 9
  - `openai-agents-js/.agents/skills`: 12
- У OpenAI явно есть два живых слоя:
  - **catalog/system corpus** — installable skills в `openai/skills`
  - **repo-local corpus** — узкие operational skills в `.agents/skills` рабочих репозиториев
- Frontmatter всегда содержит:
  - `name`
  - `description`
- В части skills есть и дополнительная UI metadata surface:
  - `metadata.short-description`
- Docs отдельно поддерживают и `agents/openai.yaml`; официальный corpus в целом показывает, что Codex authoring реально использует **дополнительные metadata surfaces**, а не только `name` + `description`.
- Supporting files используются по-настоящему:
  - `scripts/`
  - `references/`
  - `assets/`
  - `agents/openai.yaml`

## Длина

- Весь официальный Codex corpus (`66` skills):
  - `SKILL.md` минимум: 25 строк
  - медиана: 81
  - среднее: 142
  - максимум: 693
- `description`:
  - минимум: 85 chars
  - медиана: 272
  - среднее: 298
  - максимум: 703

Разрез по слоям:

- `openai/skills`:
  - медиана тела: 120 строк
  - среднее: 174
- `openai-agents-python`:
  - медиана тела: 58 строк
  - среднее: 75
- `openai-agents-js`:
  - медиана тела: 56 строк
  - среднее: 73

Практический вывод:
- официальный Codex corpus в среднем **короче Claude corpus**
- особенно коротки **repo-local skills**
- длинные skills у OpenAI есть, но они обычно либо system/creator skills, либо тяжёлые domain skills

## Повторяющиеся Формы

Самые частые секции в теле:

- `Workflow`
- `Overview`
- `Quick start`
- `Prerequisites`
- `References` / `Resources`
- `Notes`
- `When to use`

Типовые рабочие формы:

- **Тонкий operational skill**
  - примеры: `gh-address-comments`, `code-change-verification`
  - суть: короткий boundary + required sequence + script/resource pointer

- **Repo-local handoff skill**
  - примеры: `pr-draft-summary`, `implementation-strategy`
  - суть: `Purpose` / `When to Trigger` / `Inputs` / `Workflow` / `Output expectations`

- **Long procedural skill**
  - примеры: `runtime-behavior-probe`, `skill-creator`, `playwright-interactive`
  - суть: detailed rules, case matrix, resources, templates, failure handling

У OpenAI заметен устойчивый каркас:
- сначала **boundary or overview**
- потом **quick start**
- потом **workflow**
- потом **resources / references / output expectations**

## Какие Слова Они Выбирают

Официальный Codex corpus тяготеет к boundary-heavy operational vocabulary:

- `use when`
- `use only when`
- `do not`
- `skip only for`
- `when changes affect`
- `ensure`
- `run`
- `keep`
- `prefer`
- `confirm`
- `report`

Это другой ритм, чем у Claude:
- меньше “philosophy” и narrative framing
- больше routing, guardrails, required order и explicit skip-cases

## `description`: Как Пишет Официальный Корпус

Частые формулы:

- `Use when ...`
- `Trigger when ...`
- `Use only when ...`
- `Do not ...`
- `Skip only for ...`
- `When changes affect ...`

Наблюдение:
- `description` у OpenAI часто не короткий label, а **жёсткий routing contract**
- туда выносятся:
  - trigger surface
  - реальные user phrases
  - tool / workflow preference
  - repo boundary
  - skip-cases
  - expected output
  - sometimes exact conditions of use

Практически это значит:
- OpenAI не стесняется длинного `description`, если он режет ambiguity
- описание должно говорить не только **что делает skill**, но и **когда его нельзя или не нужно звать**
- `description` нужно писать как маленький matcher prompt: какие слова пользователь скажет, какой тип задачи это значит, что skill должен включить, какие соседние случаи не сюда
- секция `When to use` в body может быть полезна человеку после загрузки skill, но не заменяет frontmatter-trigger, потому что body ещё не виден на момент выбора skill

Типовой официальный каркас:

```text
[What the skill does].
Use when [task class / user intent / exact context].
Trigger when [likely user phrases].
Prefer/use [tool or workflow] when relevant.
Do not trigger for [adjacent but out-of-scope cases].
```

Наблюдаемые примеры:
- `vercel-deploy` ловит не только смысл, но и exact phrases вроде "deploy my app", "push this live", "create a preview deployment".
- `security-threat-model` и `security-best-practices` используют negative triggers, чтобы не перехватывать general architecture, code review или debugging.
- `gh-fix-ci` вшивает прямо в `description` tool choice (`gh`), scope boundary (GitHub Actions), expected loop и safety gate.
- `pdf` показывает плотный вариант: объект работы, условие важности layout/rendering и preferred tooling в одной строке.

## Metadata Surface

Для Codex это особенно важно:

- docs прямо включают metadata в progressive-disclosure layer
- docs отдельно называют optional metadata from `agents/openai.yaml`
- официальный corpus местами использует `metadata.short-description` внутри frontmatter

Вывод:
- у Codex skill authoring metadata — это не декоративный слой
- это реальная часть discovery и UI surface

## Naming

`skill-creator` рекомендует:

- lowercase
- digits and hyphens only
- short names
- prefer short verb-led phrases
- namespace by tool when это повышает ясность

Живой corpus это в целом подтверждает:

- `gh-address-comments`
- `code-change-verification`
- `implementation-strategy`
- `runtime-behavior-probe`
- `pr-draft-summary`
- `openai-docs`

Вывод:
- у OpenAI naming чаще action-first и tool-aware
- noun-like names встречаются, но operational/action names заметно доминируют

## Полезные Расхождения Внутри Самого Corpus

- Catalog skills в `openai/skills` чаще длиннее и универсальнее.
- Repo-local skills в agents repos заметно короче, жёстче и теснее привязаны к конкретному repo workflow.
- System skills вроде `skill-creator` задают идеологию authoring, но production repos показывают ещё более сжатый стиль.

Поэтому полезно держать два слоя отдельно:
- **Documented**: reusable workflow, progressive disclosure, boundary-driven `description`
- **Observed**: короткие repo-local operational playbooks с явным trigger и concrete output

## Durable Takeaways

- Для Codex сначала оптимизировать **routing contract**, потом красоту prose.
- Короткий и жёсткий `SKILL.md` — нормальная официальная форма, особенно для repo-local skills.
- `Workflow` и `Quick start` — почти дефолтный каркас.
- Skip-cases и boundaries писать прямо в `description`, а не надеяться, что модель “сама поймёт”.
- Deterministic части лучше выносить в `scripts/`.
- Variant-heavy и длинные детали лучше выносить в `references/`.
- Metadata в Codex — полноценная surface area, а не второстепенное украшение.
- Хороший официальный Codex skill обычно звучит как компактный operational contract, а не как explanatory essay.
