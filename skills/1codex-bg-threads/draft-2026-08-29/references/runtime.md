# Live runtime тредов Codex

## Цель

Выполнить native lifecycle по текущему host contract, не превращая датированный
snapshot в API и не имитируя отсутствующую capability.

Открывай непосредственно перед первым native thread action либо когда не
доказаны tool name, schema, handle, state, model или environment.

## Порядок истины

1. Live callable schema текущего host владеет tools, arguments, enums и
   доступностью; используй только returned IDs.
2. Актуальная официальная документация владеет понятиями и публичным
   lifecycle.
3. Merged OpenAI Codex source владеет runtime-инвариантом, которого ещё нет в
   документации; open issue доказывает только риск.

Отсутствующее действие возвращает capability gap. После ambiguous mutation
сначала выполни read-after-write с тем же identity; не угадывай вызов и не
заменяй visible thread same-thread subagent-ом.

## Capability snapshot

- `create`, `resume`/follow-up и `fork` выбираются соответственно для нового
  identity, продолжения прежнего и history-развилки.
- `steer` корректирует active turn, когда доступен live.
- `wait` наблюдает события по live cursor/target contract.
- `goal` хранит objective долгой самостоятельной работы, когда доступен live.
- `metadata`, `archive` и `unarchive` управляют persisted title, pin и
  lifecycle, когда доступны live.
- Returned thread ID доказывает identity; title и summary только находят
  кандидата.
- Queued client handle не передаётся операции, которой нужен thread ID.
- Exact pair текущего запроса побеждает default; отсутствующая pair возвращает
  model gap, а отсутствующая native capability — capability gap.
- Только буквальный запрос вернуть handle является launch-only; обычный вызов
  skill остаётся managed.

## Официальные источники

- [Codex App Server](https://learn.chatgpt.com/docs/app-server) — thread,
  turn, goal, metadata и archive lifecycle.
- [Long-running work](https://learn.chatgpt.com/docs/long-running-work) —
  длительная работа и наблюдение.
- [Git worktrees](https://learn.chatgpt.com/docs/environments/git-worktrees) —
  Local, Worktree, Handoff и сохранение checkout.
- [GPT-5.6 model guidance](https://developers.openai.com/api/docs/guides/latest-model)
  — роли Luna/Sol и reasoning efforts.
