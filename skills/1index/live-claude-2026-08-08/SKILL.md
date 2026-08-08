---
name: 1index
description: >
  Когда создаёшь, проектируешь, переделываешь, дополняешь, обновляешь или
  аудируешь корневой `INDEX.md`, строй карту «намерение → что читать и зачем»
  из live goals, Founder-backed future work и repeated tasks — прежде всего
  маршруты к информации, лежащей не там, где очевидно, вплоть до раздела внутри
  файла; не дерево файлов и не вторая truth. Root instruction pointer входит в ход. Known-corpus
  reading → `1md-read`; semantic discovery → `1md-search`; docs-system →
  `1document-system`.
---

# Intent Index

## Результат

Создай в корне проекта короткий `INDEX.md`, который отвечает:
«что читать для этой задачи, в каком порядке и зачем».

Корневая добродетель — **маршрутизировать намерения, а не файлы**. Главный
груз INDEX — дельта между ожиданием и реальностью: важная информация, которая
лежит не там, где её станет искать cold-start agent, вплоть до раздела внутри
файла — не «какие файлы есть», а «какая информация в каком файле и разделе
живёт». В этом INDEX — handoff будущей сессии от прошлых. При этом он остаётся
неполным navigation cache: linked owners сохраняют всю truth, а miss не
доказывает отсутствие информации.

## Default Path

1. **Восстанови surface и режим.** Прочитай effective project instructions,
   существующую root-навигацию, current goal и ближайших execution owners.
   Audit/review остаётся read-only; change/fix разрешает scoped edits.
   Эквивалентный intent-router обновляй вместо второго INDEX. Известный
   многофайловый corpus читай через `1md-read`, неизвестный semantic target ищи
   через `1md-search`, известный короткий target — напрямую. Retrieval mechanics
   здесь не повторяй.
2. **Добудь candidate intents.** В порядке силы используй:
   явные слова Founder о ближайшей работе; live GOAL/task/roadmap/backlog;
   повторявшиеся recent tasks и retrieval friction. Agent-only prediction —
   гипотеза, не основание секции. Если доступное evidence не раскрывает
   material future intent, задай один discriminating question вместо
   выдумывания.
3. **Допусти только устойчивое.** Intent входит, если он явно назван Founder
   для будущей работы, живёт у current owner либо повторился хотя бы дважды.
   Не допускай file categories, одноразовые действия, speculative future и
   разделы, которые обычная root-навигация восстанавливает с той же стоимостью.
   Default compactness budget — 3–12 intents; это сигнал pruning, не закон
   предметной области.
4. **Собери reading set из неожиданного.** Для intent назови job, aliases и
   прежде всего те links, которые cold-start agent не восстановит надёжно с
   сопоставимым усилием: информация в неочевидном файле или разделе. Ссылок
   может быть много — лимит задаёт очевидность, не количество. Указывай section
   anchor, когда нужен участок файла, а не файл целиком. Упорядочивай по
   важности для задачи; при равной важности —
   `constraint → decision/owner → implementation/evidence`. К каждой ссылке дай
   короткое действие — что там узнать, увидеть или сделать, — не пересказ
   содержания. Папку, tool или skill добавляй лишь когда без них следующий ход
   неполон.
5. **Запиши router.** Используй root `INDEX.md`, если local contract не назначил
   существующий эквивалент. Соблюдай local language, metadata и link rules;
   не изобретай `authority` fields. Обычные Markdown links обязательны для
   graph validation. Exact compact schema и пример — в
   [index-contract.md](references/index-contract.md).
6. **Сделай INDEX достижимым.** В effective root instruction chain каждого
   поддерживаемого runtime оставь один pointer и event-driven freshness rule.
   Если один instruction owner уже импортируется другим, меняй только owner.
   Неясное placement или конфликт instruction layers → `1instruction-shaping`.
7. **Обслуживай по событиям.** INDEX меняется, когда owner/path/anchor,
   reading order или состав существующего set изменились, admitted intent
   появился/исчез, либо по ходу работы важная информация нашлась в неожиданном
   месте — занеси такой route в той же authorized работе: это и есть handoff. Обычное изменение owner content INDEX не затрагивает, пока
   маршрут остаётся верным. В authorized change исправь scoped stale route в
   той же работе; в read-only назови finding и продолжи через live navigation.
   Dirty worktree проверяй по точному target: не перезаписывай пересекающиеся
   чужие edits, но unrelated dirt сам по себе не veto.
8. **Докажи полезность.** Проверь changed Markdown локальным lint owner-ом,
   links/anchors через `1md-graph` и не менее пяти representative intents:
   hit даёт достаточный set; miss и битая ссылка безопасно падают в live
   navigation; ни одна строка не стала project truth.

## Инварианты

- INDEX не заявляет полноту и не заменяет owner discovery перед material
  substantive change.
- Разрешены intent, aliases, reading order, links и короткое действие ссылки
  (что там узнать, увидеть или сделать).
  Status, decision, numeric value, policy, product promise и rationale живут
  только у linked owner.
- Изменение содержания owner-а не требует синхронизации, если маршрут не
  изменился.
- Новый раздел должен экономить повторяемый discovery, а не документировать
  существование папки.

## Routes

- Schema, admission tests и instruction pointer:
  [index-contract.md](references/index-contract.md).
- Missing/conflicting truth owner или docs topology → `1document-system`.
- Root instruction wording/placement → `1instruction-shaping`.
- Link, anchor, move, merge, rename или delete impact → `1md-graph`.
- Markdown style/syntax после edit → `1md-lint`.

## Stop

Не создавай INDEX, если уже есть эквивалентный live router, evidence даёт только
дерево файлов либо работа требует угадать material business truth. В последнем
случае исключи только затронутую секцию и закончи независимый router. Не
расширяй ход до рефактора документационной системы, owner migration или
исправления всех найденных документов.
