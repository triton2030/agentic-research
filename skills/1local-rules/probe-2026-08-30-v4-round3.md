# Реалистичная проба v4 · финальный раунд

Чистый исполнитель подтвердил SHA-256 переданных bytes:
`eb262405dccb9250a53d58ed3870445299cc6df9f50601a6093932dfa0fc030d`.
Он не читал history и выводы checker-ов и не выполнял реальные записи.

## Trigger checks

- Use: «Сделай обычный skill локальным `2*` для этого проекта сразу в Claude и
  Codex» → `1local-rules`.
- Skip: «Создай обычный глобальный skill для всех проектов» → только
  `$1skill-creation`.
- Near-miss: «Обнови приватный Claude-only skill этого проекта» → skip, потому
  что назначения для обеих сред нет.

## Update trace

Исполнитель разрешил владельца, обе проекции и project sync mechanism до
`$1skill-creation`. Он передал четыре локальных ограничения, остановил writes
без точного утверждения, а в условной ветке после approval связал его с exact
bytes, проверил conflict, использовал одну owner→projections установку и вернул
topology basis/mechanism, approval, три адреса, instruction sources и recursive
parity. Runtime-owned `agents/openai.yaml` сохранил вне переносимой поверхности.

## Retire trace

Case не называл authority route для снятия, поэтому фактический результат —
blocker до удаления. В условной ветке с применимым authority source исполнитель
получил бы exact approval отсутствия, удалил три поверхности без content-
conflict gate и вернул topology, approval и direct absence checks.

## Остатки

- Связь single install с разрешённым sync mechanism выводится из creator и
  project contract, но не названа отдельным императивом.
- Recovery после частичного сбоя принадлежит project mechanism и не задан
  candidate-ом.
- Retire-квитанция возвращает approval, но отдельно не называет instruction
  source, установивший полномочия approving party.

Проба не заявляет реальные project files, approval, sync, conflict, parity или
absence: единственное прямое filesystem evidence — hash candidate-а.
