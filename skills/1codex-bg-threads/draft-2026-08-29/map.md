# Карта рефактора 1codex-bg-threads — 2026-08-29

## Функция, контекст и цели

Каноническая формулировка находится в [`../origin.md`](../origin.md).

Первый кандидат снят после owner correction
`_ops/chat-recall/2026-08-29-203235-codex-01a04e23.md:17-25`: lifecycle
controller был слишком низкой ролью. Новый центр — технический директор,
который минимально работает сам, делегирует даже существенное мышление и
отвечает за бизнес-пользу и архитектурную траекторию.

## Плоский список старых указаний

| № | Старое указание | Новое владение |
| ---: | --- | --- |
| 1 | Actionable `THREAD_CARD` назначает receiver | `SKILL.md / Роль` |
| 2 | Retained receiver сначала читает retained contract | `Роль` → reference |
| 3 | Receiver перед terminal читает result contract | `Роль` → reference |
| 4 | Цитата или неполная карточка receiver не назначает | Поглощено actionable-card критерием |
| 5 | Иначе агент является controller | `SKILL.md / Роль` |
| 6 | Invocation означает managed offload | Первая цель + controller rule |
| 7 | Invocation автоматически применяет `1orchestration` | Controller rule |
| 8 | Root сохраняет trajectory, synthesis, acceptance и lifecycle | Первая цель + controller role |
| 9 | Ordinary subagents — другой уровень | Unique Context |
| 10 | Один bounded thread получает один outcome | Controller rule |
| 11 | Retained service переиспользует topic specialist | Вторая цель + controller rule |
| 12 | Retained specialist имеет stable title | Final lifecycle rule |
| 13 | Retained specialist имеет source resolver | Вторая цель + retained reference |
| 14 | Все background threads unpinned | Final lifecycle rule |
| 15 | Новый outcome создаёт новый thread | Поглощено one-outcome правилом |
| 16 | Fork только для history divergence | Brief reference |
| 17 | Launch-only только по буквальному create/fork handle request | Controller rule + Stop |
| 18 | Managed controller ждёт и синтезирует | Первая/третья цели + Stop |
| 19 | Только root создаёт top-level visible threads | Controller role |
| 20 | Visible thread может вызывать same-thread subagents | Controller rule |
| 21 | Перед launch/fork/follow-up открывается brief | Controller rule |
| 22 | Brief не расширяет authority, write scope или permissions | Brief goal |
| 23 | Read-only работает Local | Environment rule |
| 24 | Disjoint exact writes работают Local | Environment rule |
| 25 | Worktree требует same-file overlap | Environment rule |
| 26 | Worktree требует проверки single writer/serialization | Environment rule |
| 27 | Integration остаётся у root | Первая цель + controller role |
| 28 | Cheap default — Luna/max | Model rule |
| 29 | Exact current-request pair побеждает default | Model rule |
| 30 | Missing Luna возвращает gap | Model rule |
| 31 | Перед native action открывается runtime | Controller rule |
| 32 | Live schema владеет call contract | Runtime goal/truth order |
| 33 | Terminal/needs-input открывает result | Controller rule |
| 34 | Bounded thread архивируется после integration | Final lifecycle rule |
| 35 | Retained thread остаётся titled+unpinned | Final lifecycle rule |
| 36 | Receiver возвращает один `THREAD_DONE` | Role + Stop |
| 37 | Launch-only возвращает `threadId` или `clientThreadId` | Stop |
| 38 | Managed done требует identity | Stop |
| 39 | Managed done требует result packet | Stop |
| 40 | Managed done требует integration outcome | Stop |
| 41 | Managed done требует archived/retained state | Stop |
| 42 | Missing metadata capability остаётся gap | Stop/runtime |
| 43 | Retained identity доказывает единственный live `threadId` | Retained reference |
| 44 | Archived retained candidate сначала unarchive+verify | Retained reference |
| 45 | Cache не является source of truth | Retained goal |
| 46 | Resolver различает same/delta/replacement | Retained reference |
| 47 | Source conflict блокирует только зависимый claim | Retained reference |
| 48 | После compaction восстанавливается card/source basis | Retained reference |
| 49 | Replacement нельзя создавать до разрешения identity | Retained reference |
| 50 | Runtime truth order: schema → docs → merged source | Runtime reference |
| 51 | Missing native action не имитируется subagent-ом | Runtime reference |
| 52 | Ambiguous mutation требует read-after-write | Runtime reference |
| 53 | Create может вернуть queued client handle | Runtime snapshot |
| 54 | Queued handle не равен thread ID | Runtime snapshot |
| 55 | Fork копирует только completed history | Runtime snapshot |
| 56 | Wait — event wait с cursor, не polling | Runtime snapshot |
| 57 | Metadata setter return не доказывает persisted state | Runtime snapshot |
| 58 | Title/summary не доказывают identity | Runtime snapshot |
| 59 | Mutable card называет starting state и exact paths | Brief reference |
| 60 | Follow-up передаёт delta либо полную effective card | Brief reference |
| 61 | Fork объясняет нужность copied history | Brief reference |
| 62 | `THREAD_DONE` имеет candidate/blocked/failed schema | Result reference |
| 63 | Root проверяет packet против card/state/artifacts/checks | Result reference |
| 64 | Worktree writer возвращает durable delta или live checkout | Result reference |
| 65 | Snapshot recovery не равен integration artifact | Runtime/result references |
| 66 | Root минимально выполняет работу и мышление сам | Unique Context + первая цель |
| 67 | Root действует как технический директор | Unique Context + controller role |
| 68 | Root удерживает бизнес-пользу и связность планов | Первая цель + controller role |
| 69 | Работа делится по когнитивно посильным темам | Вторая цель + dependency на `1orchestration` |
| 70 | Sol medium разрешён для действительно сложного reasoning | Model rule |
| 71 | Sol xhigh разрешён для стратегической/архитектурной развилки | Model rule |
| 72 | Mutable output фонового автора требует independent checker | Verification rule + brief |
| 73 | Checker не может быть автором | `1orchestration/verify` + verification rule |
| 74 | Skill владеет свежей официальной Codex thread mechanics | Runtime goal + official sources |

## Группировка по целям

- Перенос работы при сохранении technical-director ownership: 5–11, 17–22,
  27, 31–33, 66–69.
- Достаточный outcome и правильная среда/retention: 1–4, 12–16, 23–30,
  43–61.
- Наблюдаемый результат и lifecycle: 34–42, 62–65, 72–73.
- Codex-specific current mechanics и model routing: 28–33, 50–58, 70–71,
  74.

## Новые ограничения и цена

| Ограничение | Закрываемый провал | Вытесненная свобода |
| --- | --- | --- |
| Три самодостаточные цели | Агент соблюдает механику, но root не разгружается или не закрывает lifecycle | Нельзя считать отдельный удачный tool call целью работы |
| Runtime reference имеет локальную цель и truth order | Датированный каталог начинает конкурировать с host schema | Нельзя действовать по памяти о старой schema |
| Peer protocol снят | Skill обещает capability, которой нет в live contract | Прямая peer-коммуникация не моделируется без native surface |
| Один observable-state gate | Десятки повторных запретов конкурируют за внимание | Нельзя закрыть lifecycle одним самоотчётом или setter return |
| Technical-director commander intent | Root делегирует руки, но продолжает думать как локальный исполнитель | Root не может присвоить себе делегируемое мышление ради скорости |
| Independent checker для mutable background output | Дешёвый автор производит правдоподобный, но неверный artifact | Нельзя принять авторский self-check; появляется дополнительный slot и latency |
| Sol medium/xhigh только по сложности | Luna получает системную развилку либо Sol тратится на рутину | Controller обязан классифицировать когнитивную сложность outcome |

## Проверка добавок сверх буквальных слов владельца

| Добавка | Дефолт → механизм → решение → вред без строки → цена строгости |
| --- | --- |
| `THREAD_CARD` назначает receiver | отдельный thread может решить, что он controller → role ambiguity → ограничить роль карточкой → фоновые треды начинают менять topology → карточка должна быть actionable |
| Root не делегирует business/topology/acceptance | делегирование мышления выглядит как передача всей задачи → authority drift → оставить сквозные решения root → флот оптимизирует локальные мелочи → root всё ещё тратит внимание на верхний уровень |
| Launch-only только по буквальному handle request | успешный create выглядит завершением → tool-success bias → различить launch-only и managed → работа не выполнена, но thread создан → controller обязан ждать обычный managed run |
| Sol medium/xhigh имеет разные пороги | сильная модель кажется безопаснее на любой трудности → capability bias → medium для bounded hard reasoning, xhigh для material strategic fork → цена и контекст растут без пользы либо Luna проектирует систему → один judgment сложности до launch |
| Missing exact model pair возвращает gap | тихая замена кажется полезнее остановки → authority gap → не подменять owner route → незаметно меняется стоимость или качество → возможна остановка launch |
| Worktree проверяет single writer/serialization | изоляция выглядит универсальной безопасностью → environment overhead → выбрать Worktree только после дешёвых вариантов → плодятся checkout и integration work → controller доказывает overlap |
| Event supervision вместо polling | «следить как за детьми» звучит как постоянное чтение → monitoring literalism → наблюдать state и отклонение от card → root снова делает работу исполнителя → промежуточные мысли не видны постоянно |
| Verifier не является автором | self-check дешевле отдельного слота → confirmation bias → независимая acceptance → правдоподобный mutable artifact принимается без проверки → дополнительный thread и latency |
| Persisted state наблюдается после setter | completed tool call выглядит доказательством → async metadata → read-after-write → retained остаётся pinned или bounded не архивирован → дополнительный read |
| Retained cache не является truth | прогретая память быстрее source resolver → stale-context bias → re-resolve owner и delta → specialist уверенно повторяет старую правду → повторное чтение изменившегося scope |
| Live schema побеждает runtime snapshot | датированный официальный reference выглядит достаточным → changing host surface → выбрать доступный call по live schema → skill угадывает отсутствующую команду → capability gap вместо выдуманного обхода |

## Протокол и неверные прочтения

| Неверное прочтение | Закрывающий шаг | Цена правки |
| --- | --- | --- |
| Root минимально работает, значит не синтезирует и не принимает | 1 и 6 сохраняют technical-director ownership | Root всё ещё платит вниманием за сквозные решения |
| Делегированное мышление передаёт исполнителю бизнес-приоритет | 1 оставляет пользу, план и архитектуру у root | Исполнитель не автономен менять top-level outcome |
| Любая трудность разрешает Sol | 3 различает bounded difficulty и material strategic fork | Controller классифицирует сложность до launch |
| Автор проверяет собственный mutable output | 5 требует отдельный verification slot | Дополнительный thread и latency для write-work |
| «Следить как за детьми» означает polling и микроменеджмент | 4 наблюдает events и card deviation | Root не видит каждую промежуточную мысль |

## Счёт самостоятельных единиц кандидата после checker round 2

- Общий активный набор body: 5 единиц — три цели, выбранная role и текущий
  route. Завершённая стадия закрывается своим артефактом до следующей.
- `runtime.md`: 20 единиц вместе с локальной целью, входом и truth order.
- `environment.md`: 8 единиц вместе с локальной целью и входом.
- `thread-brief.md`: 16 единиц вместе с восемью обязательными полями.
- `thread-result.md`: 15 единиц вместе с семью обязательными полями.
- `retained-thread.md`: 13 единиц.
- `lifecycle.md`: 12 единиц.

## Карта самостоятельных стадий

| Стадия | Наблюдаемый вход | Выход | Активные единицы |
| --- | --- | --- | ---: |
| Controller orientation | Нет actionable `THREAD_CARD` | Technical-director outcome map и запущенный `1orchestration` | 6 |
| Runtime resolution | Есть принятый orchestration slot, native contract ещё не доказан | Capability, model и identity snapshot | 20 |
| Environment resolution | Capability snapshot готов, среда не выбрана | Один environment verdict | 8 |
| Brief assembly | Snapshot и environment verdict готовы | Один достаточный `THREAD_CARD` | 16 |
| Launch и supervision | Карточка готова | Живой identity и event-observed state | 6 |
| Writer verification | Mutable author вернул candidate | Независимый `proven` либо blocker в `1orchestration` | 6 плюс текущая стадия `1orchestration` |
| Result resolution | Terminal/needs-input state наблюдаем | Проверенный semantic result | 15 |
| Retained re-entry | Прежний тематический specialist нужен снова | Разрешённый identity и current source basis | 13 |
| Lifecycle closure | Result принят | Archived bounded либо titled+unpinned retained state | 12 |

Runtime resolution и Brief assembly — последовательные стадии: агент закрывает
`runtime.md`, сохраняет его snapshot как артефакт и только затем открывает
`thread-brief.md`. Ни один reference не требует чтения другого reference.
Каждый reference-счёт уже включает локальную цель и вход. Общий body-набор не
складывается с ним второй раз: route закрывается передачей управления стадии,
а её выход возвращает controller в body. Финальный независимый повтор должен
проверить эту модель активного набора.
