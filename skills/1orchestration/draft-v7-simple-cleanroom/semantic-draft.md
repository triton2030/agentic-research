# 1orchestration — simple clean-room semantic draft

Статус: смысловой candidate, не installed package. Zero-based решение — один
`SKILL.md` без references: у функции один короткий контракт, а дополнительное
дробление само стало бы нагрузкой.

## Short trigger-only description

> Use before assigning any subagent, or when splitting your own cognitively overloaded work.

## Минимальный русский body

### Цель

Перед поручением субагенту или разделением перегруженной работы преврати её в
current source-bound выполнимый контракт, сохранив критерии и owners без
добавления лишней оркестрации.

### Контракт

1. Root до brief читает все доступные current sources и inputs, способные
   изменить качество результата, и связывает каждый точный адрес с тем, что он
   меняет в outcome, `done_when`, authority или delta.
2. Brief задаёт конкретный outcome, полный наблюдаемый `done_when`, адреса всех
   влияющих sources/inputs и только отсутствующую в них delta; канонические
   правила не пересказываются, поэтому prompt не становится вторым owner-ом.
3. После готового brief посчитай feasible active set отдельно для выбранного
   actor и для следующего решения root: каждое независимо забываемое
   требование, знание или решение считается отдельно, capability actor-а тоже
   входит в feasibility; около 20 — мягкий сигнал, а split полезен лишь если
   конкретный участник может отбросить units.
4. Выбери минимальный способный route, включая `root делает сам` и
   `no delegation`; добавляй агент, стадию, файл или правило только если можешь
   назвать конкретный худший исход без этой сложности.
5. Root сохраняет общую траекторию и своё следующее решение, existing
   specialized controller сохраняет единственную topology и свой acceptance,
   а live runtime owner — authority над моделью, инструментами и исполнением.
6. Зависимая работа продвигается только после evidence по каждому критерию;
   process-report сам по себе не acceptance, а rework получает только
   недостающую delta и прежние source addresses, не пересказ канона.
7. Изменение upstream source, input или принятого решения делает затронутые
   части brief, feasibility и acceptance non-current; пересобери только их до
   следующего зависимого хода.

## Почему каждая runtime-строка осталась

| Строка | Counterfactual harm без неё |
| --- | --- |
| 1 | Root может приложить ссылки, не прочитав их, и сформировать brief раньше owner-правды; пропавший критерий станет невидимым. |
| 2 | Исполнитель получит либо неполную приёмку, либо длинный второй канон, который разойдётся с current sources. |
| 3 | Подсчёт до добавления prompt скроет реальную нагрузку; неподходящий actor или root next-decision останется перегруженным, а косметический split будет принят за полезный. |
| 4 | Оркестрация начнёт создавать агентов, стадии и файлы по умолчанию, усиливая именно ту нагрузку, которую должна снижать. |
| 5 | Generic delegate продублирует specialized controller либо portable skill присвоит изменчивые runtime-решения; root потеряет единственную сквозную траекторию. |
| 6 | Зависимый ход стартует по уверенно звучащему отчёту; возврат на доработку раздует prompt повтором уже существующих правил. |
| 7 | После upstream change старый brief и прежний pass продолжат выглядеть действующими и направят зависимую работу по отменённому основанию. |

## Active-unit count

Постоянный runtime-набор — **7 единиц body**. Description — router, а не
дополнительная рабочая инструкция. В конкретный момент активны:

| Момент | Единицы скила | Прибавляемые task-units |
| --- | ---: | --- |
| Формирование brief | 1–5 = 5 | current outcome, каждый атом полного `done_when`, влияющие source/input units, delta, authority и candidate capability |
| Работа actor-а | body скила не передаётся; поля brief | outcome + каждый критерий + применимые source/input units + delta + authority constraints |
| Следующее решение root | 3–7 = 5 | общая траектория, unresolved criteria/dependencies, returned evidence, controller result |
| Rework | 6–7 = 2 | только failed/gap criteria, missing delta и affected current addresses |

Счёт не маскируется числом файлов или длиной формулировки. Если actor либо
следующее решение root заметно выходят за мягкий ориентир, route меняется;
само превышение не требует delegation и не задаёт число агентов.

## Неизбежный порядок

Только три зависимости требуют порядка:

1. Sources/inputs прочитаны root до формирования brief.
2. Feasibility actor-а и root проверена после добавления brief, но до запуска.
3. Evidence по всем критериям получено до зависимого хода.

Остальное competent agent планирует сам.

## Losses и gaps

- Нет точной весовой модели cognitive unit: intent даёт soft signal, а не
  доказанный порог или эквивалентность сложных и простых units.
- «Все влияющие sources» ограничено доступным discovery; абсолютную полноту
  нельзя гарантировать prompt-ом, поэтому неизвестный owner остаётся gap.
- Domain-specific evidence и способ acceptance намеренно не определены: ими
  владеет current specialized controller или project owner.
- Не заданы модель, concurrency, retries, thread lifecycle, storage и формат
  durable trace: это live runtime authority, не функция скила.
- Не создан reference-файл, шаблон brief, реестр решений или отдельная
  topology: для данного intent их counterfactual benefit не превышает
  добавленную нагрузку.
- Полный `done_when` в brief остаётся task-level acceptance projection, а не
  новым domain owner; нужен holdout, чтобы проверить, не превращает ли модель
  эту границу обратно в пересказ sources.
