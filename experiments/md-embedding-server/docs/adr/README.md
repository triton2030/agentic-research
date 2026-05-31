---
description: "Architecture Decision Records (ADR) для md-embedding-server: индекс и практика."
read-before-edit: []
edit-after-edit: []
---
# Architecture Decision Records

ADR фиксирует одно значимое архитектурное решение: контекст, само решение и
последствия. Формат — облегчённый Nygard. Решения иммутабельны: если решение
меняется, не редактируем старый ADR, а добавляем новый со статусом
`Superseded by ADR-NNNN`.

Статусы: `Proposed` / `Accepted` / `Superseded by ADR-NNNN` / `Deprecated`.

Заводи ADR, когда решение меняет архитектурную границу, публичный контракт,
формат agent-facing вывода или миграционный путь. Мелкие правки — в код и
CHANGELOG, не сюда.

Это канонический дом архитектурных решений проекта. История v2-миграции живёт в
`docs/refactor-plan/decision-log.md` (D-001…D-005) — лог эпохи миграции,
сохранён для истории; новые решения идут сюда.

## Индекс

- [ADR-0001](0001-agent-view-output-projection.md) — Agent-view проекция вывода
  (bounded-by-default + прогрессивное раскрытие без тупиков). **Accepted.**
- [ADR-0002](0002-extract-rederives-headings.md) — `md extract` до-читывает
  headings с диска (развязка от формы карты). **Accepted.**
- [ADR-0003](0003-markdown-io-canonical-parser.md) — `markdown_io` —
  канонический парсер Markdown-ссылок. **Accepted** (консолидация `graph_edges`
  pending).
