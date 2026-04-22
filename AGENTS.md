# Агентные Инструкции

## Назначение

База — для авторства скиллов, агентов, промптов и instruction files для Codex, Claude Code и соседних платформ.

Фокус проекта — не runtime-код агентов, а shape их поведения: skill contracts, system prompts, routing, guardrails, examples, research-backed guidance.

## Приоритет

- Живые `SKILL.md` — load-bearing truth layer для skill-owned поведения.
- Если root-инструкция конфликтует с живым skill contract, выигрывает `SKILL.md`.
- `AGENTS.md` — про структуру репо, routing и placement rules, а не дубликат skill bodies.

## Структура

- `knowledge/` — общие выводы, гайды, референсы, examples, category research
- `projects/` — проектные папки артефактов
- `projects/_archive/` — архивная зона для retired / superseded project artifacts; не source of truth по умолчанию
- `_ops/` — skill-owned operational layer; по умолчанию держать пустым
- Корневые файлы: `AGENTS.md`, `CLAUDE.md`

## knowledge/

- В корне `knowledge/` держать только `wisdom-*.md`
- `knowledge/practical-guides/` — короткие практические гайды
- `knowledge/guides/` — плоский слой для `perfect-*`, `*-playbook.md`, `official-*-patterns.md`
- `knowledge/examples/` — эталонные артефакты из дикой природы
- `knowledge/research/{business,design,dev,meta}/` — категорийные learnings, links, inventories
- Новые подпапки в `knowledge/guides/` не создавать
- Новые подпапки в `knowledge/research/{category}/` не создавать

## projects/

- Путь: `projects/{category}/{name}--{type}-{platform}/`
- `category`: `business` | `design` | `dev` | `meta`
- `type`: `agent` | `skill` | `plugin`
- `platform`: `codex` | `claude-code`
- `name`: `kebab-case`
- У проектной папки должен быть короткий `README.md`
- Папка в `projects/` без `README.md` или без load-bearing артефакта не считается живой surface; её нужно либо довести до валидного вида, либо архивировать/удалить
- Для новых control surfaces по умолчанию предпочитать `skill`, а не отдельный `agent`, если пользователь явно не просит agent-shaped artifact

## _ops/

- `_ops/` — не общий склад заметок, backlog и случайных plan-файлов
- По умолчанию `_ops/` должен быть пустым
- Если `main-strategy` реально активирован и работа требует durable layer, он владеет:
  - `_ops/PROJECT-PLAN.md`
  - `_ops/INTERVIEW.md`
  - `_ops/learnings.md`
- Не создавать numbered `_ops/*` вроде `1-NORTH-STAR.md`, `2-RATIONALE.md`, `3-CURRENT-STRATEGY.md`
- Не создавать `_ops/inbox/`, `_ops/plans/`, task trackers и другие ops-поверхности без явного запроса пользователя и явного skill contract, который этого требует

## Минимальный След

- По умолчанию новые файлы не создавать
- Сначала обновлять существующий правильный файл
- Не заводить side-docs, summaries, handoff notes и дополнительные explainers без явного запроса
- Каждый новый файл и лишний абзац считать будущим drift-point

## Куда Что Класть

- Общие выводы для любых агентов, skills, LLM или платформ → `knowledge/`
- Короткие практические гайды → `knowledge/practical-guides/`
- Канонические guides / playbooks / official pattern studies → `knowledge/guides/`
- Эталонные артефакты → `knowledge/examples/`
- Категорийные learnings и inventories → `knowledge/research/{category}/`
- Новый agent / skill / plugin → `projects/{category}/...`
- Retired или superseded project artifacts → `projects/_archive/`, если их нужно сохранить как историю
- Skill-owned operational state → `_ops/` только когда его реально создаёт живой skill

## Перед Работой

- Перед нетривиальной работой читать релевантный `knowledge/wisdom-*.md`; если неясно, начинать с `knowledge/wisdom-agents.md`
- Для крупных shape/routing задач читать `knowledge/wisdom-systems-thinking.md`
- Перед работой в категории читать `knowledge/research/{category}/learnings.md`
- Skills использовать как routing, не как preload
- Для существенной repo-level работы default owner-chain такой:
  - `main-strategy` — durable plan / preferences / `_ops/`
  - `system-architect` — instruction layer, folder ownership, guardrails
  - `criteria-generator` — task-level hard contract
- `step-back` — dialog-time framing и один короткий zoom-out/reframe ход
- `guide-subagents` — только когда пользователь явно хочет subagents/delegation
- Если root docs и skill conflict, следовать skill contract
- Если инструкция ссылается на глобальный Codex-skill, сначала проверять реальный installed handle в `/Users/triton/.codex/skills`

## Правила Письма

- Писать как можно короче
- По умолчанию писать только запрошенное
- Не выдумывать facts
- Не добавлять разделы и пояснения без необходимости
- Отделять факты от гипотез
- Имена обычных файлов и проектных папок — `kebab-case`
- `AGENTS.md`, `CLAUDE.md`, `knowledge/`, `projects/`, `_ops/` — допустимые исключения
