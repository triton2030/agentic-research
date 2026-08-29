# Durable carrier без живого плана

Вход: delegation допущена без живого плана, а потеря root-контекста стоит
дороже переиздания волны. Выход: создан достаточный носитель холодного
продолжения.

- Создай `<корень проекта>/_workspace/orchestration/<дата-слаг>/`.
- Добавь этот маршрут в `.gitignore`, если проект ещё не исключает его.
- В `context.md` запиши зачем, цель, границы и runtime/session handles.
- Для каждого потока запиши outcome, worker, brief, active-unit estimate,
  return/artifact, write ownership и status
  `pending|running|returned|accepted|repair|blocked`.
- Запиши обязательный барьер и следующий разрешённый ход.
- Запиши адрес live acceptance owner-а и принятое evidence.
- Запиши unresolved conflicts и blockers.
