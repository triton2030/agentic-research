# Brief окна

Вход: root прочитал карту влияющих owners. Выход: сформирован provisional
self-contained brief, достаточный для первого решения.

- `goal/outcome` — какое состояние должен сделать истинным этот поток.
- `done_when` — все критерии принятия и требуемое evidence.
- `read` — live-адрес каждого влияющего owner-а и причина чтения.
- `delta` — только task-specific факты и границы, которых нет в owners.
- `write ownership` — единственный носитель записи или read-only.
- `return` — результат · адресуемое evidence · gaps · blockers.
- Не пересказывай в prompt содержание доступного owner-файла.
