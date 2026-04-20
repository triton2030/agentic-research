# Агентные Инструкции

## Назначение

База — для авторства скиллов, агентов, промптов и инструкционных файлов для Claude Code, Codex и подобных платформ. Не для написания агентов с нуля кодом (Python-пайплайны, KV-cache реализация, sandbox-инфра, RDF-онтологии).

При триаже внешних источников: брать только мудрости, применимые к авторству. Кодовые детали runtime — пропускать. Если принцип ценный, но изложен на коде, переформулировать на языке авторства (skill, system prompt, instruction file).

## Структура

- Три домена в корне: `knowledge/`, `projects/`, `ops/`
- `knowledge/` — все общие выводы, гайды, референсы, категорийные данные
- `projects/` — только проектные папки (agent, skill, plugin) по категориям
- `ops/` — операционный слой: задачи, планы, learnings, inbox
- Корневые файлы: `AGENTS.md`, `CLAUDE.md`

## knowledge/

- В корне `knowledge/` только:
  - `wisdom-agents.md`
  - `wisdom-skills-plugins.md`
  - `wisdom-LLM.md`
  - `wisdom-codex.md`
  - `wisdom-claude-code.md`
  - `wisdom-systems-thinking.md`
- `knowledge/practical-guides/` — короткие практические гайды в `kebab-case`
- `knowledge/guides/` — плоский слой для `perfect-*`, `*-playbook.md` и `official-*-patterns.md`
- Короткие операционные сравнения и platform memos держать в `knowledge/practical-guides/`, не в `knowledge/guides/`
- `knowledge/examples/` — эталонные артефакты из дикой природы (`{slug}/` + `takeaways.md`)
- `knowledge/research/{business,design,dev,meta}/` — категорийные данные:
  - `learnings.md`
  - `links-knowledge.md`
  - `links-tools.md`
  - `inventory-claude-code.md`
  - `inventory-codex.md`
- Новые подпапки в `knowledge/guides/` не создавать
- Новые файлы и подпапки в `knowledge/research/{category}/` не создавать

## projects/

- Проектная папка создаётся только для `agent`, `skill`, `plugin`
- Путь: `projects/{category}/{name}--{type}-{platform}/`
- `category`: `business` | `design` | `dev` | `meta`
- `type`: `agent` | `skill` | `plugin`
- `platform`: `codex` | `claude-code`
- `name`: `kebab-case`
- Пустые проектные папки не создавать
- У проектной папки должен быть `README.md`
- `README.md` в проектной папке — только короткий входной файл, не длинное объяснение

## ops/

- `ops/learnings.md` — компактная project memory (до 100 строк)
- `ops/plans/plan-YYYY-MM-DD-slug.md` — планы скилла `ops`
- `ops/inbox/` — временный лоток для входящих эталонов (см. «Входящие Артефакты»)
- `ops/ROADMAP.md`, `ops/TASKS.md`, `ops/ISSUES.md`, `ops/NORTH-STAR.md` — направление и состояние работы

## Минимальный След

- По умолчанию новые файлы не создавать
- Не создавать вспомогательные документы, лишние `README`, explainers, summaries, handoff notes, планы, аудиты и другие побочные файлы, если пользователь этого не просил
- Не писать в файлах то, чего пользователь прямо не просил
- Не добавлять текст "на всякий случай", "для полноты", "на будущее" или "чтобы было понятнее"
- Сначала обновлять существующий правильный файл, а не заводить новый
- Каждый новый файл и каждый лишний абзац считать будущим хрупким местом, которое может устареть и навредить
- Если без нового файла или дополнительного блока совсем нельзя, делать минимально: только то, что нужно для задачи, максимально коротко, без повторов и лишних объяснений

## Куда Что Класть

- Общие выводы для любых агентов, скиллов, LLM или платформ → `knowledge/` (wisdom-*.md)
- Короткие практические гайды и операционные сравнения → `knowledge/practical-guides/`
- Эталонные шаблоны, playbooks и source-backed official corpus studies → `knowledge/guides/`
- Эталонные артефакты из дикой природы → `knowledge/examples/`
- Мысли, выводы, ссылки по категории → `knowledge/research/{category}/`
- Новый агент, скилл, плагин → `projects/{category}/{slug}/`
- Задачи, проблемы, приоритеты → `ops/`
- Свежие входящие эталоны до триажа → `ops/inbox/`

## Входящие Артефакты

- `ops/inbox/` — временный лоток, не живёт дольше одного ops-триажа
- Для каждого артефакта из inbox:
  - уроки поднимаются в релевантный `knowledge/wisdom-*.md` или `knowledge/guides/perfect-*.md`
  - если артефакт — эталон, который хотим видеть живым: копия в `knowledge/examples/{slug}/` + `takeaways.md` на одну страницу (что ценного + где цитируется)
  - иначе удалить из inbox
- `slug` — по источнику, `kebab-case`
- В `examples/{slug}/` — только инструктивные/эталонные файлы, без побочного шума
- Каждый эталон должен быть процитирован хотя бы в одном `perfect-*.md` или `wisdom-*.md` — иначе он не всплывёт

## Правило Продвижения

- Повторяемое знание для любых агентов и скиллов идёт в `knowledge/` (wisdom-*.md)
- Знание для одной категории остаётся в её `knowledge/research/{category}/`
- Устойчивое правило по умолчанию для всей работы поднимается в `AGENTS.md` или `knowledge/guides/`

## Инвентарь

- Файлы: `inventory-claude-code.md`, `inventory-codex.md` в `knowledge/research/{category}/`
- Разделы: `Что Есть`, `Чего Не Хватает`
- Формат:

```md
### {название}
- Тип: agent | skill | plugin | коннектор
- Источник: наш | Anthropic | Figma | {другой}
- Что делает: {одно предложение}
```

- Только факты
- Одна запись = одна сущность
- Исследовательские заметки в инвентарь не писать

## Контекст

- Для системных промптов: `AGENTS.md` + `knowledge/guides/perfect-system-prompts.md` + `knowledge/guides/perfect-context-engineering.md`
- Для скиллов: `AGENTS.md` + `knowledge/guides/perfect-system-prompts.md` + `knowledge/guides/perfect-skills.md` + `knowledge/practical-guides/skill-authoring-checklist.md` + `knowledge/guides/perfect-context-engineering.md`
- Для Codex-скиллов: добавить `knowledge/practical-guides/codex-skills.md`
- Для Claude Code-скиллов: добавить `knowledge/practical-guides/claude-code-skills.md`
- Для инженерии контекста (любые агентные инструкции, CLAUDE.md, README для агентов): `knowledge/guides/perfect-context-engineering.md` + примеры из `knowledge/examples/`
- Для проектирования формы нового или существующего проекта (где живут типы артефактов, как роутить новое, по каким сигналам видно, что система ломается): `knowledge/guides/perfect-project-shape.md` + `knowledge/wisdom-systems-thinking.md`

## Перед Работой

- Перед любой нетривиальной работой сначала читать релевантный `knowledge/wisdom-*.md`
- Если неясно, какой `wisdom-*.md` релевантен, начинать с `wisdom-agents.md`
- Перед крупным проектом, новой подсистемой или когда чувствуешь tunnel vision внутри задачи — читать `knowledge/wisdom-systems-thinking.md`
- Также читать `ops/learnings.md`
- Перед созданием или изменением любого скилла всегда читать `knowledge/guides/perfect-skills.md` и `knowledge/practical-guides/skill-authoring-checklist.md`
- Перед созданием или изменением Codex-скилла всегда читать `knowledge/practical-guides/codex-skills.md`
- Перед созданием или изменением Claude Code-скилла всегда читать `knowledge/practical-guides/claude-code-skills.md`
- Перед работой в категории или в проектной папке сначала читать `knowledge/research/{category}/learnings.md`
- Для `projects/business/*` → `knowledge/research/business/learnings.md`
- Для `projects/design/*` → `knowledge/research/design/learnings.md`
- Для `projects/dev/*` → `knowledge/research/dev/learnings.md`
- Для `projects/meta/*` → `knowledge/research/meta/learnings.md`
- Если работа затрагивает несколько категорий, читать `learnings.md` каждой из них

## Правила Письма

- Писать как можно короче
- По умолчанию писать только запрошенное, не расширять объём без необходимости
- Не писать то, чего точно не знаем
- Не выдумывать новые разделы без необходимости
- Не добавлять разделы вроде "зачем это нужно", если без них можно обойтись
- Отделять факты от гипотез
- Имена проектных папок и обычных файлов — `kebab-case`
- `AGENTS.md`, `CLAUDE.md` в корне и рут-папки `knowledge/`, `projects/`, `ops/` — исключения из `kebab-case`
