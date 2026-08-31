# Reviews v6 — round 4 (commander intent)

Проверяемая версия: `draft-v6/**` после прямых решений владельца
`_ops/chat-recall/2026-08-29-163434-codex-01a04d4a.md:21-22`.

## Проверка траектории

Fresh-eyes дал не консенсус, а полезное расхождение:

- Ladder: цепочка от refactor-а до верхней цели проекта держится.
- Solvent: universal observable state machine — недоказанное допущение;
  `count`, `map` и `carrier` нельзя делать ценой любого поручения.
- Prospector: mission command поддерживает intent + существенные границы;
  Kubernetes/Temporal предупреждают не копировать control-plane без runtime.
- Premortem (`claude-opus-5`): сигнал уже присутствовал — до терминального
  исхода прежняя версия безусловно читала `orient`, `brief`, `count`, `budget`.

Решение: не начинать refactor заново. Сохранить точные функциональные швы, но
сделать полный ledger и control-plane условными. Лёгкий путь теперь
`orient → brief → approximate root/actor count → shape →
direct-assignment|no-delegation|controller-handoff`.

## Что перенесено в commander's intent

| Смысл | Новый владелец | Снятая procedural-строка | Почему выводится |
|---|---|---|---|
| Root оценивается вместе с исполнителями | `Уникальный контекст`: каждое текущее решение, включая root | `decompose`: отдельное повторение про root | Центральная модель уже задаёт общий субъект нагрузки. |
| Деление законно только при меньшем следующем наборе | Цель 2 | `budget`: безусловное действие после verdict-а | Route `decompose` и цель вместе определяют требуемый исход. |
| Явная схема пользователя не исчезает в `no-delegation` | Цель 3: требуемая схема и полномочия сохранены | `shape`: отдельный запрет `no-delegation` | Cheapest schema обязана удовлетворять goal/done_when и explicit actor/topology constraints. |
| Простое поручение не становится волной | `Уникальный контекст` | безусловные `count → budget` | Body сначала допускает лёгкую оценку и terminal direct assignment. |

## Локальные цели references

| Reference | Локальный intent | Что стало выводимым |
|---|---|---|
| `orient` | Прямое понимание всего влияющего; исследуемый gap — работа | Отдельные команды «запиши каждый источник» и «root прочитай адрес» поглощены наблюдаемым выходом карты. |
| `brief` | Достаточный контракт, не второй канон | Запрет пересказа объясняется моделью owner-address + delta; точная schema осталась. |
| `count` | Проверяемая спорная нагрузка actor/root-point | Нумерация ритуала снята; unit-definition и total-from-entries остались. |
| `budget` | Feasibility без магического cap | Отдельный приказ `decompose` после verdict-а снят; факторы и soft `20` остались. |
| `decompose` | Boundary действительно снимает units | Повтор boundary-rule снят из procedure; stage/parallel, no-honest-boundary и re-entry остались. |
| `handoff` | Specialized owner сохраняет topology и acceptance | Точный terminal packet оставлен отдельно от общей формы. |
| `shape` | Minimal sufficient form без захвата authority | Controller-ветвь вынесена; exact contract/constraints остались. |
| `assign` | Capable actor и live runtime owner | Capability и простой one-slot acceptance отделены от topology. |
| `map` | Убрать launch-неоднозначность | Ни одно поле schema не снято: каждое falsifies ownership, order, barrier или return. |
| `carrier` | Восстановить безопасный ход, не создать canon | Повтор «carrier условен» поглощён context/input; transition timing и evidence остались. |
| `execute` | Один slot outcome без пересечения barrier | Отдельная строка barrier поглощена локальной целью; runtime parallel/serial и state-before-dependent остались. |
| `verify` | Каждый done_when доказан до закрытия | Evidence, verifier boundary и terminal unknown остались отдельным falsifying gate. |
| `accept` | Проверенный slot закрыт до dependent action | Closure, blocker branch-stop, invalidation и state timing остались. |
| `integrate` | Один результат цели; durable truth к owner | Отдельная команда «собери и проверь цель» поглощена локальной целью; evidence/no-vote, chat trace и final state остались. |

## Почему оставшиеся hard lines не выводятся безопасно

- `goal/done_when/read/delta` — точный интерфейс поручения; без него clean agent
  смешивает owner-текст и новую delta либо теряет критерий.
- Прямое чтение root каждого влияющего адреса — owner-exact boundary; ссылка
  исполнителю не доказывает понимание оркестратора.
- Перечисленный ledger и total-from-entries — falsifying acceptance только для
  спорной нагрузки; прошлый executor вернул голые `14/18` и скрыл units.
- `≤20` как мягкий порог — специфичное owner-знание, не общий model default.
- Early `controller-handoff`, capability gate и runtime launch owner — границы
  authority и feasibility; абстрактная цель не выбирает живой интерфейс.
- Stale-инвалидация — recovery-механика после изменения входов.
- Slot/barrier, приёмка до следующего запуска и accepted blocker — критичный
  порядок multi-return, уже нарушенный буквальным checker-ом.
- Условные state writes — точная recovery-семантика; без условия carrier
  превращается в обязательный второй owner.
- Evidence каждого `done_when` и независимый verifier по риску — falsifying
  acceptance; progress/self-report уже были приняты как ложный proof.
- Исследуемая неопределённость в brief — неочевидная ветвь, без которой skill
  блокирует агента, порученного закрыть gap.

## Clean-checker corrections

- `orient` теперь маршрутизируется по принятой карте и её непрочитанным
  адресам, а не по расплывчатому «источники читались».
- Body явно выполняет `actor_count/root_count`, затем разрешает нагрузку в одно
  из состояний: low · `manageable` · accepted overload; historical verdict не
  открывает стадию повторно.
- Перегруженный `shape` разделён на `handoff`, `shape` и `assign`: topology,
  capability и runtime ownership больше не скрыты в одной unit.
- Лёгкий путь пропускает ledger/map/carrier, но создаёт один slot и проходит
  тот же `execute → verify → accept → integrate`.
- Evidence-проверка отделена от закрытия slot-а; недоказанность создаёт
  принятый `terminal blocker`, поэтому `execute` не открывается повторно без
  нового material outcome.
- `carrier` больше не предлагает живого owner-а после входа «живого owner-а
  нет».
- Внешний конфликт runtime-цитат `1skill-creation` не принят как правка
  candidate: прямой owner-refusal сильнее; сигнал сохранён в
  `_ops/findings/2026-08-29-181237-4401-18044.md`.

## Языковая точка

Калька «государственный автомат» отсутствует в candidate, tracked owner и
установленных проекциях. Термины `автомат состояний` / `машина состояний` в
runtime не потребовались; структура из-за этой проверки не менялась.

Codex metadata включена в точную candidate-версию: `short_description` —
короткий English trigger-only текст, `default_prompt` — русский.

## Следующий gate

После этой material edit нужны пропорциональные structural checks, два
независимых clean checker-а и один clean executor на точной версии. Новый
архитектурный круг без нового falsifying evidence не открывается.
