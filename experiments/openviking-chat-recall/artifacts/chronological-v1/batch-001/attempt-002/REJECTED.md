---
kind: semantic-audit-verdict
batch: batch-001
attempt: 2
status: rejected
date: 2026-08-22
---

# Clean batch-001 attempt-002 — REJECTED

Candidate SHA-256:
`5b6d2a0e12df4f4a55273640b6f33621100cd8e718b67db7d3c84da2459f7701`.
Модель `gpt-5.6-luna`, thinking `max`, prompt `wiki-writer.v2.md`
(SHA `e5c4389374911239551f3157bce2b03e878dcd9981dae48a60831af856c8eeba`).
21 операция `create`: `index.md` + 20 страниц `concept`; 32/32 записи `used`.

Deterministic `--check-only` дал PASS. Это structural evidence, не semantic
acceptance — и в этот раз сам PASS оказался дефектным (см. M1).

## Независимый аудит: шесть осей, шесть FAIL

Веер read-only Codex-ревьюеров `gpt-5.6-sol/xhigh`, общий бриф
`../audit/BRIEF.md`, одна схема возврата, гейт на адрес источника.
Полные пакеты: `_workspace/codex-artifacts/20260822T0907*`.

| Ось | Вердикт | Ядро |
| --- | --- | --- |
| source-fidelity | FAIL | 9 major: потеряны точные отношения, сдвинуто время, соседняя тема втянута в ответ |
| owner-attribution | FAIL | 7: объективизация слов владельца, ослабление решения до упоминания, frontmatter holder-а в прозе |
| coverage-determinism | FAIL | blocker M1 + три пропущенные repetition groups |
| page-fit | FAIL | 3 blocker: один ответ разорван по двум страницам, одна страница несёт два вопроса |
| ia-findability | FAIL | blind 4/5; 4 страницы из 20 неверного типа (`method`/`entity` размечены `concept`) |
| route | FAIL | решение о page allocation принимается слишком поздно |

## Классы дефектов

**S1 · Page-allocation instability (родительский класс).** Attempt-001
переобъединил разные named subjects; attempt-002 разрезает один owner answer
по двум страницам (`owner-historical-capture` против `owner-quote-capture`;
`owner-skill-density` против `owner-embedding-duplicate-boundary`) и одновременно
склеивает два независимых вопроса в одну страницу (`owner-agent-metadata`,
`owner-embedding-duplicate-boundary`). Это один класс, а не два разных — иначе
механизм может бесконечно качаться между крайностями, не достигая stop rule.

**S2 · Дедупликация не сработала.** Заявлена одна repetition group на 32
записи; аудит нашёл ещё три:
`cr-92ba68ae02b88b40`+`cr-1d42692df43b815f`,
`cr-0c56f9b82f11ffc7`+`cr-9e42f2995175d537`,
`cr-9e42f2995175d537`+`cr-e0cc9eb95585f23d`.
Прямое следствие: неопознанный повтор получает собственную страницу.

**S3 · Attribution drift.** Слова владельца поданы как объективный факт
(«Скилл вызывают Codex, Claude и параллельные агенты»), решение ослаблено до
упоминания («назвал» вместо «решил, что будут использовать»), субъект смещён
(из другого проекта пришла цитата -> «инструмент может приходить из другого
проекта»), project-метаданные holder-а попали в прозу.

**S4 · Page-type drift.** `owner-quote-capture` — процедура (`method`);
`owner-playwright-parity`, `owner-codex-priority-flag`, `owner-reference-file` —
named things (`entity`). Все размечены `concept`.

## M1 · Дефект механического валидатора (исправлен)

Coverage содержал:

```json
{"record_id": "cr-07c5570aa291ce00", "disposition": "used",
 "reason": "Поддерживает material claim undefined на странице undefined."}
```

`used` без `page_path`, reason с незаполненным шаблоном — и `--check-only`
пропустил это, хотя `output_contract` требует `page_path` для каждого `used`.
Маршрут `запись -> claim -> страница` был необеспечен.

Исправлено в `scripts/materialize_chronological_changeset.py`,
`_validate_coverage`: `used` обязан нести `page_path`, совпадающий с операцией,
которая реально использует запись; `reject`/`skipped` не могут нести page path.
Регрессия закреплена тестом
`tests/test_materialize_chronological_changeset.py::test_used_coverage_requires_matching_page_path`.
Прямой прогон исправленного валидатора против этого кандидата:
`used coverage is missing page_path for cr-07c5570aa291ce00`.

Правка меняет materializer SHA, поэтому следующий batch обязан получить новый
manifest с обновлённым binding.

## Диагностика объёма

10 079 байт исходных цитат -> 27 379 байт кандидата (x2,72); holder-файлы
целиком — 20 726 байт. Числовой compression gate снят владельцем и здесь не
применяется как условие приёмки; замер приложен как диагностика направления.

## Статус

Wiki и receipt не материализованы. Этот artifact — immutable failure evidence,
не semantic prior и не repair target. Ручное исправление запрещено.

Stop rule `task.md` сработал: два последовательных FAIL одного класса (S1)
после prompt bump опровергают prompt-only route. Третий полный changeset без
изменения механизма не запускается.
