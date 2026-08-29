# Refactor map v6 — 1orchestration

## Функция

В момент general coordinated wave или явного managed offload выбрать
минимальную окупающуюся форму, распределить между окнами work + instruction
load, защитить ownership и барьеры, а затем принять evidence и собрать один
результат, не отдавая root траекторию и решения.

## Уникальный контекст

Субагенты покупают независимость и чистоту контекста ценой координации. Только
оркестратор видит одновременно целую просьбу, пользу проекта, карту потоков,
цену активных инструкций и общую интеграцию.

## Цель владельца

Один агент не должен одновременно тащить весь свод инструкций, исполнение,
проверку и траекторию; root остаётся CTO, а исполнители получают посильную
задачу и сфокусированный instruction set.

## Момент вызова

- General wave: прямая просьба оркестрировать/разделить работу между 2+
  субагентами либо instruction-required parallel/staged streams без другого
  controller-а.
- Managed offload: live skill явно назначает root оркестратором; один уже
  запрошенный bounded поток не отменяется и не размножается автоматически.
- Skip: один ordinary worker/advisor/critic и волна, формой которой уже владеет
  `1fresh-eyes` или `1deep-agents`.

## Три цели

1. Минимальная окупающаяся форма без лишних окон.
2. Посильные outcomes, сфокусированный instruction load, явные ownership, барьеры и
   return packets.
3. Root удерживает пользу/траекторию и собирает один доказанный результат.

## Счёт активных единиц

| Файл | Текущая v5 | Кандидат v6 | Как считалось |
|---|---:|---:|---|
| `SKILL.md` | 19 | 19 | Разделялись указания, которые можно нарушить независимо; взаимоисключающиеся ветви одного решения считались одной. |
| `references/repair.md` | 7 | 7 | Trigger · probe · repair tree · replacement · terminal · root-break recovery · durable transition. |
| `references/wave-folder.md` | 8 | 8 | Trigger · path · carrier schema · acceptance · branch-stop · transition · decisions · owner transfer. |

## Карта старых указаний

| ID | Старое указание | Цель | Вердикт v6 |
|---|---|---:|---|
| R1 | General 2+ wave trigger | 1 | Сохранен; позитивный use case перенесён в hot zone `description`. |
| R2 | Skip one worker/advisor/critic и specialized controller | 1 | Сужен до ordinary one-worker; managed-offload исключение по owner evidence 2026-08-26. |
| U1 | Независимость/context hygiene против coordination cost | 1 | Сохранён как Уникальный контекст. |
| G1 | Полезная минимальная волна | 1 | Сохранён; добавлена третья законная форма — уже запрошенный one-stream offload. |
| G2 | Обоснованный no-wave | 1 | Сохранён в Целях и Завершении. |
| G3 | Волна не владеет планом/методологией/продуктом | 3 | Поглощён direct-owner rule и отрицательной routing-границей. |
| D1 | Root сам читает load-bearing owners | 3 | Сохранён дословно по смыслу. |
| D2 | Root разрешает reversible in-scope, owner — durable/authority/irreversible | 3 | Сохранён. |
| D3 | Допуск по independence/ownership/context/time gain | 1 | Сохранён; managed-offload добавлен как взаимоисключающаяся ветка того же решения. |
| D4 | Parallel только independent; dependent handoff условен | 1 | Сохранён в Стандарте и order-sensitive шаге 3. |
| D5 | Минимум окон; не создавать generic reviewer | 1 | Сохранён двумя строками Стандарта. |
| D6 | Деление по outcome или owner | 2 | Сохранён. |
| W1 | Chat map до launch с outcome/order/barrier/ownership/focus/return | 2 | Сохранён; для one-stream offload названа одна строка. |
| W2 | Self-contained brief с live addresses, boundaries, focus и return packet | 2 | Сохранён; статическая table-полемика снята как историческая. |
| W3 | File/write isolation и root не пересекает barrier | 2 | Сохранён в шаге 3. |
| W4 | Return до synthesis; evidence ≠ progress report | 3 | Сохранён в шаге 4. |
| W5 | Независимая acceptance только по риску/контракту, не автором | 3 | Сохранён в Стандарте и шаге 4. |
| W6 | Root разрешает конфликты, проверяет claims, интегрирует и отчитывается | 3 | Сохранён в шаге 5. |
| C1 | Plan state vs wave mechanics seam | 3 | Обновлён: живой owner теперь task-file; удалён несуществующий `1planning → Delegation`. |
| C2 | Conditional no-plan carrier | 3 | Сохранён и адресует полный draft reference. |
| C3 | No-delta repair terminal | 3 | Сохранён; root-break recovery стал self-contained. |
| F1–F4 | Четыре дублирующих failure-строки | 1–3 | Поглощены D3, W2, W4 и W6: каждое действие теперь стоит в своём моменте. |
| Z1 | Completion для launch и no-launch | 1–3 | Сохранён и расширен на законный one-stream managed offload. |

## Новые ограничения

| Ограничение | Закрываемый провал | Вытесненная свобода |
|---|---|---|
| Managed-offload является отдельной ветвью admission | Общий skip отменял явно запрошенный one-thread offload. | Root больше не может отменить offload из-за общего порога; всё ещё может отказаться от лишних окон. |
| Root-break recovery self-contained в `repair.md` | Ссылка вела в снятый `1planning/references/delegation.md`. | Root больше не может переложить recovery на несуществующий owner. |

## Принципы

Решение: узкий refactor v6, а не новая функция.

- `agentic-research:P-002` — вернуть root выбор формы и траектории; не добавлять
  статическую таблицу или новый checklist.
- `agentic-research:P-005` — проверять general wave, one managed offload и root-break
  recovery на observable outputs; не принимать lint за behavioral proof.
- `agentic-research:P-007/P-008` — держать смысл в существующем owner-пакете; не
  создавать второй control surface.

Контрпринципная проверка: `agentic-research:P-003` требует учесть ситуацию
за буквальной просьбой; поэтому более новая договорённость про managed background
threads побеждает прежнюю буквальную one-worker границу.
