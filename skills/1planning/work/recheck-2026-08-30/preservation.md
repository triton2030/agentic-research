# Сохранность 1planning

| Смысл | Носитель | Вердикт |
| --- | --- | --- |
| Скептический what-next admission | Context + Goal 1 | сохранён |
| Один автономный approved handoff | Goal 2 + Protocol 4,7 | восстановлено по acceptance loss |
| Карта/task имеют других writers | Context + Goal 3 | сохранён |
| Живая цель и state до решения | Protocol 1 | восстановлено по observed focus-on-local-prompt harm |
| Применимые project instructions | Protocol 2 | восстановлено по acceptance loss |
| Видимая named book-method декомпозиция | Protocol 5 | восстановлено по acceptance loss |
| Exact approval полного handoff до durable write | Protocol 6 | восстановлено по acceptance loss |
| Handoff без смысловой мутации | Protocol 7 | сохранено как cross-window seam |
| Modes и appetite | — | снято: результат выводим без них |

## Agent-default chains

- `live sources`: агент стартует по последнему сообщению → локальный prompt
  выглядит достаточным → читает цель/state → иначе выбирает stale work → цена:
  один релевантный reread.
- `exact approval`: полезная конкретизация после обсуждения выглядит безвредной
  → меняет поручение → владелец не утверждал записанный смысл → цена: один gate.
- `unchanged handoff`: planner может сразу записать удобную форму → появляется
  второй writer → durable contract расходится → цена: отдельный handoff.
- `applicable instructions`: root state выглядит достаточным → локальное
  правило остаётся непрочитанным → срез нарушает границу проекта → цена: один
  адресованный reread.
- `book trace`: название метода выглядит доказательством → декомпозиция не
  наблюдаема → владелец не видит изменённый срез → цена: один trace метода.
