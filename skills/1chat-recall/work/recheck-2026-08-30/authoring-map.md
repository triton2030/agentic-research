# Semantic pass и active sets

## Commander's intent

Слова владельца должны оставаться находимым evidence для одного решения, а не
превращаться в профиль, current truth или догадку. В каждом reference цель и
уникальный контекст дают mental model; runtime prose оставляет только decision
boundaries, которые helper не способен выбрать сам.

| Reference | Локальная модель | Terminal result |
| --- | --- | --- |
| Capture | полный holder + topic/session/quote indexes + helper transaction | receipt/opened address либо gap |
| Retrieval | topic route, holder route и owner position — разные вещи | position/`abstain` |
| Integrity | source proof перед обычным Capture | validation receipt или `capture-needed` |

## Active sets

Единица — самостоятельный выбор поведения, action или scope; helper schema,
CLI syntax и поясняющие существительные не дробятся. Учитываются body, выбранный
reference и применимая ветвь; завершённый reference освобождается.

| Runtime | Capture | capture-needed | Retrieval warm / topic follow-up / background | Retrieval cold recovery | Validation | Repair read-only / mutation |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Codex | 20 | 22 | 20 / 22 / 23 | 22 | 10 | 17 / 20 |
| Claude | 20 | 22 | 20 / 22 / 23 | 22 | 10 | 17 / 20 |

Обычные Capture и Retrieval находятся на ориентире 20. Условные ветви
`capture-needed`, topic follow-up, cold recovery и один background retrieval
дают 22–23: это не постоянная routine нагрузка, а native coordinates, отдельная
topic boundary либо восстановление runtime. Новых стадий или references ради
счётчика не добавлено.

## Что стало выводимым

- per-field payload/schema, формат и atomicity принадлежат `chat_capture.py`;
- конкретные search flags и coverage-каталоги принадлежат `chat_digest.py`;
- parser `topics.md` общий для Capture и Retrieval; topic score не входит в
  holder score, а retired boundary не допускается;
- transcript subcommands принадлежат runtime `chat_recall.py`;
- повторения запретов, optional stages и authoring bureaucracy сняты.

Остались links на helpers и способ их запуска: `python3` для Capture/transcript,
`uv run --locked --script` для PEP-723 digest. Без этого чистый агент не имеет
исполняемого runtime path. Hybrid bootstrap условен: только diagnostic, затем
одна попытка либо lexical fallback; занятая hybrid queue завершается явной
ошибкой после ограниченного deadline, без обхода очереди dense-поиском.
