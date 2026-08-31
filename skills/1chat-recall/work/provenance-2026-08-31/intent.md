# Намерение deletion-only Capture

Статус: `установлено`.

## Основание

- Владелец разрешает сокращать его цитату только удалением: сообщение может
  содержать вставленные документы и целые разговоры, которые не являются его
  словами — `_ops/chat-recall/2026-08-29-150002-codex-01a04cf3.md:31`.
- User-visible сообщение, доставленное tool/controller/subagent, не становится
  прямой речью владельца из-за carrier-а `role=user` — там же, `:31`.
- Терминальные команды, help и ответы scripts должны не противоречить
  runtime-контракту — там же, `:32`.

## Commander's intent

### Цель

В корпус попадают только дословные фрагменты владельца. Пасты чужого материала
и agent-delivered сообщения не маскируются под owner speech; при неясном
авторстве агент возвращает gap.

### Уникальный контекст

Message-level provenance и авторство каждого фрагмента внутри сообщения —
разные доказательства. Transcript adapter может подтвердить carrier, timestamp
и source address, но не распознать смысловую границу вставленного документа.
Поэтому агент выбирает owner-authored span и сокращает его только удалением,
сохраняя слова и порядок; capture helper атомарно пишет caller-confirmed excerpt.

## Минимальная архитектурная граница

- Не добавлен `--source-text`: передача полного сообщения раздувает интерфейс,
  увеличивает exposure и всё равно не доказывает авторство вложенного текста.
- Не добавлен эвристический классификатор документов или разговоров: он мог бы
  молча удалить реальные слова владельца.
- Extractors отбрасывают наблюдаемые carriers; Capture contract владеет
  смысловой deletion-only границей; writer владеет schema и atomicity.

## Фальсификаторы

- Legacy Codex `event_msg.user_message` с `<codex_delegation>` или
  `origin.kind=controller` не должен попадать в выдачу.
- Claude plain-text user record с `sourceToolAssistantUUID` не должен попадать
  в выдачу.
- Direct current-schema Codex `response_item.message` должен сохраниться.
- CLI не должен называть transcript candidates доказанными owner quotes и не
  должен документировать отсутствующий флаг.

