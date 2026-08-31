# Capture

## Цель

Один helper сохраняет доказанные слова владельца так, чтобы будущий поиск нашёл
и проверил их.

## Уникальный контекст

`topics.md` — единственная карта тематических boundary. `session-context` —
полная актуальная однострочная карточка разговора, а `context-note` — короткий
noun-phrase index: набор существительных и ключевых фраз о конкретной цитате,
не пересказ. Эти метаданные только ведут к evidence.
[chat_capture.py](../scripts/chat_capture.py)
владеет schema, format и atomicity; запускай linked helper через `python3`.

## Ход

1. Захватывай только подтверждённую прямую материальную owner speech: literal
   `quote` или выбранный `selection`; agent follow-up и простое assent пропусти.
2. Открой текущий файл этой сессии целиком, если он существует: обновлённый
   `session-context` должен описывать весь разговор, а не только новую реплику.
3. Через `chat_capture.py --list-metadata` полностью прочитай карту target
   проекта и выбери boundary по предмету цитаты. Если ни одна не подходит,
   создай одну новую в той же операции через `--new-topic` и
   `--new-topic-boundary`; если карты нет, верни gap.
4. По `chat_capture.py --help` выполни одну Capture-операцию с literal evidence,
   темой, коротким `context-note` и полным актуальным `session-context`. Если
   реплика отменяет прежнюю позицию, передай проверенный адрес через
   `--supersedes <file>.md#L<line>`; если конфликт
   не разрешён, передай `--contested <file>.md#L<line>`, иначе верни gap. Для
   `capture-needed` используй native target project/session/timestamp packet;
   source address в corpus не записывай.
5. Успех — только helper receipt и открытый address; иначе gap без ручной записи.
