# Recovery после обрыва root

Вход: оборвалось окно root. Выход: волна восстановлена из адресуемого state
либо зависимая ветка получила final blocker.

- Выбери адресуемый state: живой task-file с evidence-адресами, иначе созданный
  carrier; нет обоих → `UNKNOWN`/final blocker без переиздания external actions.
- Сверь записанный state с surviving artifacts и live runtime state.
- Переиздай только непринятые потоки.
- Не повторяй external action без доказанного статуса прежней попытки.
- Outcome recovery запиши в task-file или carrier.
- Продолжай от записанного перехода, не от памяти чата.
- Tool-specific wait, follow-up и lifecycle оставь live runtime owner-у.
