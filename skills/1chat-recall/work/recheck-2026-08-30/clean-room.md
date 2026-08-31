# Clean-room trace

Статус: `superseded process trace`, не candidate и не approval.

Этот проход сохранил semantic value, но не удовлетворил буквальному гейту
`только commander's intent`: вместе с разделом намерения исполнитель получил
служебные Source basis, FAST, hard boundaries и active sets. Два последующих
прохода и окончательное исправление записаны в
[intent-only-clean-room.md](intent-only-clean-room.md).

## Изоляция

- Исполнитель: `/root/clean_room_reimplementation`, новое окно с
  `fork_turns=none`.
- Единственный содержательный вход:
  [intent.md](intent.md).
- Ему было прямо запрещено читать tracked/live `1chat-recall`, history, tests,
  evidence, Product Frame и owner conversations.
- Файлы он не менял.

## Буквально выполненные методы

1. `Clean-room reimplementation`: исполнитель вывел пакет только из сущностей
   literal evidence, provenance/address, owner chronology и existing semantic
   owner.
2. `Zero-based design`: начал с пустого пакета, добавил router и только три
   первоначально выведенные функции — Capture, Retrieval, Repair.

Первичная topology:

```text
1chat-recall/
├── SKILL.md
└── references/
    ├── capture.md
    ├── retrieval.md
    └── repair.md
```

Semantic draft сохранил full-topic-map before Capture, keyword-like context,
atomic quote/index receipt, literal provenance, chronology/live-owner checks,
`abstain`, immutable raw evidence, Repair→Capture и existing-owner-only
restoration. Точные CLI, schema и runtime roots были оставлены placeholders, а
не выдуманы.

## Наблюдённые active sets clean draft

Метод самого исполнителя: одна адресованная нормативная единица `[R/K/C/Q/P]`
равна одной единице.

| Путь | Count |
| --- | ---: |
| Capture | 21 |
| Retrieval | 21 |
| Repair validation | 22 |
| Repair с материальной цитатой | 31 |

Эти превышения и отсутствие точных runtime seams не были скрыты. После
сравнения потерь root вернул Recovery, Restoration и Validation как отдельные
стадии и вынес Repair→Capture в body-router; это снизило каждый одновременный
набор без дробления одной функции.

## Приёмка

Первоначальный вердикт `accepted` отозван после буквального checker-а. Слот
остался полезным evidence, но не закрывает обязательный clean-room критерий.
