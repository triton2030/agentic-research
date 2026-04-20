# Claude Code Plugins vs Free Skills

Короткая операционная памятка по packaging-разнице между свободными skills и plugin-skills в Claude Code.
Не канон по strategy и не playbook.
Повторяемые выводы про выбор слоя упаковки держим в `/knowledge/wisdom-claude-code.md` и `/knowledge/wisdom-skills-plugins.md`.

## Роль Файла

- Здесь только операционные различия: где что лежит, что видно в UI и что нужно для регистрации.

## Что Видит Модель И UI

**Свободные скиллы** — директории в `~/.claude/skills/<name>/SKILL.md`.
Дискаверятся по файловой системе, работают для модели, **не видны в UI** `/plugin`, без версий, без неймспейса, без источника поставки.

**Плагины** — пакуются через marketplace, регистрируются в конфиге. Видны и управляются через `/plugin`, имеют неймспейс `plugin:skill`, версию, источник и toggle вкл/выкл.

## Что Где Живёт

- `~/.claude/skills/<name>/` — свободные скиллы.
- `~/.claude/marketplaces/<marketplace>/` — локальные marketplace-директории. Внутри `.claude-plugin/marketplace.json` + `.claude-plugin/plugin.json` + `skills/` + `agents/`.
- `~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/` — плагины, установленные из GitHub-marketplace.
- `~/.claude/plugins/known_marketplaces.json` — реестр известных marketplace.
- `~/.claude/plugins/installed_plugins.json` — реестр установленных плагинов.
- `~/.claude/settings.json` — `enabledPlugins` и `extraKnownMarketplaces`.

## Минимальный Локальный Плагин

```text
~/.claude/marketplaces/<name>/
├── .claude-plugin/
│   ├── marketplace.json
│   └── plugin.json
├── skills/<skill>/SKILL.md
└── agents/<agent>.md
```

Регистрация плагина требует правок в `known_marketplaces.json`, `installed_plugins.json` и `settings.json`. После правок нужен рестарт сессии.

## Почему Свободный Скилл Не Виден в UI

UI `/plugin` оперирует плагинами как единицей учёта. Свободная директория в `~/.claude/skills/` не имеет manifest, источника и записи в `installed_plugins.json`, поэтому для UI её не существует, хотя модель её видит.

## Неймспейс В Списке Скиллов

Плагинные скиллы видны модели как `plugin-name:skill-name` (например, `my-skills:ops`). Свободные — без префикса (например, `ops`).

## Scope: User vs Project

- `scope: user` в `installed_plugins.json` — плагин доступен во всех проектах пользователя.
- `scope: project` + `projectPath` — только в конкретном проекте.
- Переопределение в проекте: `<project>/.claude/settings.local.json` с `enabledPlugins`.
