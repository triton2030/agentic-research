# Claude Code Skills

Короткий практический гайд по созданию скиллов под Claude Code.
Для общих принципов — `knowledge/guides/perfect-skills.md`.
Для того, как официальный Anthropic corpus реально пишет Claude skills — `knowledge/guides/official-claude-skills-patterns.md`.
Для постоянной короткой памятки — `knowledge/practical-guides/skill-authoring-checklist.md`.
Для Codex-специфики — `codex-skills.md`.

## Главное Правило

Скилл может быть сколь угодно большим по знаниям и контексту, **если он разложен по файлам**.

Claude Code грузит скилл в три уровня (progressive disclosure):
1. **Метаданные** (`name` + `description`) — всегда в контексте. На практике это полноценная routing-поверхность; у Anthropic `description` часто длинный и trigger-heavy.
2. **Тело `SKILL.md`** — грузится, когда скилл сработал, ≤500 строк.
3. **Бандл (`references/`, `scripts/`, `assets/`)** — подтягивается по ссылке из `SKILL.md`, лимита нет.

Поэтому тяжёлый материал не урезается — он выносится в `references/` и подключается по ссылке. Скилл остаётся лёгким в холодном состоянии и раскрывается вглубь только тогда, когда нужен.

## Структура

```text
skill-name/
├── SKILL.md        # обязательный, тонкий
├── references/     # длинные справочники, примеры, контракты вывода
├── scripts/        # детерминированные исполняемые операции
└── assets/         # файлы, идущие в результат (шаблоны, иконки, шрифты)
```

Создавать только те подпапки, которые реально нужны. `agents/openai.yaml` — не для Claude Code.

## Что Держать В `SKILL.md`

- frontmatter: `name`, `description`
- быстрый вход: `Overview`, `Quick Start` / `Quick Reference` или decision tree, если это помогает
- когда использовать
- когда не использовать
- какой контекст нужен на входе
- основной рабочий ход
- развилки и компромиссы
- `done when`
- ссылки на `references/`, `scripts/`, `assets/` с указанием, когда их читать

Тонкое тело обязательно. Приближаешься к 500 строкам — выноси детали в `references/` и оставляй чёткий указатель.

## Что Выносить В `references/`

- длинные примеры хороших и слабых ответов
- точный output contract и форматы
- red flags и anti-bypass правила
- доменные справочники (по одной теме на файл)
- крупные таблицы вариантов

Для длинных reference-файлов (>100 строк) — давать table of contents в начале.

## Мульти-домен

Если скилл обслуживает несколько доменов или фреймворков, организуй по вариантам:

```text
cloud-deploy/
├── SKILL.md            # workflow + выбор варианта
└── references/
    ├── aws.md
    ├── gcp.md
    └── azure.md
```

Claude читает только тот файл, который нужен под текущую задачу.

## `description` — Главный Триггер

- Это единственный сигнал, по которому Claude решает вызывать скилл.
- Писать конкретно: и что делает, и когда использовать.
- Claude чаще не триггерит, чем перетриггеривает — формулировка должна быть слегка «настойчивой»: перечислять триггерные фразы, типы задач и контексты.
- В официальном Anthropic corpus описание часто строится как routing contract: `Use this skill whenever ...`, `Trigger when ...`, `Do NOT use when ...`.
- Не оптимизировать описание под искусственную сверхкраткость. Практический ориентир — discovery quality и актуальные platform limits, а не старые короткие примеры из help-статей.
- Для двуязычного репо добавлять и английские, и русские формулировки триггеров.
- Описание обновлять каждый раз, когда меняется набор ситуаций, в которых скилл должен срабатывать.

## Что Видно По Официальному Corpus Anthropic

- Официальный corpus допускает и очень тонкие router-skills, и тяжёлые production-skills. Хорошая форма зависит от класса задачи, а не от догмы “всегда коротко”.
- Частый каркас: `Overview` → `Quick Start` / `Quick Reference` → workflow / decision tree → `Reference Files` / `Dependencies`.
- Quick reference, команды, QA loop и anti-pitfall формулировки (`CRITICAL`, `ALWAYS`, `NEVER`) — нормальный официальный паттерн, а не “слишком жёсткий тон”.
- Gerund naming полезен, но не обязателен. В живом Anthropic repo много tool-like имён (`brand-guidelines`, `claude-api`, `skill-creator`).

## Lean Installed Version

В установленной версии скилла — только то, что реально нужно модели:
- `SKILL.md`
- `references/`, `scripts/`, `assets/` — если используются

Не класть в installed version:
- `README.md`
- `CHANGELOG.md`
- `QUICK_REFERENCE.md` и прочий human-doc шум

Документацию для человека держать в проектной папке репо, не в установленном скилле.

## Тип Скилла

Скилл сам должен сообщать тип:
- **Rigid** (TDD, debugging, screenshot-audit) — следовать точно.
- **Flexible** (паттерны, дизайн) — адаптировать к контексту.

## Чего Не Делать

- Не раздувать `SKILL.md` в длинную статью.
- Не дублировать материал в `SKILL.md` и `references/`.
- Не класть в installed skill README и changelog.
- Не делать скилл «про всё сразу» — одна работа на скилл.
- Не пытаться Read-ом открыть `SKILL.md` — это обходит механизм загрузки Skill tool.
- Не использовать Codex-специфику (`agents/openai.yaml`, `$skill-name`) в Claude Code скилле.

## Установка

- Глобально для всех проектов — ставить в плагин `my-skills` (`~/.claude/marketplaces/my-skills/skills/<name>/`) и синхронизировать с кэшем.
- Локально для одного репо — `<repo>/.claude/skills/<name>/`.
- После установки обновлять `marketplace.json` и `plugin.json` (description, tags).
