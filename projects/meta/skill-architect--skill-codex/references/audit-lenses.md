# Audit Lenses

Линзы применяются **по ходу 8 шагов**, не как отдельный шаг. Капаbility reality используется в Шаге 2; human navigation и legibility — в Шагах 2, 4, 7; trace audit — в Шаге 1 если есть direct trace.

## Reality Lenses — Применяются В Шаге 2 (As-is Map)

- `Capability reality`
  Совпадает ли instruction text с реально установленными skills / tools / hook or validator where the runtime supports its or validators where the runtime supports them / MCP? Текст говорит «skill X существует» — реально установлен? hook or validator where the runtime supports it в `config/instruction files` с тем matcher'ом, что написан? Mismatch — это failure, не тихий pass.

- `Capability visibility`
  Даже если capability реально установлена — знает ли о ней новая сессия и живой пользователь? Installed ≠ discoverable. Hook, о котором никто не знает, = архитектура через удачу.

## Navigation Lenses — Применяются В Шагах 2, 4, 7

Два пользователя навигируют систему: живой человек и свежая AI-сессия. Оба должны понять структуру без знания лора.

- `Human navigation`
  Живой пользователь за минуту находит нужное? Имена папок и файлов предсказуемы? Иерархия отражает доменную модель, а не историю проекта? Если пользователь постоянно делает `grep` по репо — topology проигрывает.

- `Fresh-session navigation`
  Свежая AI-сессия поймёт, что читать первым, где истина, как здесь принято работать? Поймёт без 10 context-injection hook or validator where the runtime supports its or validators where the runtime supports them?

- `Precedence clarity`
  При конфликте правил ясно, какой файл важнее? Корневой `AGENTS.md` vs локальный? Глобальный `CLAUDE.md` vs project? Если не ясно — drift.

- `Truth routing`
  Понятно, что живёт в `_ops/`, что в корневых инструкциях, что в `knowledge/`, что в project-local skill? Если truth layer размазан по 5 местам — каждый раз лотерея.

- `Progressive disclosure`
  Разделены metadata, ядро инструкции, `references/`, `scripts/`? Или в одном месте слишком много и новая сессия теряет главное под шумом?

## Legibility Lenses — Применяются В Шаге 4 (Failure Classes)

- `Траектория текущего чата`
  Что уже показало реальное поведение модели в этой сессии: shortcuts, missed reads, слабые выводы, drift, ненужные вопросы, плохой route, падение качества.

- `Поведение по умолчанию`
  Поймёт ли модель, **когда** писать файлы, когда обсуждать, когда верифицировать, когда вызывать skill или tool? Если нет default — каждая сессия угадывает.

- `Drift и противоречия`
  Где слои спорят между собой, дублируют друг друга, оставляют dangerous gaps? Дублирование = источник drift.

## Pressure Lenses — Применяются В Шаге 7 (Minimize Pass)

- `Ещё живое?`
  Служит ли правило своему backlink'у сейчас? PROJECT-ROADMAP сдвинулся, а правило осталось — archaeology-кандидат.

- `Overlap`
  Два правила на одну проблему — один owner или compose layer, не три параллельных.

- `Chesterton's fence`
  Если убрать — что сломаю? Не могу объяснить — не трогаю.

## Decision Lenses — Применяются В Шагах 5-6 На Каждой Prescription

Качество решения внутри шага. Прогоняй каждую prescription через эти линзы перед тем, как включить её в output.

- `Reversibility`
  One-way door или two-way? Форма папок, удаление ownership, миграция структуры данных — one-way, порог тщательности высокий. Hook или правило в CLAUDE.md — two-way, дешевле попробовать и откатить. Не путай: «легко внести» ≠ «легко откатить». *(Bezos — one-way vs two-way doors.)*

- `Blast radius`
  Что случится, если сам guard сломается? Хук падает → блокирует всю сессию? Правило ссылается на несуществующий файл → все следующие сессии ошибаются? Чем шире blast radius, тем выше требования к тестированию и fallback'у.

- `Owner clarity`
  Одно правило живёт в **одном** месте, не в трёх. Если одну и ту же политику прописал AGENTS.md, CLAUDE.md и skill — каждый rewrite ломает два из трёх. При конфликте ownership очевиден: корень > локальный, runtime > prompt, явный owner > implicit.

- `Simplicity under pressure`
  Выдержит ли prescription через 6-24 месяца, или разваливается под первой названной силой? Проверка: возьми одну из Forces (Шаг 3) и мысленно примени к prescription — она всё ещё работает, или превращается в archaeology? Если второе — либо переформулируй, либо явно назови sunset signal этой силой.

## Trace Audit — Применяется В Шаге 1 Если Есть Direct Trace

Текущий чат содержит полезные сигналы:
- Смотрю не только на финальный ответ, но на траекторию.
- Отмечаю, где модель пропустила очевидный источник истины.
- Отмечаю, где выбрала более короткий, но более слабый путь.
- Отделяю единичный промах от повторяющегося failure pattern.
- Использую эти сигналы как evidence для prescriptions, а не как повод переписать ответ.

## Как Применять В Аудите

1. В Шаге 2 прохожу **Reality + Navigation** линзами — что есть, видно ли это, как устроена topology.
2. В Шаге 4 прохожу **Legibility** линзами — где сбои читаются.
3. В Шаге 7 прохожу **Pressure** линзами — что можно удалить.
4. Trace audit — по ситуации в Шаге 1, если диалог даёт evidence.

Не применяй линзу, которая не меняет prescription. EVPI работает и здесь.
