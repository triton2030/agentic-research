# Сообщение receiver-у

## Цель

Дай умному receiver-у bounded commander intent, а не процедурную карточку.

Начинай receiver prompt ровно с `# Контекст`, следующим разделом ставь `# Цель`.

`# Контекст` передаёт operation context, current truth и source addresses;
top-level decisions остаются root.

`# Цель` называет один bounded outcome и observable done.

Добавляй дополнительную секцию только при concrete harm от её отсутствия.

Не включай typed envelope, recursive controller invocation — включая
`$1codex-bg-threads` и `1orchestration` — или authority над visible background
fleet.
