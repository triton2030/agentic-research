# Среда треда

## Цель

Выбрать среду с минимальной координационной ценой и без конфликта записи.

Открывай после capability snapshot и до `THREAD_CARD`.

- Read-only scope выполняется Local.
- Непересекающиеся exact write paths выполняются Local.
- Same-file overlap сначала снимается single writer.
- Оставшийся same-file overlap сначала пробуется сериализовать.
- Worktree разрешён только для доказанного overlap, который не сняли два
  предыдущих правила.
- Worktree verdict называет starting state, exact overlap и pre-existing
  changes.
