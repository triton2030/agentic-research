MUST:

Сначала прочитай `AGENTS.md`. Для внешнего обзора проекта читай `README.md`.

Skill contracts сильнее старых repo notes: если живой `SKILL.md` и корневая
инструкция расходятся, следуй `SKILL.md`.

Канон этого репо пишется только под `GPT-5.5` и `Claude Opus 4.7`; старые
model-neutral советы не использовать как baseline без свежей проверки.

OpenAI prompt guidance для `GPT-5.5`: предпочитай короткие outcome-first
контракты с явными success criteria, constraints, validation и stop rules.
Не переноси старый process-heavy prompt stack по инерции.

`PROJECT-ROADMAP.md` — стратегия верхнего уровня. Он не хранит task criteria,
commands, evidence, closeout, task paths или имена task-файлов.

Три уровня работы:
- Level 1 — `PROJECT-ROADMAP.md`: стратегия и стадии.
- Level 2 — имена task-файлов в `_ops/plans/**/task-*.md`.
- Level 3 — `Подшаги` внутри task-file.

`README.md` — общее публичное объяснение проекта и repo-reading route; его
общую рамку обновляет `1project-strategy`, а не criteria/task owners.

`_ops/criteria/*.md` — постоянные критерии приёмки по сфере будущей работы.
Выбирай criteria по задаче и готовности для агента, а не по редактируемому
файлу. Точный шаблон и протокол записи criteria держит `1user-truth`; не
дублируй его в instruction files. Новые цели и критерии принятия нельзя
додумывать за пользователя: только прямой пользовательский сигнал или явно
утверждённый пользователем источник проекта.

Папочные instruction files должны перечислять, какие `_ops/criteria/*.md`
могут пригодиться для работы в этой папке. Файлов может быть несколько. Сами
критерии не копировать в instruction file; давать ссылки на файлы.

`INTERVIEW.md` и `LEARNINGS.md` больше не являются live owner surfaces. Не
восстанавливай их. Durable user preference / tone / red line / рабочий default
маршрутизируй через `1user-truth`: он выбирает owner в root-инструкциях,
`_ops/criteria/`, roadmap или task-file.

Moment layer включай по риску, а не как ритуал: `1before-work` при
нетривиальном старте или unclear branch, `1before-write` перед substantive
Edit/Write, `1work-review` перед closeout или когда есть criteria/evidence.

Начало работы в repo/project, новый проект, отсутствующая базовая
shape-структура или вопрос “какой skill брать?” → `1start-here`.

Task filenames, task scope и acceptance criteria живут в `1task-contract`;
task-файл обязан ссылаться на применимые `_ops/criteria/*.md`. Unresolved
approach branches / domain prerequisites / missing-middle questions — в
`1strategy-discussion`.

Instruction/runtime слой: вопрос “куда положить правило/механизм” сначала
идёт в `1instruction-layer`. Уже выбранная skill-работа идёт в
`1skill-architect`; уже выбранная runtime/folder/tooling работа идёт в
`1repo-shape`.

`knowledge/` — основной input-layer: перед созданием или правкой skill / agent /
instruction file начинай с ближайшего `wisdom-*` и одного guide/practical guide.

`_ops/plans/**` — эфемерная execution surface; создавай лениво только под
активную сложную задачу и не используй как source of truth.

Новый проект или отсутствующий `_ops` work-shape не собирать руками. Запускай
`python3 /Users/triton/.codex/skills/1start-here/scripts/init_project_shape.py <repo-root>`;
он создаёт `README.md`, `_ops/PROJECT-ROADMAP.md`, `_ops/criteria/` и
`_ops/plans/` без перезаписи существующих файлов.

GitHub/push workflow читать через `_ops/criteria/git-backup-workflow.md`:
GitHub здесь — backup локального `main`, а не branch/PR collaboration flow.

## Язык

Главное правило: с пользователем писать и разговаривать только на русском, если
он явно не попросил другой язык.

Сложные программистские вещи объясняй простым русским языком. Английский
оставляй для кода, команд, API, имён файлов, цитат и точных handles.

В планах, проектах и обсуждениях избегай программистского жаргона. Можно
использовать язык веб- и UI-дизайна: поверхности, тени, иконки, дизайн-система,
компоненты, вёрстка.
