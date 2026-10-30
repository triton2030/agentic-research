# skill-gallery

Мод Claude Code: боковая панель со списком скиллов и встроенных команд по разделам. Клик по имени
вставляет `/имя ` в поле ввода, звёздочка ведёт избранное. Избранное висит
и в строке над полем ввода, там же `☆ skills` открывает закрытую панель.
Свёрнутые разделы и избранное хранятся в `$.store` между сессиями.

## Установка

Папка — локальный магазин `skill-gallery-mods`, плагин стоит на уровне
пользователя: `skill-gallery@skill-gallery-mods`. Сессии читают его прямо
из `skill-gallery/` (проверено `claude plugin update` на 2.1.312), копия
в `~/.claude/plugins/cache/` не используется.

Правка доходит до сессии при её старте или после `/reload-plugins`.
Новая версия в `plugin.json` для этого не нужна.

## Хранилище

Избранное и свёрнутые разделы лежат в
`~/.claude/plugins/store/skill-gallery_skill-gallery-mods-<hash>.json`.
Хранилище привязано к источнику плагина: копия мода из
`~/.claude/dev-mods/` пишет в отдельный файл `skill-gallery_inline-*`.
Поэтому не держи копию в `dev-mods` рядом с установленным плагином:
после перезапуска сессии грузятся оба, и избранное расходится.
Правь эту папку и делай `/reload-plugins`.

## Проверка правки

```bash
claude plugin test experiments/skill-gallery/skill-gallery
```

```bash
claude plugin validate experiments/skill-gallery
```

API модов — встроенный скилл `plugin-authoring`, его `types/claude-code.d.ts`.
