# Агентные Инструкции

## Цель

Создаём полигон знаний, критериев и рабочих контрактов, который помогает
будущей ИИ-сессии проектировать и улучшать skills, agents, prompts и
instruction files под `GPT-5.5` и `Claude Opus 4.7`.

Источник: `_ops/GOAL.md#Что делаем`. Контракт синхронизации цитаты ведёт
`1folder-contract`.

## Папочный граф

Central index папочных зависимостей и veto-class — `_ops/project-graph.md`
(owner: `1folder-contract`). Читай первым при substantive работе, чтобы
видеть какие папки задевает локальная просьба. Здесь только указатель — сам
граф живёт там, чтобы не размывать прозу инструкций.

## Контекст и границы

Фокус проекта — не runtime-код агентов, не каталог project artifacts и не
движение по заранее составленной дорожной карте. Здесь можно в разные моменты
собирать research-backed советы, проверять идеи, хранить examples и
экспериментировать с формой поведения: skill contracts, system prompts,
routing и guardrails.

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
- Для Codex поверхности Claude всегда только для чтения: `CLAUDE.md`,
  `.claude/**`, Claude skills и инструкционные файлы Claude. Codex может читать
  их как контекст, но никогда не редактирует, не создаёт, не перемещает, не
  удаляет и не форматирует; если нужна правка на стороне Claude, он
  останавливается и отдаёт её пользователю или рабочему процессу Claude.
- OpenAI prompt guidance для `GPT-5.5`: prompts должны быть короче,
  outcome-first, с явными success criteria, constraints, validation и stop
  rules; старый process-heavy prompt stack не переносить по инерции.

## Структура

- `README.md` — короткий контекст, мотивация и on-ramp для проекта (owner:
  `1strategy-docs`).
- `knowledge/` — знания, исследования, гайды, examples и category research.
- `_ops/GOAL.md` — главный контракт проекта: что делаем, что не делаем,
  definition of done и stop rules (owner: `1strategy-docs`).
- `_ops/PROJECT-ROADMAP.md` — текущий режим, путь или стадия проекта. Shape
  файла (формат, что туда идёт) — `1strategy-docs`; content updates (current
  path сдвинулся, Stage closed) — `1planning`. Это не список стадий и не
  обязательная дорожная карта.
- `_ops/criteria/*.md` — рабочие критерии по сфере будущей работы. Папка
  остаётся нужной и используется в разные моменты, когда критерии реально
  помогают задаче.
- `_ops/interviews/**` — временные интерактивные вопросники для длинного сбора
  ответов пользователя. Создавать через `1start-here` / `1folder-contract`,
  wording маршрута чинить через `1instruction-layer`, оформлять через
  `1obsidian`; после разбора переносить смысл к владельцам и архивировать.
- `_ops/findings/**` — временный слой только для реальных актуальных находок:
  ошибок, подтверждённых сомнений, результатов аудита и субагентов, которые ещё
  не стали задачей, критерием или решением.
- `_ops/plans/**` — только временные task-файлы по явному запросу для активной
  сложной работы; не backlog, не список задач и не источник истины. В
  `_ops/plans/` и каждой папке внутри неё есть `_archive/` для неактивных
  планов.
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

- `_ops/` — не общий склад заметок, backlog, идей, исследований или случайных
  plan-файлов.
- По умолчанию `_ops/` содержит `AGENTS.md`, `GOAL.md`, `PROJECT-ROADMAP.md`,
  `criteria/`, `interviews/`, `findings/` и ленивый `plans/`.
- `_ops/AGENTS.md` объясняет, как пользоваться папками `_ops/` и какие скилы
  вызывать для planning, criteria, interviews и findings.
- `INTERVIEW.md` и `LEARNINGS.md` не являются живыми рабочими поверхностями; не
  восстанавливать их. Для длинных вопросов использовать `_ops/interviews/**`,
  но только как временный вход, а не как постоянную память.
- Новый проект или отсутствующий `_ops` work-shape не собирать руками. Запускать
  `bash ~/.claude/skills/1start-here/scripts/init-three-level.sh [/path]` (Claude)
  или `python3 ~/.codex/skills/1start-here/scripts/init_project_shape.py <repo-root>` (Codex).
  Скрипт создаёт `README.md`, `_ops/AGENTS.md`, `_ops/GOAL.md`,
  `_ops/PROJECT-ROADMAP.md`, `_ops/criteria/`, `_ops/interviews/`,
  `_ops/interviews/_archive/`, `_ops/findings/`, `_ops/findings/_archive/`,
  `_ops/plans/` и `_ops/plans/_archive/`, не перетирая существующие файлы.

**Рабочие слои:**

- **Контракт — `_ops/GOAL.md`** (owner `1strategy-docs`):
  outcome-first контракт проекта: что делаем, что не делаем, definition of
  done и stop rules. README его не дублирует.
- **Планирование — `1planning`**:
  рекурсивно сужает фокус: Level 1 `_ops/PROJECT-ROADMAP.md` → Level 2
  `_ops/plans/**/task-*.md` → Level 3 подшаги внутри task-файла. Не раскрывает
  всё дерево заранее; пишет только активный уровень или ближайший фронт
  неопределённости.
- **Рамка — `_ops/PROJECT-ROADMAP.md`**:
  текущая рамка проекта без обязательной цепочки стадий. Shape файла —
  `1strategy-docs`; content updates — `1planning`.
- **Критерии — `_ops/criteria/*.md`** (write/protocol owner `1user-truth`):
  постоянные критерии приёмки по сфере будущей работы; `1instruction-layer`
  отвечает за wording/placement ссылок, `1folder-contract` — за delivery chain.
- **Интервью — `_ops/interviews/**`** (route owner `1start-here` /
  `1folder-contract`, wording owner `1instruction-layer`, truth owner
  `1user-truth`):
  временные интерактивные вопросники, когда агенту нужно много ответов от
  пользователя. Форму брать из `1obsidian`; после команды пользователя вроде
  “проверь” переносить смысл в criteria, task-файлы, roadmap, GOAL/README или
  knowledge и архивировать файл в `_ops/interviews/_archive/`. Критерий:
  `_ops/criteria/interview-intake-workflow.md`.
- **Находки — `_ops/findings/**`** (owner `1findings`):
  лёгкий временный слой только для актуальных находок до решения стратегии.
  Quick-jot path — одна команда `~/.claude/skills/1findings/scripts/add.sh
  <model> "<строка>"`, одна сессия = один файл; полная нота-документ только
  если находка реально требует структуры. Это не задачи, не критерии, не
  backlog и не общий список наблюдений.
- **Task-файлы — `_ops/plans/**`** (owner `1planning`):
  опциональная временная поверхность только для активной сложной задачи, когда
  пользователь явно хочет task contract.

`1start-here`, `1work-review` (общие для Codex и Claude), `1instruction-layer`
и `1folder-contract` обслуживают routing / review / instruction wording /
folder-system contract — не уровни планирования. В Codex structural guardrails
(folders/hooks/permissions/MCP/validators/scripts) теперь являются режимом
`1folder-contract`.

- Перед проектированием или правкой hooks / runtime guardrails читать
  `knowledge/practical-guides/hooks-runtime-guardrails.md`: hooks нужны только
  когда lifecycle-moment, owner, проверка и stop/re-check signal ясны. Для
  cross-hook / cross-skill памяти сессии — schema в
  `~/.claude/skills/1start-here/references/session-state-schema.md` (canonical
  shared structure через `~/.claude/state/session-{session_id}.json`).

## _ops/criteria/

- Критерии выбираются по сфере будущей работы и готовности для агента, а не по
  редактируемому пути или широкой абстрактной теме.
- Один и тот же файл может требовать разные criteria: текст посадочной страницы,
  дизайн, frontend animation, skill authoring, instruction layer,
  folder contract, criteria-routing или repo structure/runtime guards.
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
- Короткий публичный контекст, мотивация и reader on-ramp → `README.md` через
  `1strategy-docs`.
- Главный контракт проекта, scope, NOT in scope, definition of done и stop
  rules → `_ops/GOAL.md` через `1strategy-docs` после выбранного подхода.
- Shape стратегических документов README/GOAL/ROADMAP → `1strategy-docs`;
  текущий режим и live-roadmap правки → `_ops/PROJECT-ROADMAP.md` через
  `1planning`.
- Длинный набор вопросов к пользователю → `_ops/interviews/**` через
  `1start-here` / `1folder-contract`; Obsidian-форму брать из `1obsidian`,
  wording маршрута — через `1instruction-layer`.
- Актуальная находка, ошибка, подтверждённый риск аудита или результат
  субагента, который ещё не стал задачей, критерием или решением →
  `_ops/findings/**`.
- Описательные anti-goals / границы проекта → `_ops/GOAL.md` через
  `1strategy-docs`, если это выбранный scope-контракт.
- Anti-goals в форме правила, красной линии или повторяемого критерия →
  `_ops/criteria/*.md` через `1user-truth`.
- Постоянные критерии приёмки → `_ops/criteria/*.md`.
- Объём активной задачи, подшаги и доказательства закрытия →
  `_ops/plans/**/task-*.md` через `1planning` только по явному запросу или
  когда без task-файла работа станет мутной.
- Новый agent / skill / plugin не создавать как repo artifact по умолчанию; если нужен живой control surface, сначала выбрать installed/global handle или отдельную strategy/package линию.
- Retired или superseded artifacts по умолчанию не хранить; важный урок извлекать в `knowledge/` или `_ops/criteria/`.

## Перед Работой

- Сначала прочитать `AGENTS.md`; если работа публично-проектная, также `README.md`.
- Перед записью или разбором файлов внутри `_ops/` читать `_ops/AGENTS.md`.
- Перед нетривиальной работой читать релевантный `knowledge/wisdom-*.md`; если неясно, начинать с `knowledge/wisdom-agents.md`.
- Для крупных shape/routing задач читать `knowledge/wisdom-systems-thinking.md`.
- Перед работой в категории читать `knowledge/research/{category}/learnings.md`.
- Перед созданием или правкой skill / agent / instruction file начинать с
  ближайшего `wisdom-*` и одного релевантного guide/practical guide.
- Для создания или правки skills сначала читать
  `knowledge/practical-guides/how-to-write-skills/`, затем уже live `SKILL.md`
  и platform-specific контекст.
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
- Если для продолжения нужно много ответов пользователя, не превращать чат в
  длинное интервью: через `1start-here` создать/найти файл в
  `_ops/interviews/**`, а `1folder-contract` должен держать маршрут в системе;
  wording инструкции — через `1instruction-layer`. Форма вопросника берётся из
  `1obsidian`.
- Moment layer включать по риску, а не как ритуал: `1strategy` перед важным
  автономным/scope-changing ходом, `1planning` для task/prerequisite scope,
  локальные owner/criteria checks перед substantive Edit/Write,
  `1work-review` перед closeout или когда есть criteria/evidence.
- Рекурсивное планирование, roadmap content (current path сдвинулся, Stage closed),
  task-файлы, подшаги, статус и закрытие task-файла → `1planning`. Shape roadmap
  (формат, что туда идёт) → `1strategy-docs`.
- Выбор подхода для конкретной задачи, развилки в моменте, сырой метод или
  важный автономный ход → `1strategy` (momentum decision-thinking).
- Goal-formation, scope, definition of done, stop rules или shape
  README/GOAL/ROADMAP → `1strategy-docs` (он думает и пишет, internal work
  не делегируется в `1strategy`).
- Roadmap/current mode/stages/сверка `_ops/PROJECT-ROADMAP.md` → `1planning`;
  если вопрос о том, что вообще должно лежать в roadmap, сначала
  `1strategy-docs`.
- Unresolved approach branches при выполнении задачи / domain prerequisites /
  missing-middle questions → `1strategy`. Unresolved goal/scope/done shape →
  `1strategy-docs`.
- Устойчивая пользовательская правда, тон, красная линия или рабочий default → `1user-truth`,
  который выбирает owner: root-инструкции / `_ops/criteria/*.md` /
  рамка проекта / task-file; не в `INTERVIEW.md`. Если сигнал пришёл из
  заполненного `_ops/interviews/**`, сначала извлечь прямые ответы
  пользователя, потом записывать только нужную устойчивую правду.
- Вопрос “как сформулировать или куда положить маленькое правило” →
  `1instruction-layer`. Вопрос “какой механизм/папочный контракт/guardrail
  ведёт агента к цели” → `1folder-contract`. Уже выбранная skill-работа
  (`SKILL.md`, trigger, frontmatter, `openai.yaml`) → `1skill-architect`;
  уже выбранная runtime/folder/tooling работа
  (folders/hooks/permissions/MCP/validators/scripts) → `1folder-contract`.
- Для Codex skill-структуры сначала сверяться с текущими официальными OpenAI
  Agent Skills docs. Официальный минимум — папка с `SKILL.md`, где есть
  `name` и `description`; `scripts/`, `references/`, `assets/` и
  `agents/openai.yaml` опциональны. `agents/openai.yaml` использовать как
  metadata/policy/dependencies surface, а не как обязательный файл каждого
  скилла.
- По умолчанию используй `$1md-navigator` перед чтением папки или выбором
  между несколькими `.md` файлами/секциями. `map`, `headings` и `read-related`
  дают меню по `description`, заголовкам, ссылкам и объёму, чтобы агент быстрее
  находил owner, читал точные фрагменты и не забивал контекст шумом.
- Если один `.md` файл очевиден, читай напрямую. После выбора цели проверки
  graph/frontmatter/related-docs/dependency-radius идут через `$1md-graph`;
  смысл файла остаётся за owner: `1planning`, `1user-truth`,
  `1strategy-docs`, `knowledge/` или скиллом.
- `1step-back` — dialog-time framing и один короткий zoom-out/reframe ход.
- Codex-only `1fresh-eyes` — когда пользователь явно хочет свежие глаза,
  независимую проверку, субагентов, параллельную проверку или совет ролей.
  На Claude живёт отдельная Claude-версия этого скилла.
- Если root docs и skill conflict, следовать skill contract.
- Если инструкция ссылается на глобальный Codex-skill, сначала проверять реальный
  installed handle в текущем live-root `/Users/triton/.codex/skills`, а для
  совместимости с официальными docs также `$HOME/.agents/skills`.

## Локальные Инструменты

- Для поиска и инвентаризации сначала использовать `rg`, `fd`,
  `git status/diff/log`; `find` — только при необходимости.
- Грязное git-дерево само по себе не блокер: здесь есть только правки
  пользователя и агента. Работать с текущим содержимым файлов, не требовать
  чистого дерева перед обычной задачей.
- GitHub/push workflow читать через `_ops/criteria/git-backup-workflow.md`:
  GitHub здесь — backup локального `main`, а не branch/PR collaboration flow.
- Для JS/TS/Markdown/package evidence доступны: `knip`, `lychee`,
  `markdownlint-cli2`, `tsc`, `biome`, `eslint`, `stylelint`,
  `depcruise`, `ast-grep`/`sg`, `publint`, `attw`, `syncpack`,
  `gitleaks`, `osv-scanner`, `trivy`, `semgrep`, `actionlint`.
- Предпочитать repo-local запуск (`pnpm exec`, `npm exec --`,
  `npx --no-install`) перед глобальными бинарями.
- `1cli-tools` вызывать, когда нужны быстрые CLI evidence для
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
