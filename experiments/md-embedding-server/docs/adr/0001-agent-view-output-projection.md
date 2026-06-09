---
description: 'ADR-0001: agent-view проекция вывода md CLI — bounded-by-default + прогрессивное
  раскрытие.'
depends-on:
- '[[../architecture-lock.md]]'
---
# ADR-0001 — Agent-view проекция вывода

- **Статус:** Accepted
- **Дата:** 2026-05-31

## Контекст

Вывод `md`-инструментов раздувался линейно с размером корпуса: на 2000-файловом
корпусе `md orient` = 502 КБ, `md ls` = 884 КБ, `md status` и `md search` ≈ 30 КБ.
Это рвёт контекст агента-потребителя — ради которого инструмент и вызывают.

Причина системная: «лестница контекста» ограничивала только **глубину** (тела за
`--expanded`), но не **ширину** (число строк) и не **утечку движковых полей**
(`rowid`, `content_hash`, полный `body`, сырые `bm25`/`dense` скоры). Флаги вида
называли непоследовательно (`map_only` / `content_included` / `expanded`), а
`read_next` дублировал «леса» на каждой строке (до 44% веса `orient`).

## Решение

Единая **agent-view проекция** из двух слоёв:

1. **Центральный pass** `md_cli.envelope.project_payload`, вызываемый из `wrap()`
   до оценки размера: денилист `INTERNAL_FIELDS` (`rowid`, `content_hash`) везде
   кроме `_envelope`; относительные пути против `corpus_root` (якоря —
   `root`/`corpus_root`/`index_path` — остаются абсолютными); схлоп
   `map_only`/`content_included` в один `view` (`map`/`expanded`).
2. **Поинструментные шейперы** (в navigator-слое) выбирают поля и сворачивают:
   `orient` → `start_here` + `owner_docs` + folded `shape`; `ls` → folded
   `summary` + bounded top-N; `status` → headline + `recommended_action`;
   `search` → lean-строки + `render`.

Жёсткие инварианты:

- **Прогрессивное раскрытие без тупиков:** всё, что прячет bounded-дефолт,
  достижимо через `--expanded` или `read_next`.
- `read_next` — один payload-level канал, не per-item.
- Проекция трогает только `result`, никогда `_envelope` (поэтому
  `recommended_action` гарантированно сохранён); `runner` остаётся единственным
  владельцем `envelope.wrap` и JSON-печати.

## Последствия

- `SCHEMA_VERSION` → `4.0.0` (удаление полей) — детали в CHANGELOG 3.0.0.
- Размеры на корпусе MAVO: `orient` 502→7 КБ, `ls` 884→22 КБ, `status` 30→2 КБ.
- Проверено consumer-simulation + adversarial агентами на живом корпусе:
  недостижимых полей нет; задачи решаются на bounded-дефолте.
- Skill-доки (`1md-navigator`/`1md-graph`) регенерированы из catalog;
  `engine-internals.md` обновлён под новую форму строки `search`.
- **Известный долг:** `md ls` ещё держит top-50 строк (≈ 22 КБ); `start_here`
  топологичен (PageRank), а не под намерение задачи — task-relevance закрывает
  связка `orient` → `md search`.
