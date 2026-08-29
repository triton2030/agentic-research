# Trigger probes — round 1 — 2026-08-29

Exact candidate description проверена изолированно по names/descriptions only:
current GPT runtime через clean non-fork agent и Claude `claude-opus-5` через
fresh `claude_ask`; writes/tools были запрещены.

| Bare phrase, 5–10 слов | GPT | Claude Opus 5 | Expected |
|---|---|---|---|
| Работа идёт, продолжай по текущему плану | none | none | not yet |
| Долгая работа дошла до развилки траектории | 1fresh-eyes | 1fresh-eyes | use |
| Запусти свежие глаза: куда двигаться дальше | 1fresh-eyes | 1fresh-eyes | use |
| Используй auditor для проверки заявленной готовности | 1fresh-eyes | none | use |
| Исправь локальный отступ в этом компоненте | none | none | skip |
| Найди пробел между фреймворком и реализацией | none | none | skip |
| Дай независимое мнение Claude по решению | 1claude-mcp | 1claude-mcp | near-miss |
| Проведи один premortem этого решения | 1fresh-eyes | 1fresh-eyes | named use |

Обе семьи правильно переключили first phrase → second phrase из `not-yet` в
`use-now` по появлению наблюдаемой развилки.

Finding: Claude не вывел доступность `auditor` из generic `specialist profile`.
Decision: description теперь называет `auditor` как пример профиля; probe
повторяется по точной исправленной версии.
