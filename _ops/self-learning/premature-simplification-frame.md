# Premature Simplification Frame

## Observation

Когда пользователь говорит "слишком сложно" про живой tool/backend, модель
может преждевременно принять рамку "сократить/удалить функции" вместо проверки
реального consumer contract. Это ведёт к неправильному аудиту: считать частоту
и размер раньше, чем понять, какие скилы завязаны на функционал.

## Counter

- 2026-05-22 [GPT-5.5]: в аудите `md-embedding-server` я сначала вывел
  staged shrink вокруг меньшей public surface; пользователь поправил, что
  функции нужны разным скилам и v2 должна сохранить привычное использование
  `1md-navigator`, `1md-graph` и `1strategy` через замену backend-ссылки.

## Possible upgrade

Для "меньше кода" в tool/backend сначала строить consumer map: какие skills,
hooks, CLI fallback и runtime registrations зависят от функций. Только после
этого обсуждать внутреннее упрощение.
