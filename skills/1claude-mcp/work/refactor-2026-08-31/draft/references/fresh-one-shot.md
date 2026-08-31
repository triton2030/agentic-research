# Fresh Opus One-shot

Вход: immutable one-shot call envelope. Выход: один raw `CallToolResult` либо
typed invocation failure.

## Протокол поведения

По протоколу `1skill-creation` коррекция владельца сохранена дословно:

<!-- rumdl-disable MD013 -->

> Мы ещё сделали его не блокирующим, но на самом деле это не всегда обязательно, если работы паралельной нет и ждём только опуса, то тогда надо дать агенту возможно запускать через блокирующий режим, чтобы агент просто ничего не делал пока опус работает

<!-- rumdl-enable MD013 -->

1. Выполни подготовленный `mcp__claude_mcp__claude_ask` ровно один раз.
2. Верни raw packet без содержательной интерпретации в body для acceptance.
3. Tool receipt, progress или accepted transport не заменяют raw result.
