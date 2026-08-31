# Terminal receipt — `candidate-v7`

## Outcome

`PASS · READY FOR EXACT APPROVAL · NOT INSTALLED`

Exact candidate сохранил четырёхфайловую форму, прошёл один blind same-settings
long-trajectory probe и две независимые проверки одних байтов без findings.
Owner, tracked projections и live в этой итерации не изменялись.

## Exact artifact

- Path: `skills/1instruction-authoring/versions/v7/**`.
- Files: 4.
- Fingerprint algorithm: для файлов в сортировке по относительному пути
  последовательно хэшируются `относительный путь · NUL · байты · NUL`.
- SHA-256:
  `b6dd5b397cc78d49b6edd7212a48bb021a7c6b41b6feec359b81aaeaf378b1ee`.
- Fingerprint совпал до probe, до и после обоих checker-ов и после финальных
  механических проверок.

## Provenance

### Owner criteria

- Русский instructional body и короткий English trigger-only description —
  `_ops/chat-recall/2026-08-29-163434-codex-01a04d4a.md:20`.
- Commander intent через цель и контекст умного агента — тот же holder, `:21`.
- Процесс не должен быть переусложнён — `:33`.
- Recheck нужно исправить до готовности по `1skill-creation` — `:35`.

### Verification contract repair-task

Четырёхфайловая форма, один blind same-settings long probe и две независимые
exact-byte проверки были критериями текущего repair-task. Они являются
контрактом доказательства этой candidate, а не прямой речью владельца.

## Complexity delta

| Surface | Current official | Candidate v7 |
| --- | ---: | ---: |
| Полный Codex package | 11 файлов | 4 файла |
| Instructional Markdown | 10 файлов / 323 строки | 3 файла / 104 строки |
| References | 8 | 1 |
| Agent contracts | 1 | 1 |

V7 не добавил ни файла, ни стадии относительно v6. Verification заменил
каталог trial-полей одним `single-blind matched controlled trial`, общим
immutable manifest и content-addressed package authority. Что удалено и какой
вред оправдывает каждый остаток, адресовано в `preservation-map-v7.md` и
`cut.md`.

## Active sets

Консервативный максимум двух независимых checker-ов:

| Режим | Active units |
| --- | ---: |
| Ordinary authoring | 15 |
| Clean scout | 15 |
| Verification | 20 |
| Install-only continuation | 20 |
| Codex invocation | 1 |

Literal full-file counts: root 16, scout 16, verification 27, Codex metadata 4.
Trajectory checker дал 19/18 для verification/install; terminal receipt берёт
большие значения 20/20. Условная installation boundary не активна в обычном
verification run, а trial уже материализован при install-only continuation.

## Two independent exact-byte checks

Оба clean-window checker-а пересчитали exact fingerprint до и после review, не
читали вывод друг друга и не редактировали candidate.

- Literal checker: counts `15 / 15 / 20 / 20 / 1`; `findings: none`.
- Trajectory checker: counts `15 / 15 / 19 / 18 / 1`; `findings: none`.

Полная квитанция: `review-v7-final.md`.

## Blind same-settings long probe

Оба arm получили один fixture и task, `gpt-5.6-terra`, reasoning `medium`,
`fork_turns=none`, read-only isolation и одинаковый dispatch contract. Opaque
package path и owned output path были единственными служебными различиями;
контролируемая содержательная переменная — assigned package. Arm label,
comparator и ожидаемый ответ исполнителям не передавались.

- Fixture fingerprint:
  `aaf7231d40ed8a6f500248b82b9f903d54ab0e533ed8c7498e6045caa5a2cc5f`.
- Task SHA-256:
  `6ec313e6488de7b62d444c200596dc4ce30bea3039e04a69da82c56c46548abf`.
- Current arm сохранил veto и authority, но после семи промежуточных решений
  назвал long retention непроверенным и посчитал адреса вместо смыслов.
- Candidate arm сохранил тот же veto и lawful non-use, связал ранний package
  hash с поздним approval mismatch, признал пройденную траекторию long evidence
  и вернул четыре независимо нарушимых смысла целевого пути.

Manifest, outputs, их hashes и ограничение одного run на arm находятся в
`probe-long-v7/manifest.md` и `probe-long-v7/verdict.md`. Один probe доказывает
возможность и отсутствие наблюдаемого вреда в holdout-case, но не
вероятностный сдвиг по распределению.

## Mechanical and language checks

- `quick_validate.py`: pass.
- `qv-skill`: pass.
- `md check`: 35 targets, 0 issues.
- `sync_simple_projections.py 1instruction-authoring --check`: current tracked
  и installed projections соответствуют их current owners.
- `git diff --check` и trailing-whitespace check: pass.
- Instructional body трёх Markdown-файлов — русский; English остаётся в
  технических терминах.
- Все Markdown descriptions и Codex `short_description` — короткие English
  `Use when ...` trigger-only тексты; `short_description` — 64 символа.
- Оба самостоятельных дочерних контракта имеют локальный раздел `## Цель`.

## Semantic edges

Знаменатель `candidate-v7`: ровно две body Markdown-ссылки, declared
`depends-on` отсутствуют.

1. Root требует clean scout только при неизвестном owner/edge; target владеет
   независимым поиском owner, consumers и coverage, не проектируя instruction.
   Слабая версия «generic research без unknown-edge boundary» отвергнута
   `agents/zone-scout.md:9-15,25-31`. Без ссылки author подтверждает свою
   догадку.
2. Root требует проверку exact candidate и stop на неположительном verdict;
   target владеет package identity, causal trial и exact authority. Слабая
   версия «generic quality review» отвергнута
   `references/verification.md:9-32`. Без ссылки plausible text получает pass
   либо official меняется по approval других байтов.

Semantic edge review status for `candidate-v7`: 2 body links valid/support,
0 affected/stale, 0 unread.

## Principles trace

Owner criteria на `…01a04d4a.md:20–21,33,35` задали язык, commander intent,
простоту и готовность. Четырёхфайловая форма и состав verification были
операционализированы repair-task contract, а не приписаны владельцу.
P-002/P-003 удержали smart-agent commander intent; P-004/P-005 поддержали
наблюдаемое evidence; P-007 оставил один candidate owner без параллельной
product truth. Контрпринципов, требующих вернуть процедуры или новый reference,
в прочитанных GOAL, Frame и P-001…P-008 нет.

## Official byte guard

Начальные и terminal fingerprints совпадают:

| Surface | Files | SHA-256 |
| --- | ---: | --- |
| Shared owner | 11 | `ceb4c69a9fcb22a9f5d3674ef50776ec7a2454e02072378d527427e9dc70ca93` |
| Claude tracked | 10 | `5edfb217899522187e2f1340bc82b2be2df0753c3c17878f49449cf868d5a33b` |
| Claude live | 10 | `5edfb217899522187e2f1340bc82b2be2df0753c3c17878f49449cf868d5a33b` |
| Codex tracked | 11 | `07c6fffae9681ab3e2bf61872955b7b0d2c9e8903be4a9ee6770d8c626e923fa` |
| Codex live | 11 | `07c6fffae9681ab3e2bf61872955b7b0d2c9e8903be4a9ee6770d8c626e923fa` |

Эти surfaces были dirty до перепроверки; byte guard доказывает отсутствие
новых official/live writes этой итерации, а не чистый Git worktree.

## Gaps and needs

- Distribution-wide probabilistic improvement остаётся `unknown`: verification
  contract требовал один long probe, а не resampling.
- Exact approval на fingerprint `b6dd5b…b1ee` отсутствует; установка не
  выполнялась в рамках repair-task verification contract.
- Для будущей установки нужен отдельный unconditional exact approval этого
  fingerprint; после него применяется existing owner-first sync и byte parity.

Других blocker-ов готовности candidate нет.
