# Fresh Opus One-shot

Вход: immutable one-shot call envelope. Выход: один raw `CallToolResult` либо
typed invocation failure.

1. Выполни подготовленный `mcp__claude_mcp__claude_ask` ровно один раз.
2. Верни raw packet без содержательной интерпретации в body для acceptance.
3. Tool receipt, progress или accepted transport не заменяют raw result.
