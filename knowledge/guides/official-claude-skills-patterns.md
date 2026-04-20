# Official Claude Skills Patterns

Снимок на 20 апреля 2026.

Этот guide фиксирует, как Anthropic пишет Claude skills в официальных источниках.
Основан только на:
- Claude Help Center (`What are Skills`, `Use Skills in Claude`, `How to create custom Skills`)
- Claude Docs / Claude Code docs (`Agent Skills`, `Skill authoring best practices`, `Extend Claude with skills`)
- официальном репозитории `anthropics/skills`

Нужен не как общий канон по скиллам, а как опора по стилю и форме именно официального Claude corpus.

## Что Anthropic Говорит Напрямую

- Скилл должен решать **specific, repeatable task**, а не “всё подряд”.
- `description` — главный routing-signal: он должен говорить и **что делает скилл**, и **когда его вызывать**.
- Progressive disclosure — базовый механизм: metadata всегда в контексте, `SKILL.md` грузится при активации, большие детали живут в отдельных файлах.
- Практический ориентир для тела `SKILL.md` — **до 500 строк**, дальше лучше выносить в bundled files.
- Scripts, reference files и examples — нормальная часть скилла, а не исключение.

## Что Делает Живой Официальный Корпус

- Просмотрено 17 официальных `SKILL.md` в `skills/` плюс template.
- Frontmatter почти всегда минимальный:
  - обязательно `name`
  - обязательно `description`
  - часто `license`
- Корпус неоднородный по форме:
  - есть тонкие router-like skills
  - есть medium procedural skills
  - есть тяжёлые production-grade document skills
- Supporting files используются по-настоящему:
  - `scripts/`
  - `reference/` или language folders
  - `examples/`
  - `templates/`
  - `assets/` / bundled resources

## Длина

- `SKILL.md` по строкам:
  - минимум: 32
  - медиана: 236
  - среднее: 236
  - максимум: 590
- Распределение:
  - `<=100` строк: 6 skills
  - `101-250`: 3 skills
  - `251-500`: 7 skills
  - `>500`: 1 skill
- Document skills (`docx`, `pdf`, `pptx`, `xlsx`) заметно длиннее:
  - среднее: 357 строк
- Остальной корпус:
  - среднее: 199 строк

### `description`

- длина `description` в живом corpus:
  - минимум: 204 chars
  - медиана: 324 chars
  - среднее: 423 chars
  - максимум: 945 chars
- Практический вывод:
  - официальные skills часто используют **длинный trigger-heavy `description`**
  - routing clarity важнее декоративной краткости

## Повторяющиеся Формы

Частые каркасы тела `SKILL.md`:

- `Overview`
- `Quick Start` или `Quick Reference`
- workflow / decision tree / stages / phases
- `Reference Files`
- `Dependencies`
- явные команды и snippets
- anti-pitfall блоки вроде `Common Pitfalls`, `CRITICAL`, `ALWAYS`, `NEVER`

Типовые рабочие формы:

- **Тонкий router**
  - пример: `skills/internal-comms/SKILL.md`
  - суть: определить тип задачи → загрузить нужный example/reference → следовать ему

- **Procedural guide**
  - пример: `skills/webapp-testing/SKILL.md`
  - суть: quick path, decision tree, helper scripts, common pitfall, reference files

- **Heavy production skill**
  - примеры: `skills/docx/SKILL.md`, `skills/pptx/SKILL.md`, `skills/xlsx/SKILL.md`
  - суть: много operational detail, команды, QA loop, gotchas, scripts

- **Meta-skill**
  - примеры: `skills/claude-api/SKILL.md`, `skills/skill-creator/SKILL.md`
  - суть: branching logic, subcommands, reading guide, eval loop, reference hierarchy

## Какие Слова Они Выбирают

Корпус тяготеет к operational vocabulary:

- `use`
- `create`
- `read`
- `run`
- `load`
- `check`
- `verify`
- `trigger`
- `always`
- `never`
- `critical`

Это важный сигнал:
- официальный Anthropic style — не “описать тему”, а **сказать модели, что делать**
- даже creative skills остаются procedural, просто с другим словарём: `philosophy`, `bold`, `distinctive`, `craftsmanship`, `memorable`

## `description`: Как Пишет Официальный Корпус

Частые формулы:

- `Use this skill whenever ...`
- `Use when ...`
- `Trigger whenever ...`
- `Do NOT use when ...`
- перечисление trigger phrases, file types, deliverables, adjacent cases

Наблюдение:
- в theory/docs есть рекомендация писать аккуратно и кратко
- в live corpus Anthropic регулярно пишет **длинные, плотные, trigger-rich descriptions**
- `description` работает как routing contract, а не как label

## Naming

Anthropic docs рекомендуют консистентный naming и склоняются к gerund-form, но живой corpus это не абсолютизирует.

В официальном repo много имён другого типа:

- `brand-guidelines`
- `claude-api`
- `skill-creator`
- `theme-factory`
- `mcp-builder`

Вывод:
- gerund — полезная рекомендация, но не обязательный стиль
- важнее, чтобы имя было ясно обсуждаемым и не слишком общим

## Полезные Расхождения Между Docs И Corpus

- Help-style материалы местами звучат более “простыми” и консервативными.
- Live repo показывает, что на практике Anthropic допускает:
  - длинные `description`
  - тяжёлые `SKILL.md` для production задач
  - сильную procedural жёсткость
  - tool-like naming, а не только gerund naming

Поэтому при авторстве полезно держать два слоя отдельно:
- **Documented**: что Anthropic рекомендует
- **Observed**: как Anthropic реально пишет в официальном corpus

## Durable Takeaways

- Сначала оптимизировать **discovery**, потом красоту текста.
- `description` должен быть trigger-rich и не стесняться перечислять реальные surface signals.
- `SKILL.md` полезно строить как navigation + playbook, а не как длинную энциклопедию.
- Quick reference, decision tree и явные команды — типичный официальный паттерн.
- Большой скилл нормален, если он распилен по файлам и не тащит всё в ядро.
- Scripts и validation loops — нормальный способ сделать скилл устойчивее.
- Naming должен быть ясным и обсуждаемым; gerund — рекомендация, не догма.
