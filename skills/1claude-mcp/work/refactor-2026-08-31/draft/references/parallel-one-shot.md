# Parallel Opus One-shot

Вход: immutable one-shot call envelope и полезная независимая работа Codex.
Выход: один raw result либо один transport diagnostic, адресованный opaque ref.

1. В одной `functions.exec` cell запусти Promise ровно одного подготовленного
   `mcp__claude_mcp__claude_ask`.
2. Верни `family: claude, phase: started`, вызови `yield_control()` и продолжи
   полезную локальную работу в root.
3. Та же cell ждёт исходный Promise; не открывай session, не polling-уй, не
   запускай duplicate call и не повторяй отказ автоматически.
4. Любой returned `CallToolResult` сохрани без интерпретации под `result_ref`;
   cell/transport exception сохрани под `failure_ref`.
5. Ровно один terminal `notify()` сообщает соответствующий status и opaque ref.
6. После wake загрузи ровно этот ref: result верни в body для acceptance, а
   diagnostic — для recovery.
