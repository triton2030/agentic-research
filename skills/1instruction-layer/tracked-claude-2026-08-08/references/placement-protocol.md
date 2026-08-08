# Размещение И Структура — Протокол И Выход

Открывается из [`audit-placement-structure.md`](audit-placement-structure.md).

## Протокол

1. **Инвентаризация.** Собери затронутые instruction files и прочитай root +
   relevant subtree. Известные files читай напрямую; literal refs/duplicates
   передай `1cli-tools`. Если exact evidence недостаточно, выбери следующий
   owner через routing в `cli-recipes.md`.
2. **Owner каждого правила.** Для каждого правила — чья это зона? Не та папка →
   пометь move. Форма контейнера спорна (нужен ли вообще отдельный файл, split/
   merge) → сначала `1ia-audit`, не закрепляй плохую IA текстом.
3. **Root↔child дубль.** Сначала direct read и exact packet от `1cli-tools`; для
   semantic spread передай discovery в `1md-search` и прими его results
   только как candidates до чтения bodies.
   Содержательно одинаково → один owner + pointer; расходится → drift; разный
   момент работы → conscious freshness, если owner остаётся один.
4. **Структура файла.** Hot path держи сверху; rare depth переноси в
   project-owned cold owner только с условным pointer. Не навязывай чужому repo
   конкретные README/GOAL/`_ops` conventions. Язык — через
   `language-quality-audit.md`.
5. **Правка — только change mode.** Move правила к owner-у; сжать дубль до
   ссылки; перестроить порядок/формат. Если target участвует в graph, передай
   cascade/anchors в `1md-graph`.
6. **Closeout — только после edits.** Direct diff/read всегда; project-owned
   graph/link check — по реальному риску. Не требуй `md` в repo, где он не
   является live owner tool.

## Выход

- Каждое правило у правильного owner-а (в audit mode — repair назван; в change
  mode — scoped move сделан).
- Root↔child дубли сняты или явно оправданы свежестью.
- Форма по шаблону; hot-path сверху; длинная база и cold-path вынесены со ссылкой.
- Closeout-проверки зелёные или deferred явно.
