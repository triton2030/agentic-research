# Карта механики снимаемых пакетов — вход рефактора v3

Мой собственный разбор, исполнителю с чистым окном не передавался. Служит
сверкой при проверке потерь (`refactor.md`, «После полного черновика»).

Снимаемое = **v2** (`skills/shared/1document-system/portable/`, 2 файла,
18 единиц) + **`1ia-audit`** (8 файлов, 662 строки, ~109 механизмов), который
владелец решил влить целиком и снять (`#L37`).

Итого **127 механизмов**.

## A. v2 — тело, 11 единиц

| № | Механизм |
| --- | --- |
| A1 | Принять словарь проекта целиком, если он живой; признак жизни — текущие файлы ему следуют |
| A2 | Взять его имена типов, разделы и метаданные без изменений и не подмешивать своего; два словаря убивают адрес |
| A3 | Уступают только эти три вещи; остальное действует в любом проекте |
| A4 | Открыть `type-selection.md`, когда своего словаря нет и тип корпусом не задан; вернуться с термином и именем файла |
| A5 | Брать у стереотипа жанр и порядок, но не объём, не церемониальные разделы, не регистр |
| A6 | Вытесненное — только то, на место чего встаёт новый текст, а не то, что сформулировал бы иначе |
| A7 | Авторство роли не играет, историю держит git |
| A8 | Проверка по diff: несёт удаления; объём без нового охвата = вытеснения не было |
| A9 | Закрывать по готовому файлу, а не по своему отчёту; назвать действие или вопрос для каждого блока |
| A10 | Жанровая дисциплина не уступает никогда |
| A11 | Семья артефактов чужого скила остаётся за ним — маршрутизировать, не типизировать |
| A12 | Не вносить служебные семьи: история ревизий, статус/версия, summary, введение, предыстория, заключение, преамбула о границах, глоссарий, приложение |
| A13 | Пересказ несёт источник и его состояние и не добавляет своих фактов |
| A14 | Изменившийся источник делает пересказ устаревшим до перепроверки |
| A15 | Переросший файл письмом не чинится — `1ia-audit` |

## B. v2 — `type-selection.md`, 7 единиц

| № | Механизм |
| --- | --- |
| B1 | Тип выбирается от вопроса, переживающего разговор |
| B2 | Опора на именованные внешние рамки: YAGNI, KISS, just enough documentation |
| B3 | Самый лёгкий стандартный деловой термин; ближайший стандартный бьёт выдуманный точный |
| B4 | Термин остаётся деловым стандартом, обычно английским, даже когда тело на языке проекта |
| B5 | Новый тип и его дом допускаются только с первым реальным документом |
| B6 | Имя файла `<ТИП> — <предмет>.md`; предмет — устойчивая вещь, не повод |
| B7 | Имена по конвенции (`README.md`, `CHANGELOG.md`) объявляют тип первой строкой |

## C. `1ia-audit` — тело

| № | Механизм |
| --- | --- |
| C1 | Три режима: audit, design, change; audit/review read-only |
| C2 | Рекомендация сама не разрешает mutation |
| C3 | **Natural form** — наименьшая структура, в которой primary reader находит, понимает, меняет и проверяет mutable answer у одного owner без false seams и independently editable copies |
| C4 | Видимая композиция (length, headings, близкие темы, симметрия) только **номинирует** вопрос, verdict-ом не является |
| C5 | Фазовое состояние: admission/authority → current trace → candidate trace → material delta → mechanism/repair → permission/proof |
| C6 | Каждая фаза даёт наблюдаемый результат до следующей |
| C7 | Новое evidence опровергло premise/owner/job → отбросить downstream state и перестроить |
| C8 | `Not material` завершает вопрос без redesign |
| C9 | `Unresolved` authority не разрешает положительный shape verdict |
| C10 | Неодинаковая конкретность traces даёт `unknown` |
| C11 | Нет material delta — нет IA-улучшения |
| C12 | Длина не создаёт seam (демонстрация) |
| C13 | **Authority:** IA владеет job, natural form и seam **одного** bounded surface; не создаёт reusable system types, system-wide homes и folder axes; не переназначает semantic owner; не исполняет graph/instruction/planning/runtime mutations |
| C14 | Возвращать минимальный проверяемый packet, а не весь controller |
| C15 | Готово/стоп; возврат к последней непройденной фазе; остановка до mutation, если intent не разрешает слой |

## D. `1ia-audit` — Gate 0–1 (допуск и authority)

| № | Механизм |
| --- | --- |
| D1 | Назвать mode |
| D2 | Разделить current surface и proposed change; greenfield не делает candidate baseline |
| D3 | Ограничить surface точным документом/секцией/контейнером и назвать, что вне verdict |
| D4 | Записать primary reader и **один observable action**, ради которого форма существует |
| D5 | Записать mutable answer или obligation, который reader должен найти, применить или изменить |
| D6 | Materiality: форма не меняет job, путь к ответу или update/validation → `not material` |
| D7 | Выписать material premises; если отрицание меняет scope/owner/verdict — проверить или `unknown` |
| D8 | Candidate semantic owner — не место, где текст случайно найден |
| D9 | Прочитать live responsibility/normative contract, назначающий authority |
| D10 | Status `confirmed`/`unresolved`; polish, rank, filename и удобная новая форма owner-а не назначают |
| D11 | Отделить semantic owner от container, view, index и физического placement — это разные оси |
| D12 | Назвать, кто и при каком trigger обновляет ответ, и его lifecycle |
| D13 | Назвать check/validator и dependent view/consumer, если они в той же операции |
| D14 | Разделить primary job и secondary material; secondary внутри только при том же reader, lifecycle и validation |
| D15 | Seam независим по reader, owner, lifecycle, edit trigger и check; headings и темы seam не доказывают |

## E. `1ia-audit` — Document Form Lens

| № | Механизм |
| --- | --- |
| E1 | Документная форма — интерфейс к информации |
| E2 | Прогнать lens для обеих сторон пары; один правдоподобный trace shape change не обосновывает |
| E3 | Цепочка: reader task → information moves → section grammar → agent operation trace → evidence |
| E4 | Таблица «reader task → нужные moves → формы-примеры», 7 строк — **открытый lens, не каталог типов** |
| E5 | Primary job first; secondary как секция при том же reader/lifecycle/validation |
| E6 | Split по независимости, не по числу headings |
| E7 | Agent effect required: форма обязана наблюдаемо менять retrieval, context completeness, update locality или blast radius |
| E8 | Truth vs teaching/view: tutorial и overview компонуют owner truth, но durable rule остаётся у canonical owner |
| E9 | Form-task mismatch: policy в FAQ, evidence как decision, reference длинной прозой |
| E10 | Template monoculture: одинаковые секции только при одинаковых jobs и checks |
| E11 | **No catalog invention** → нужен admitted reusable type, section contract или template — передать `1document-system` |

## F. `1ia-audit` — Gate 2–4 (operation pair и delta)

| № | Механизм |
| --- | --- |
| F1 | Exact trigger/query, с которого начинается работа читателя |
| F2 | Как он находит confirmed owner, либо первый наблюдаемый wrong turn |
| F3 | Minimum sufficient slice, без которого ответ нельзя понять или применить |
| F4 | Конкретный understand/use act |
| F5 | Exact edit anchor, где меняется mutable answer |
| F6 | Обязательные соседние edit hops; pointer/view не edit anchor, если durable truth там не меняется |
| F7 | Affected holders/dependent views только когда операция их требует |
| F8 | Bounded validation, доказывающая корректность после update |
| F9 | Для каждого friction — адресуемое body/usage evidence |
| F10 | Deletion test для shallow/pass-through контейнера: убирает ли его удаление стоимость операции |
| F11 | Пропущенное звено помечать `not applicable`/`unknown`, а не достраивать прозой |
| F12 | Smallest viable candidate против конкретного current friction; greenfield сравнивается с наименьшей рабочей формой |
| F13 | Тот же trigger и тот же mutable answer, иначе сравниваются разные jobs |
| F14 | Owner discovery восстанавливается заново; новая taxonomy не discoverable автоматически |
| F15 | Не потерялся ли необходимый context за новой seam |
| F16 | Те же категории, что в baseline |
| F17 | New/removed/moved hops не сворачивать сразу в число шагов |
| F18 | Где normative truth, где navigation/teaching/generated view; **два independently editable truth surfaces не допускаются** |
| F19 | Independence test повторяется для split/merge/move |
| F20 | Reversibility и future constraint: какую следующую правку candidate удешевляет, какую закрывает |
| F21 | Сопоставление звено к звену, не подробный trace против абстрактной фразы |
| F22 | Affected dimension из семи: retrieval, context completeness, comprehension, update locality, conflict surface, validation, edit blast radius |
| F23 | Каждой дельте — evidence либо `hypothesis`; ожидаемая аккуратность не evidence |
| F24 | Signal ≠ evidence: длина, headings, links, similarity, симметрия папок, search rank, template conformity только номинируют |
| F25 | Counts допустимы лишь как summary уже прочитанных hops |
| F26 | Для каждого gain проверить ближайшую потерю |
| F27 | Evidence изменило premise/owner/job → clean re-anchor обеих traces, не защита предпочтённого candidate |
| F28 | Итог: `material gain / material loss / trade-off / no material delta / unknown` |

## G. `1ia-audit` — Gate 5–6 (repair и proof)

| № | Механизм |
| --- | --- |
| G1 | Failure mechanism одним causal statement: какая форма заставляет кого сделать какую лишнюю операцию и какой вред следует |
| G2 | Mechanism объясняет observed delta, а не переименовывает длину, похожесть темы или отклонение от шаблона |
| G3 | Smallest repair; минимальность мерится устранённым harm, не размером diff |
| G4 | Сравнивать 2–3 формы только при материальном различии по trace/owner/lifecycle/validation/reversibility |
| G5 | Один semantic owner и одна normative representation; вторая тропа — pointer/view при доказанном втором reading path |
| G6 | Current form verdict: `pass / risky / fail / unknown / not present` |
| G7 | Proposed change decision: `accept / reject / defer / not requested` |
| G8 | Согласованность: `pass + accept` требует нового gain; `fail + reject` требует другого repair; подтверждённый red flag несовместим с `pass` |
| G9 | Отделить shape recommendation от authority на mutation; назвать, что intent реально разрешает менять |
| G10 | При move/rename/delete получить read-only graph-impact evidence до final verdict |
| G11 | В change mode применять только разрешённую правку и минимальные supporting edits |
| G12 | После правки повторить ту же операцию: те же trigger, answer, reader, dimensions |
| G13 | Проверить direct read/diff, owner/placement, truth/view, routes, structural gate |
| G14 | Предсказать bypass: форма чище, а wrong turn остался; split сохранил дубль; view стал owner-ом; validation не покрыла новую seam |
| G15 | Counterfactual walkthrough — design-time proxy; material claim требует cold-start или previous-version case |
| G16 | Self-report, заполненный packet, lint и валидность ссылок улучшения не доказывают |
| G17 | Назвать один affected external owner и один unresolved risk |

## H. `1ia-audit` — Smell Catalog

| № | Механизм |
| --- | --- |
| H1 | Правило чтения: `signal → candidate smell → body check → owner-registry check → judgment → smallest repair` |
| H2 | Нет evidence → `unknown`, а не вкус |
| H3 | Подтверждённый неустранённый red flag → `risky` или `fail`; назвать owner или handoff недостаточно |
| H4 | **Duplicate truth** — один durable decision в нескольких independently editable местах; риск drift |
| H5 | **Ownerless container** — папка не отвечает, кто владеет смыслом и правками; копит мусор |
| H6 | **View стал truth** — index/MOC/report/dashboard содержит уникальные правила |
| H7 | **Blind atomization** — дробление без отдельных readers, owners, checks |
| H8 | **Taxonomy aesthetics** — симметрия папок без укорочения edit path |
| H9 | **Speculative scaffolding** — папка «на будущее» без 2+ однотипных файлов и owner-а |
| H10 | **Mixed functions** — canon, задачи, критерии, примеры, заметки и view в одном файле |
| H11 | **Retrieval gap** — имя/description/headings не выводят к owner truth |
| H12 | **Жанровый наполнитель** — секция или оговорка существует потому, что её требует жанр: колонка с одним значением, защита от несуществующего возражения, TOC в коротком документе |
| H13 | **Metrics-as-verdict** — длина и counts названы причиной без чтения содержания |
| H14 | Duplicate truth diagnosis: `location / topology / relation / representation` |
| H15 | `grep -c`, 3+ совпадений и similarity — только candidate generators; читать каждый context |
| H16 | Repair уточняется attributes: inside-file → один home со stable ID; owner-echo → anchor + local consequence; project-domain → удалить дубль или pointer; competing-owners → authority unresolved до решения владельца; prose-table-machine → одна normative representation |
| H17 | Дубль производится section/template contract → diagnosis `template defect`, handoff `1document-system` |
| H18 | Form-task mismatch, template monoculture, cluster/folder mismatch |
| H19 | **Изобретённый словарь** — термин закрытого словаря вне реестра владельца |
| H20 | **Невысказанный инвариант владельца** — правило живёт только как выводимое следствие, и чужая проекция становится de-facto answer surface |
| H21 | **Родовой retrieval surface** — description точен, но не отличает файл от соседей; плоский top-3 |

## I. `1ia-audit` — Design Patterns

| № | Механизм |
| --- | --- |
| I1 | Начинать от живой оси; более красивая таксономия не evidence для реорганизации |
| I2 | Две легитимные оси: project/feature и domain/capability; отдельная ось требует повторяющегося давления workflow |
| I3 | Держать вместе то, что обычно читают, меняют и проверяют вместе |
| I4 | Split только при независимом owner, lifecycle, retrieval/update path или validation |
| I5 | One truth, optional views: view владеет навигацией и синтезом, но не вводит конкурирующих durable rules |
| I6 | Таблица пяти форм: одна секция у живого owner-а · отдельный owner-файл · MOC/hub · генерируемый view · hub-and-spoke |
| I7 | Для hub-and-spoke направление явно; симметричные папки и взаимное владение не требуются |
| I8 | Лестница решений: секция → отдельный контейнер → truth + view → динамический view |

## J. `1ia-audit` — Evidence

| № | Механизм |
| --- | --- |
| J1 | Цепочка `signal → smell → read bodies → confirm authority → judgment → repair` |
| J2 | Route once: тела → `md` CLI; неизвестный owner/дубль → `1md-search`; holders/anchors/cycles → `1md-graph`; точные вхождения → `1cli-tools` |
| J3 | Не копировать их runbooks; дать корень, зону и один извлекаемый вопрос |
| J4 | Два IA-owned channels: `md audit` и `md canon-check`; оба платные, требуют тёплого индекса |
| J5 | Пустая выдача = «нет кандидата в этой пробе», не отсутствие дефекта |
| J6 | Таблица интерпретации кандидатов; семантическое пересечение только номинирует пару |
| J7 | Search rank доказывает discoverability, не authority |
| J8 | Холодный/частичный индекс снижает уверенность покрытия |
| J9 | Подстройка порога оправдана, только если меняет материальный набор и калибруется парой известных примеров |
| J10 | При move/rename/delete запросить graph-impact packet до verdict; edge mutation после — у `1md-graph` |

## Предварительная диспозиция

Не решение, а рабочая гипотеза до возврата чистой комнаты.

| Группа | Ожидание | Основание |
| --- | --- | --- |
| C3, C4, F18, F24, H4, H6, H13, I5 | **выживут** | Ядро «одна правда, вид не становится правдой, сигнал не вердикт» — прямо служит цели «второго расходящегося ответа не осталось» |
| E4, E7, I1–I4, I6–I8, D14, D15 | **выживут в свёрнутом виде** | Выбор дома по смыслу — заказан владельцем (`#L40`), но 20 механизмов лестниц и осей в бюджет не влезут |
| H5, H7, H9, H10, H12 | **кандидаты** | Признаки грязного, названные владельцем (`#L44`): чужой жанр, структурная грязь |
| C1, C5, C6, C14, C15, D1–D3, F1–F28, G1–G17 | **сняты почти целиком** | Evidence-контроллер read-only аудита с шестью гейтами и трассировкой операций. Новый скил — скил записи; владелец требует «без каких либо протоколов или длинных инструкций» (`#L47`) |
| C13 | **отменён владельцем** | «не создаёт system-wide homes или folder axes» — ровно то, что владелец заказал делать (`#L40`) |
| E11, H17 | **самоотменяются** | Маршруты в `1document-system`, который теперь и есть этот скил |
| J1–J10 | **сняты** | Инструментальный слой чужих владельцев; при снятии `1ia-audit` маршруты к ним остаются у их собственных скилов |
| A1–A15, B1–B7 | **проверяются отдельно** | Действующий пакет; часть поглощается новой целью, часть должна выжить |
