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

**Три уровня планирования (других владельцев у уровней нет):**

- **Level 1 — `_ops/PROJECT-ROADMAP.md`** (owner `project-strategy`): путь от нуля до конца — Goal, Approach, Stages (фазы), Anti-goals; `_ops/learnings.md` рядом
- **Level 2 — `_ops/plans/phase-NN-<slug>/task-MM-<slug>.md`** (owner `1task-contract`): одна задача = один файл, Цель + Stage anchor
- **Level 3 — Подшаги / Must / Must-not / Verification внутри task-file** (owner `1task-contract`)

`1repo-shape`, `1instruction-layer`, `1before-work`, `before-write`,
`work-review` обслуживают runtime/folders/routing/moments — не уровни
планирования.

- `user-truth` владеет `_ops/INTERVIEW.md`
- `_ops/plans/` — эфемерный слой; не ссылаться на пути внутри него извне
- Не создавать numbered `_ops/*` вроде `1-NORTH-STAR.md`, `2-RATIONALE.md`, `3-CURRENT-STRATEGY.md`
- Не создавать `_ops/inbox/`, task trackers и другие ops-поверхности сверх контрактов live skills

## Минимальный След

- По умолчанию новые файлы, разделы и абзацы не создавать
- Сначала обновлять существующий правильный файл; если его нет, назвать функцию будущего файла до создания
- Каждый файл держит одну функцию; содержимое вне функции файла не добавлять
- Не заводить side-docs, summaries, handoff notes и дополнительные explainers без явного запроса
- Каждый новый файл, раздел и лишнее слово считать будущим drift-point

## Куда Что Класть

- Общие выводы для любых агентов, skills, LLM или платформ → `knowledge/`
- Короткие практические гайды → `knowledge/practical-guides/`
- Канонические guides / playbooks / official pattern studies → `knowledge/guides/`
- Эталонные артефакты → `knowledge/examples/`
- Категорийные learnings и inventories → `knowledge/research/{category}/`
- Новый agent / skill / plugin → `projects/{category}/...`
- Retired или superseded project artifacts → `projects/_archive/`, если их нужно сохранить как историю
- Skill-owned operational state → `_ops/` только когда его реально создаёт live skill

## Перед Работой

- Перед нетривиальной работой читать релевантный `knowledge/wisdom-*.md`; если неясно, начинать с `knowledge/wisdom-agents.md`
- Для крупных shape/routing задач читать `knowledge/wisdom-systems-thinking.md`
- Перед работой в категории читать `knowledge/research/{category}/learnings.md`
- Skills использовать как routing, не как preload
- Default chain для существенной repo-level работы: `1before-work` → нужный owner-skill → execution → `work-review`
- Перед substantive Edit/Write использовать `before-write`
- Task-file scope/criteria/status/closeout → `1task-contract`
- Direction/Goal/roadmap/status reconciliation → `project-strategy`; unresolved approach branches / domain prerequisites / missing-middle questions → `1strategy-discussion`; user preferences/vision/conflicts → `user-truth`
- Skill/trigger design → `skill-architect`; AGENTS/CLAUDE/routing placement → `1instruction-layer`; folders/hooks/permissions/MCP/validators → `1repo-shape`
- `1step-back` — dialog-time framing и один короткий zoom-out/reframe ход
- `1guide-subagents` — только когда пользователь явно хочет Codex subagents / delegation / parallel workers / multiple agents
- Если root docs и skill conflict, следовать skill contract
- Если инструкция ссылается на глобальный Codex-skill, сначала проверять реальный installed handle в `/Users/triton/.codex/skills`

## Локальные Инструменты

- Для поиска и инвентаризации сначала использовать `rg`, `fd`,
  `git status/diff/log`; `find` — только при необходимости
- Для JS/TS/Markdown/package evidence доступны: `knip`, `lychee`,
  `markdownlint-cli2`, `tsc`, `biome`, `eslint`, `stylelint`,
  `depcruise`, `ast-grep`/`sg`, `publint`, `attw`, `syncpack`,
  `gitleaks`, `osv-scanner`, `trivy`, `semgrep`, `actionlint`
- Предпочитать repo-local запуск (`pnpm exec`, `npm exec --`,
  `npx --no-install`) перед глобальными бинарями; глобальные
  Homebrew/npm tools — fallback evidence
- `repo-power-tools` вызывать, когда нужны быстрые CLI evidence для
  cleanup/move/delete/dead-code/docs-link/import/package/security задач;
  root docs только напоминают о tool surface

## Правила Письма

- Писать как можно короче; каждое слово должно платить за место
- По умолчанию писать только запрошенное
- Не выдумывать facts
- Не придумывать новые разделы, описания и пояснения без необходимости
- Отделять факты от гипотез
- Имена обычных файлов и проектных папок — `kebab-case`
- `AGENTS.md`, `CLAUDE.md`, `knowledge/`, `projects/`, `_ops/` — допустимые исключения
