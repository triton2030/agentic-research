# Refactor map v6 — 1orchestration

## Функция

Перед любым поручением субагенту превратить работу в один или несколько
выполнимых cognitive tasks: root читает все влияющие owners, формирует
goal/acceptance/address/delta brief, оценивает одновременно активные единицы,
декомпозирует перегруженное и принимает один evidence-backed результат.

## Уникальный контекст

Prompt субагенту — временный instruction layer поверх system, проекта, skills,
plan-а и truth owners. Оркестратор единственный видит целую source/work map и
может уменьшить active set исполнителя, не потеряв общую траекторию.

## Цель владельца

Развивать когнитивную работу до выполнимого списка задач: качество определяется
не только субъективной сложностью, но и числом независимо удерживаемых
инструкций, критериев и знаний. Brief сообщает невыводимую дельту и адресует
доступных owners вместо пересказа.

## Момент вызова

- Use: перед поручением любому субагенту, включая один ordinary или managed
  offload поток.
- Use: до разделения перегруженной работы на root/subagent, parallel или staged
  tasks.
- Specialized controller сохраняет topology и роли своей волны;
  `1orchestration` формирует cognitive contract каждого её окна.
- Skip: root выполняет локальную работу сам, и признака cognitive overload нет.

Representative naked-trigger candidates; это ещё не результаты прогона:

- ordinary use: `Поручи субагенту проверить этот файл`;
- overloaded use: `Разбей сложную задачу между агентами`;
- managed use: `Вынеси анализ логов в фоновый тред`;
- specialized composition: `Проведи fresh-eyes аудит траектории проекта`;
- skip: `Исправь эту опечатку сам`.

## Три цели

1. Полная карта влияющих owners прочитана root-ом.
2. Каждый исполнитель получает load-bounded brief.
3. Root интегрирует принятые returns в один доказанный результат.

## Карта стадий и active sets

Применимая часть тела — 9 единиц: центральная модель · три цели · четыре
независимых смысла буквальных owner-цитат · одна выбранная route-строка.
`Завершение` становится десятой единицей только в terminal-момент без reference.
Description — отдельное trigger-решение до входа в протокол.

| Стадия | Вход → наблюдаемый выход | Reference units | Ещё активны из прошлого | Итого |
|---|---|---:|---:|---:|
| sources | работа известна → root прочитал source map | 10 | 0 | 19 |
| brief | source map есть → provisional brief записан | 9 | 1 cursor карты | 19 |
| budget | brief есть → `manageable|decompose` | 9 | 2: cursor + running count | 20 |
| decompose | verdict overload → provisional child list | 9 | 2: общая цель + source-map pointer | 20 |
| map | все tasks manageable → launch map в чате | 10 | 1: verdict set | 20 |
| carrier | карта есть, cold-loss дорог → durable carrier | 9 | 1: launch-map pointer | 19 |
| execute | карта и briefs готовы → packets или blocker | 7 | 3: order/barrier · write owner · return | 19 |
| accept | packet есть → pass либо stopped branch | 6 | 2: done_when · evidence owner | 17 |
| integrate | returns приняты → один результат и chat proof | 6 | 2: accepted set · общая цель | 17 |
| persist | durable state изменён → owners синхронизированы | 5 | 1: current transition | 15 |
| repair | первый wait без delta → return либо final blocker | 9 | 2: named return · dependent barrier | 20 |
| recover-root | root оборван → restored state либо blocker | 10 | 1: plan/carrier pointer | 20 |

Source map и briefs — внешние ledger-артефакты: стадия budget обходит их
последовательно и держит одновременно одну проверяемую единицу и running count.
Это не исключает task units из счёта; это способ не загружать весь кандидат до
того, как verdict определит его форму.

## Карта старых указаний

| ID | Старое указание | Цель | Вердикт v6 |
|---|---|---:|---|
| R1 | General 2+ wave trigger | 2 | Расширен прямой owner-коррекцией 2026-08-29: protocol нужен перед любым subagent prompt. |
| R2 | Skip one ordinary worker и specialized controller | 2 | Ordinary skip снят; specialized owner сохраняет topology, но не отменяет cognitive contract. |
| U1 | Independence/context hygiene против coordination cost | 2 | Переформулирован как active-set design, а не ценность числа окон. |
| G1 | Минимальная окупающаяся форма | 2 | Сохранён через budget, decompose и launch map. |
| G2 | Обоснованный no-wave | 2 | Сохранён как `no-delegation` после budget. |
| G3 | Волна не владеет продуктом/планом/методологией | 1,3 | Сохранён owner-map и specialized-topology seam. |
| D1 | Root сам читает load-bearing owners | 1 | Усилен до полной применимой instruction/truth chain; summary чтение не заменяет. |
| D2 | Root хранит пользу, выполнимость и authority boundary | 3 | Сохранён в `sources`. |
| D3 | Допуск по independence/ownership/context/time gain | 2 | Заменён более фундаментальным budget/decomposition verdict. |
| D4 | Parallel только independent; dependent handoff условен | 2 | Сохранён в `decompose` и `execute`. |
| D5 | Минимум окон; не создавать generic reviewer | 2 | Сохранён через cheaper staged-task и risk-based acceptance. |
| D6 | Деление по outcome или owner | 2 | Расширен decision/stage boundaries и проверкой уменьшения active set. |
| W1 | Chat map до launch | 2 | Сохранён в `map`; добавлен active-unit estimate. |
| W2 | Self-contained brief с addresses, boundaries и return | 2 | Перестроен в goal · done_when · read · delta · write · return. |
| W3 | One writer и dependent barrier | 2 | Сохранён в `execute`. |
| W4 | Evidence до synthesis; progress ≠ evidence | 3 | Сохранён в `accept`. |
| W5 | Независимая acceptance только по риску/контракту | 3 | Сохранён в `accept`. |
| W6 | Root разрешает conflicts, claims, integration и chat report | 3 | Разнесён на `integrate` и `persist`. |
| C1 | Plan state vs wave mechanics seam | 3 | Живой task-file остаётся owner-ом state; orchestration владеет cognitive map. |
| C2 | Conditional no-plan carrier | 3 | Сохранён после launch map. |
| C3 | No-delta repair terminal | 3 | Сохранён; root-break вынесен в самостоятельную стадию. |
| Z1 | Completion для no-launch и launch | 1–3 | Сохранён по budget, acceptance, integration и durable sync. |

## Новые ограничения

| Ограничение | Закрываемый провал | Вытесненная свобода |
|---|---|---|
| Protocol перед любым subagent prompt | Один ordinary worker мог получить когнитивно перегруженное поручение без анализа. | Быстрый delegation без source/brief/budget прохода. |
| Root читает всю применимую owner-цепочку | Prompt мог пропустить спецификацию, plan или acceptance owner. | Делегирование по summary без прямого owner-reading. |
| Brief по умолчанию не повторяет доступный owner content | Повтор увеличивал active load и мог расходиться с каноном. | Риторическое усиление копированием; live receiving owner может потребовать адресованную критичную выдержку. |
| `>20` — soft decomposition threshold | Перегруженный prompt запускался как будто количество обязанностей не меняет adherence. | Безоговорочный launch; escape — named overload с checkpoints и независимой приёмкой. |

## Добавки по agent-defaults

| Добавка | Дефолт → механизм → решение → вред → цена строгости |
|---|---|
| Specialized controller сохраняет topology | General skill видит subagents и перестраивает wave → overlapping controller кажется универсальнее → не менять роли/линзы specialized wave → теряются её acceptance и freshness contracts → cognitive brief обязан вписаться в уже выбранную topology. |
| Scope delta возвращает поток к cognitive stages | Worker продолжает прежний brief → уже начатый ход психологически дешевле остановки → не исполнять новую scope до source/brief/budget → незагруженный owner или overload остаётся невидимым → платим повторным shaping. |
| Неразложимый overload можно принять явно | `decompose` читается как hard prohibition → число 20 выглядит точным gate → разрешить named overload с checkpoints/acceptance → иначе цель урезается или работа не стартует → допускается более слабое adherence с явным риском. |
| Root recovery требует адресуемый state | После обрыва хочется восстановить по памяти чата → продолжение выглядит полезнее остановки → без task-file/carrier вернуть blocker → возможен duplicate external action или ложный accepted state → безопасно recoverable wave иногда останавливается. |
| Runtime owner сохраняет lifecycle | Wave-level repair выглядит владельцем любого wait/follow-up → ближайшая инструкция перехватывает tool semantics → orchestration решает барьер, runtime — lifecycle → неверный polling/retry/archive → root читает дополнительный live owner. |

## Протокол поведения

| Правдоподобное неверное прочтение | Пробел | Цена | Правка / TWI момент |
|---|---|---|---|
| Сначала разделить работу, потом посмотреть инструкции. | Границы проведены без реального active set. | Каждый child наследует тот же перегруз. | `sources → brief → budget` стоит до `decompose`. |
| Ссылок достаточно, goal и acceptance можно оставить в owner-файлах. | Агенту не задано конкретное состояние текущего поручения. | Формально полезное чтение без завершённого outcome. | `brief` отдельно владеет goal/done_when. |
| Для надёжности всегда надо повторить текст owner-а в prompt. | Канон и prompt становятся двумя владельцами смысла. | Дубликат съедает бюджет и устаревает. | `read` адресует; только receiving owner может потребовать критичную выдержку. |
| Двадцать строк равно двадцати единицам. | Несколько независимо нарушимых обязанностей склеены синтаксисом. | Счёт врёт, декомпозиция не срабатывает. | `budget` считает independently forgettable units. |
| `>20` автоматически требует больше агентов. | Parallelism перепутан с cognitive decomposition. | Handoff дороже staged work, write conflicts. | `decompose` сначала выбирает decision/owner/stage boundary. |
| Progress report достаточен для синтеза. | Return не связан с `done_when`. | Root принимает неполный результат. | `accept` отделён от `integrate`. |

## Принципы

- `agentic-research:P-002` — сохранять root-у целую траекторию и уменьшать
  active set исполнителя, а не плодить окна.
- `agentic-research:P-003` — latest owner correction переопределяет router:
  ordinary one-worker теперь тоже проходит cognitive protocol.
- `agentic-research:P-005` — проверять actual source map, brief, count,
  decomposition и acceptance, а не только lint.
- `agentic-research:P-007/P-008` — owners остаются каноном; brief адресует их и
  не создаёт второй truth surface.
