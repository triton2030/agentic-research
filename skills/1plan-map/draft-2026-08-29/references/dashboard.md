# The owner's dashboard (Obsidian)

The owner follows the project through the dashboard, not the files. When a map
is created, the dashboard is created at once; on a later map edit a missing
file is created from the template, while existing files are never overwritten
because project views live in them. The dashboard lives above the map root;
names and headings stay in the owner's language. Dashboards read frontmatter
only.

`Дашборд.base` — epics:

```yaml
filters:
  and:
    - file.inFolder("<map root folder>")
formulas:
  Задачи: >-
    note["задач-готово"].toString() + "/" + note["задач"].toString()
    + " созданных"
views:
  - type: table
    name: По порядку
    filters:
      and:
        - тип == "эпик"
        - запуск == true
    order:
      - порядок
      - file.name
      - описание
      - статус
      - health
      - задачи
      - formula.Задачи
      - зависит-от
    sort:
      - property: порядок
        direction: ASC
  - type: table
    name: Затыки
    filters:
      and:
        - тип == "эпик"
        - статус == "🛑 затык"
    order:
      - file.name
      - критерий
  - type: table
    name: Отложенное
    filters:
      and:
        - тип == "эпик"
        - статус == "⏳ отложено"
    order:
      - file.name
      - область
      - критерий
```

`Планы.base` — tasks. `Прогресс` reports the current subtask list, never task
closure; epic `Задачи` is created-file inventory, not a completion fraction.

```yaml
filters:
  and:
    - file.inFolder("<map root folder>")
    - тип == "задача"
formulas:
  Прогресс: >-
    if(note["подзадач"] > 0,
    ((note["подзадач-готово"] / note["подзадач"]) * 100).round().toString()
    + "%", "—")
views:
  - type: table
    name: Живые задачи
    filters:
      and:
        - статус != "✅ готово"
    order:
      - file.name
      - эпик
      - статус
      - режим
      - порядок
      - formula.Прогресс
      - обновлено
    sort:
      - property: эпик
        direction: ASC
      - property: порядок
        direction: ASC
  - type: table
    name: Завершённые задачи
    filters:
      and:
        - статус == "✅ готово"
    order:
      - file.name
      - эпик
      - статус
      - режим
      - порядок
      - formula.Прогресс
      - обновлено
    sort:
      - property: эпик
        direction: ASC
      - property: порядок
        direction: ASC
```

`Дашборд.md` — the owner's single screen:

```markdown
# 🚀 <project name> — путь к цели

<one or two lines: status legend and what the ✅ bar means>

## 🗺️ Путь по порядку

![[Дашборд.base#По порядку]]

## 📋 Живые задачи

![[Планы.base#Живые задачи]]

## ✅ Завершённые задачи

![[Планы.base#Завершённые задачи]]

## 🛑 Где затык

![[Дашборд.base#Затыки]]

## ⏳ Отложенное

![[Дашборд.base#Отложенное]]
```

Project views and columns are added in these same files. Hyphenated properties
use `note["имя-с-дефисом"]`; a bare name parses as subtraction.
