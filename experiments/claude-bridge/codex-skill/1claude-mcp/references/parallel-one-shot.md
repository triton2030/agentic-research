# Parallel Opus One-shot

Вход: immutable one-shot call envelope и полезная независимая работа Codex.
Выход: один task-scoped opaque outcome ref.

1. В одной `functions.exec` cell запусти Promise ровно одного подготовленного
   `mcp__claude_mcp__claude_ask`.
2. Вызови `yield_control()` и продолжи полезную локальную работу в root.
3. Эта cell владеет единственным Promise до settlement; отказ не повторяется.
4. Любой returned `CallToolResult` сохрани без интерпретации под `result_ref`;
   cell/transport exception сохрани под `failure_ref`.
5. Ровно один terminal `notify()` сообщает outcome status и opaque ref.
6. После wake загрузи ровно этот ref: result верни в body для acceptance, а
   diagnostic — для recovery.
