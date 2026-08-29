# Brief окна

Вход: root прочитал owner map. Выход: сформирован provisional
self-contained brief, достаточный для первого решения.

- `goal/outcome` — состояние, которое должен сделать истинным actor.
- `done_when` — evidence, которое доказывает outcome.
- `read` — адреса принятого owner ledger-а.
- `delta` — только task-specific информация, отсутствующая в owners.
- Доступный owner не пересказывай; требуемая live receiving owner-ом выдержка
  сохраняет адрес и считается в active set.
