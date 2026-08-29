# Bounded repair stalled return

Читай в любом режиме после первого bounded wait без изменения заранее
названного `return/artifact/diff`. Progress report material delta не является.

Сделай один read-only probe носителя режима:

- Delta нет → верни `UNKNOWN`/blocker и останови только зависимую ветку; новое
  окно не создавай.
- Delta есть, но возврат не принят → один repair прогретому worker-у.
- Если root и карта волны живы, но runtime не позволяет продолжить того же
  worker-а, замени только незавершённый поток; замена считается текущей
  попыткой repair.
- Повторный repair выполняет свежее окно. Нет принятого возврата после него →
  запиши final blocker и переход, останови зависимую ветку; третьего repair нет.
- Outcome probe/repair запиши в живой task-file, созданный carrier или отчёт
  волны в чате.
- Tool-specific wait, follow-up и lifecycle оставь live runtime owner-у.
