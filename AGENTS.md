# Агентные Инструкции

## Назначение

База — чтобы скилы, агенты, промпты и instruction files для Codex, Claude Code
и соседних платформ получались качественными за счёт активного чтения локальных
знаний, исследований, статей и examples.

Фокус проекта — не runtime-код агентов и не каталог project artifacts, а
research-backed shape их поведения: skill contracts, system prompts, routing,
guardrails, examples и сырые идеи, которые могут дозреть до канона.

Текущая модельная рамка канона — только `GPT-5.5` и `Claude Opus 4.7`.
Советы под старые или соседние модели не считать рабочим baseline, если они не
переобоснованы в `wisdom-*` / `guides/`.

Model-delta правка означает не только добавить новое правило, но и удалить или
сузить старое правило, которое толкает сильные модели в лишний процесс,
defensive repetition, автоматический fan-out или устаревший baseline.

## Приоритет

- Живые `SKILL.md` — load-bearing truth layer для skill-owned поведения.
- Если root-инструкция конфликтует с живым skill contract, выигрывает `SKILL.md`.
- `AGENTS.md` задаёт repo routing и placement rules, а не дублирует skill bodies.
- OpenAI prompt guidance для `GPT-5.5`: prompts должны быть короче,
  outcome-first, с явными success criteria, constraints, validation и stop
  rules; старый process-heavy prompt stack не переносить по инерции.

## Структура

- `README.md` — публичное объяснение проекта и того, почему структура такая
  (owner `1project-strategy` для общей рамки).
- `knowledge/` — знания, исследования, гайды, examples и category research.
- `_ops/PROJECT-ROADMAP.md` — стратегия верхнего уровня: Goal, Approach, Stages, Anti-goals.
- `_ops/criteria/*.md` — постоянные критерии приёмки по сфере будущей работы.
- `_ops/plans/**` — эфемерные task-файлы только для активной сложной работы.
- Корневые файлы: `AGENTS.md`, `CLAUDE.md`.

## knowledge/

- В корне `knowledge/` держать только `wisdom-*.md`.
- `knowledge/practical-guides/` — короткие практические гайды.
- `knowledge/guides/` — плоский слой для `perfect-*`, `*-playbook.md`, `official-*-patterns.md`.
- `knowledge/examples/` — эталонные артефакты из дикой природы.
- `knowledge/research/{business,design,dev,meta}/` — категорийные learnings, article/source links, inventories.
- Новые подпапки в `knowledge/guides/` не создавать.
- Новые подпапки в `knowledge/research/{category}/` не создавать.

## _ops/

- `_ops/` — не общий склад заметок, backlog, идей, исследований или случайных plan-файлов.
- По умолчанию `_ops/` содержит только `PROJECT-ROADMAP.md`, `criteria/` и ленивый `plans/`.
- `INTERVIEW.md` и `LEARNINGS.md` не являются live owner surfaces; не восстанавливать их.
- Новый проект или отсутствующий `_ops` work-shape не собирать руками. Запускать
  `python3 /Users/triton/.codex/skills/1start-here/scripts/init_project_shape.py <repo-root>`.
  Скрипт создаёт `README.md`, `_ops/PROJECT-ROADMAP.md`, `_ops/criteria/` и
  `_ops/plans/`, не перетирая существующие файлы.

**Три уровня работы:**

- **Level 1 — `_ops/PROJECT-ROADMAP.md`** (owner `1project-strategy`):
  стратегия и стадии от нуля до результата — Goal, Approach, Stages,
  Anti-goals.
- **Level 2 — имена task-файлов в `_ops/plans/phase-NN-<slug>/task-MM-<slug>.md`**
  (owner `1task-contract`): список задач внутри Stage живёт как task-file
  handles/filenames, а не как список в roadmap.
- **Level 3 — `Подшаги` внутри task-file** (owner `1task-contract`):
  конкретные действия, Must/Must-not, Verification, closeout evidence.
- **Criteria — `_ops/criteria/*.md`** (write/protocol owner `1user-truth`):
  постоянные критерии приёмки по сфере будущей работы; `1instruction-layer`
  отвечает за placement и ссылки на них, task-файлы ссылаются на них.

`1start-here`, `1repo-shape`, `1before-work`, `1before-write`,
`1work-review` обслуживают runtime/folders/routing/moments — не уровни
планирования.

## _ops/criteria/

- Критерии выбираются по сфере будущей работы и готовности для агента, а не по
  редактируемому пути или широкой абстрактной теме.
- Один и тот же файл может требовать разные criteria: текст посадочной страницы,
  дизайн, frontend animation, skill authoring, instruction layer или repo shape.
- Точный шаблон criteria-файла и протокол записи держит `1user-truth`; не
  дублировать его в AGENTS/CLAUDE/папочных инструкциях.
- Критерий пишется только из прямого пользовательского сигнала или источника
  проекта, который пользователь явно утвердил; цели и критерии принятия нельзя
  додумывать за пользователя.
- Если criteria-файл растёт, сначала сжимать и объединять смысл; разбивать
  только когда появились разные типы работ, которые часто вызываются отдельно.

## Минимальный След

- По умолчанию новые файлы, разделы и абзацы не создавать.
- Сначала обновлять существующий правильный файл; если его нет, назвать функцию будущего файла до создания.
- Каждый файл держит одну функцию; содержимое вне функции файла не добавлять.
- Не заводить side-docs, summaries, handoff notes и дополнительные explainers без явного запроса.
- Каждый новый файл, раздел и лишнее слово считать будущим drift-point.

## Куда Что Класть

- Общие выводы для любых агентов, skills, LLM или платформ → `knowledge/`.
- Короткие практические гайды → `knowledge/practical-guides/`.
- Канонические guides / playbooks / official pattern studies → `knowledge/guides/`.
- Эталонные артефакты → `knowledge/examples/`.
- Категорийные learnings и inventories → `knowledge/research/{category}/`.
- Публичное “что это за проект и почему так устроено” → `README.md` через
  `1project-strategy`.
- Стратегия и стадии → `_ops/PROJECT-ROADMAP.md`.
- Постоянные критерии приёмки → `_ops/criteria/*.md`.
- Level-2 task names/handles и активная task scope / subtasks / closeout
  evidence → `_ops/plans/**/task-*.md`.
- Новый agent / skill / plugin не создавать как repo artifact по умолчанию; если нужен живой control surface, сначала выбрать installed/global handle или отдельную strategy/package линию.
- Retired или superseded artifacts по умолчанию не хранить; важный урок извлекать в `knowledge/` или `_ops/criteria/`.

## Перед Работой

- Сначала прочитать `AGENTS.md`; если работа публично-проектная, также `README.md`.
- Перед нетривиальной работой читать релевантный `knowledge/wisdom-*.md`; если неясно, начинать с `knowledge/wisdom-agents.md`.
- Для крупных shape/routing задач читать `knowledge/wisdom-systems-thinking.md`.
- Перед работой в категории читать `knowledge/research/{category}/learnings.md`.
- Перед созданием или правкой skill / agent / instruction file начинать с
  ближайшего `wisdom-*` и одного релевантного guide/practical guide.
- Чтение расширять только пока оно меняет owner, constraints, validation или
  stop condition; не читать ради полноты.
- Для skill / prompt / instruction правок сначала сверять модельную рамку:
  `GPT-5.5` и `Claude Opus 4.7`, outcome/scope/evidence/stop до процесса.
- Для любой substantive работы выбрать релевантные `_ops/criteria/*.md` по
  сфере будущей работы и применить их как критерии приёмки.
- При создании или правке папочных instruction files перечислить, какие
  `_ops/criteria/*.md` могут пригодиться для работы в этой папке; файлов может
  быть несколько, выбор делается по сфере будущих задач.
- В `AGENTS.md`, `CLAUDE.md` и папочные инструкции не копировать сами критерии;
  давать ссылки на нужные файлы из `_ops/criteria/`.
- Критический анализ служит цели пользователя, а не остановке ради остановки:
  сначала понять желаемый эффект, но не считать желание доказательством
  правильности способа.
- Skills использовать как routing, не как preload.
- Начало работы в repo/project, новый проект, отсутствующая базовая
  shape-структура или вопрос “какой skill брать?” → `1start-here`.
- Moment layer включать по риску, а не как ритуал: `1before-work` при
  нетривиальном старте или unclear branch, `1before-write` перед substantive
  Edit/Write, `1work-review` перед closeout или когда есть criteria/evidence.
- Task-file scope/criteria/status/closeout → `1task-contract`.
- Direction/Goal/roadmap/status reconciliation и общая рамка `README.md` →
  `1project-strategy`.
- Unresolved approach branches / domain prerequisites / missing-middle questions → `1strategy-discussion`.
- Durable user preference, tone, red line или рабочий default → `1user-truth`,
  который выбирает owner: root-инструкции / `_ops/criteria/*.md` /
  roadmap / task-file; не в `INTERVIEW.md`.
- Вопрос “куда положить правило/механизм” → `1instruction-layer`. Уже выбранная
  skill-работа (`SKILL.md`, trigger, frontmatter, `openai.yaml`) →
  `1skill-architect`; уже выбранная runtime/folder/tooling работа
  (folders/hooks/permissions/MCP/validators/scripts) → `1repo-shape`.
- `1step-back` — dialog-time framing и один короткий zoom-out/reframe ход.
- `1criteria-council` — только когда пользователь явно хочет субагентов /
  несколько агентов / совет ролей для многокритериального решения.
- Если root docs и skill conflict, следовать skill contract.
- Если инструкция ссылается на глобальный Codex-skill, сначала проверять реальный installed handle в `/Users/triton/.codex/skills`.

## Локальные Инструменты

- Для поиска и инвентаризации сначала использовать `rg`, `fd`,
  `git status/diff/log`; `find` — только при необходимости.
- GitHub/push workflow читать через `_ops/criteria/git-backup-workflow.md`:
  GitHub здесь — backup локального `main`, а не branch/PR collaboration flow.
- Для JS/TS/Markdown/package evidence доступны: `knip`, `lychee`,
  `markdownlint-cli2`, `tsc`, `biome`, `eslint`, `stylelint`,
  `depcruise`, `ast-grep`/`sg`, `publint`, `attw`, `syncpack`,
  `gitleaks`, `osv-scanner`, `trivy`, `semgrep`, `actionlint`.
- Предпочитать repo-local запуск (`pnpm exec`, `npm exec --`,
  `npx --no-install`) перед глобальными бинарями.
- `1repo-power-tools` вызывать, когда нужны быстрые CLI evidence для
  cleanup/move/delete/dead-code/docs-link/import/package/security задач.

## Правила Письма

- Главное правило: с пользователем писать и разговаривать только на русском, если он явно не попросил другой язык.
- Сложные программистские вещи объяснять простым русским языком; английский оставлять для кода, команд, API, имён файлов, цитат и точных handles.
- В планах, проектах и обсуждениях избегать программистского жаргона; можно использовать язык веб- и UI-дизайна: поверхности, тени, иконки, дизайн-система, компоненты, вёрстка.
- Писать как можно короче; каждое слово должно платить за место.
- По умолчанию писать только запрошенное.
- Не выдумывать facts.
- Не придумывать новые разделы, описания и пояснения без необходимости.
- Отделять факты от гипотез.
- Имена обычных файлов и папок — `kebab-case`.
- `AGENTS.md`, `CLAUDE.md`, `README.md`, `knowledge/`, `_ops/` — допустимые исключения.
