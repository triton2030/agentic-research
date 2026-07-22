---
description: "Deep audit root/subtree instruction topology: owner, duplicate, placement и hot path."
read-when: "Спорны root vs subtree, duplicate/drift или структура набора instruction files."
---

# Размещение И Структура Instruction Files

Playbook: каждое правило лежит у правильного owner-а, дети не повторяют корень,
а форма инструкции соответствует live runtime/repo. Это **структурный** аудит инструкций, не
смысловой (смысл и критерии — `audit-meaning-criteria.md`). Линзы качества языка
тянутся из `language-quality-audit.md`.

В audit/review mode вернуть findings и recommended repair без edits. Шаги
починки ниже исполнять только в change/fix mode.

## Что проверяет

1. **Правильная папка / owner.** Каждое правило — у того, кто реально владеет
   зоной? Папочное правило живёт в своей папке, не в корне; корневое — в корне,
   не размазано по детям. Effective chain и owner gate задаёт `SKILL.md`.
2. **Дети не повторяют корень.** Папочный `AGENTS.md` повторяет правило, которое
   уже сказано в корневом? Это второй source of truth или потраченный бюджет
   внимания. Допустимо только как **осознанная свежесть** (тот же смысл в другом
   моменте работы), не как копия в другом слое хранения.
3. **Формат, порядок, структура.** Hot-path сверху, редкое — в project-owned
   cold surface по ссылке, секции существуют только когда меняют решение.
   Runtime-specific loading и size guidance проверяй через discovery reference,
   а не превращай в универсальный Markdown law.

## Протокол

1. **Инвентаризация.** Собери затронутые instruction files и прочитай root +
   relevant subtree. Известные files читай напрямую; literal refs/duplicates
   передай `1cli-tools`. Если exact evidence недостаточно, выбери следующий
   owner через routing в `cli-recipes.md`.
2. **Owner каждого правила.** Для каждого правила — чья это зона? Не та папка →
   пометь move. Форма контейнера спорна (нужен ли вообще отдельный файл, split/
   merge) → сначала `1ia-audit`, не закрепляй плохую IA текстом.
3. **Root↔child дубль.** Сначала direct read и exact packet от `1cli-tools`; для
   semantic spread передай discovery в `1md-navigator` и прими его results
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

## Findings — формат

Каждая находка через именованный режим + recommendation: move к owner / сжать до
ссылки / заострить как SoT / перестроить структуру / оставить как осознанная
свежесть. «Звучит плохо» — вкус, не finding. Рекомендуй один repair; спрашивай
только при материальной развилке по risk/scope/reversibility.

## Выход

- Каждое правило у правильного owner-а (в audit mode — repair назван; в change
  mode — scoped move сделан).
- Root↔child дубли сняты или явно оправданы свежестью.
- Форма по шаблону; hot-path сверху; длинная база и cold-path вынесены со ссылкой.
- Closeout-проверки зелёные или deferred явно.
