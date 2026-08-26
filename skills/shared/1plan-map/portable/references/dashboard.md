# The owner's dashboard (Obsidian)

The owner follows the project through the dashboard, not the files. When a map is created, the dashboard
is created at once; on any later map edit a missing file is created from the
template, while existing files are **never overwritten** — project views
live in them. The dashboard's home is the folder above the map root. It is
the owner's surface: file names, headings and view names stay in the owner's
language. Dashboards read frontmatter only.

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

`Планы.base` — tasks by their own files (`Прогресс` reports checklist
progress of the current subtask list, never task closure; the epic table's
`Задачи` is an inventory of created JIT files, not a completion fraction):

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

`Дашборд.md` — the owner's single screen, embedding the views:

```markdown
# 🚀 <project name> — путь к цели

<one or two lines: the status legend and what the ✅ bar means>

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

Project views and columns are added in these same files. Hyphenated property
names in formulas are addressed as `note["имя-с-дефисом"]` — a bare name
parses as subtraction.
