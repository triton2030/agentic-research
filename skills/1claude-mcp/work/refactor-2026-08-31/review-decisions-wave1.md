# Решения по проверке — волна 1

Версия волны: первый полный draft до структурных исправлений reviewers.

## Принято

| Находка | Решение и evidence |
| --- | --- |
| Файлы превышают 20 самостоятельных единиц | Принято по `1skill-creation/SKILL.md`: runtime-дубли убираются, fresh one-shot и existing-session read получают самостоятельные режимы, session/recovery переписываются ниже 20. |
| Нет exact MCP tool name и `requested_effort` | Принято по callable schema текущего host и `behavior-decisions.md`; exact fields входят в fresh/parallel terminal gate. |
| Session control не требует affirmative Opus evidence | Принято по owner Opus-only решению и `src/claude-result.js:33-35`; resume/send/steer и success fail-closed без Opus evidence. |
| `description` двусмысленен и не покрывает inspect/list | Принято; новая строка различает non-Opus Claude boundary и inspection/control, оставаясь ≤200 символов. |
| Goals и recovery ошибочно пронумерованы | Принято по правилу `1skill-creation`: goals/recovery становятся маркерами, последовательные one-shot шаги остаются numbered. |
| Agent-authored one-shot повторяет intent | Принято частично: выводимые действия удаляются из runtime steps; дословный блок сохраняется по прямому требованию `behavior-protocol.md`. |
| Неверные адреса owner evidence | Принято по `nl -ba` исходного holder: clean launch `:19-21`, чтение `:20`, Goal/Context `:22`, лимит `:23`. |
| Нет deletion-test каждого элемента контекста | Принято по `goal-context.md`; добавлена адресуемая таблица. |
| Нет property falsifiers | Принято по роли reviewer; `cut.md` получает цепочки decision/evidence/property/falsifier. |
| Project-specific billing path | Принято по корневому правилу global artifact: runtime dependency удаляется, owner остаётся source evidence вне установленного пакета. |
| Fresh-task recovery звучит как разрешение создать task | Принято по scope: recovery только предлагает владельцу fresh task и не действует автоматически. |

## Отклонено

| Рекомендация | Причина |
| --- | --- |
| Удалить дословный блок «Протокол поведения» из runtime-скила | `behavior-protocol.md` требует записать именно потребованный владельцем способ в этом разделе дословно и запрещает сокращать без согласия. Дублирующая агентская проза снимается, но owner text остаётся. |
| Скопировать billing guidance в package-relative reference | Это создаст второй owner billing truth вопреки `experiments/claude-bridge/AGENTS.md`; безопасный runtime default — fail-closed typed report без локального path. |
