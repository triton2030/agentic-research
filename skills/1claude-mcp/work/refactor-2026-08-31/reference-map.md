# Карта режимов и reference-файлов — после wave 1

| Режим | Наблюдаемый вход | Выход | Консервативная оценка единиц |
| --- | --- | --- | ---: |
| Router | Skill выбран по `description`. | Ровно один применимый режим либо stop. | 17 |
| Fresh one-shot | Нужен один ответ; независимой работы до него нет. | Terminal Opus packet либо typed failure. | 15 |
| Parallel one-shot | Нужен один ответ; полезная работа Codex остаётся. | Terminal Opus packet либо один diagnostic. | 18 |
| Session control | Нужен follow-up, steer, status/liveness или stop известной Opus session. | Одно действие и typed state/result того же native ID. | 16 |
| Existing-session inspection | Владелец просит list/read активной Claude session. | Один read-only bounded result без Opus attribution. | 7 |
| Failure recovery | Уже есть exact typed failure packet. | Одна recovery action либо честный stop. | 17 |

Уникальный контекст и цели router-а не входят в двадцать единиц по контракту
`1skill-creation`; пять дословных owner-methods считаются пятью отдельными
единицами и сохранены по прямому требованию `behavior-protocol.md`.

## Самостоятельность

- Каждый reference выполняется по телу, одному названному файлу и входному
  артефакту: brief, native ID/state либо typed failure packet.
- Reference возвращает свой terminal output в body и не требует чтения другого
  reference; новый режим начинается только отдельным решением root.
- Exact normal/parallel tool invocation дублируется намеренно: объединение
  заставило бы один reference вызывать другой и нарушило бы cognitive-mode seam.
