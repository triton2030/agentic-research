# Итоговая проверка `candidate-v6`

## Outcome

`candidate-only · approval gate not passed · official unchanged`

`candidate-v6` доказанно проще действующего пакета и лучше ведёт себя в
matched clean probe, но два независимых checker-а не дали безусловный `pass`
точной финальной версии. Поэтому tracked owner, projections и live не
перезаписывались и exact approval на установку не запрашивается.

## Точные артефакты

- Candidate: `../../versions/v6/**`, 4 файла.
- Fingerprint алгоритм: относительный путь, `NUL`, байты файла, `NUL`; файлы
  сортируются по относительному пути; SHA-256.
- Candidate fingerprint:
  `56201757fbd2cbc04ac1ff7ac30f53cf963e01e3e9225ce876f6998102bf1075`.
- Commander's intent: `commander-intent.md`.
- Карта сохранения и простоты: `preservation-map-v6.md`.
- Clean-room reimplementation: `../../versions/cleanroom-candidate/**` и
  `cleanroom-trace.md`; старый
  пакет не был входом исполнителя. Fingerprint четырёхфайлового clean-room
  draft: `596d32ac641ce468cc277428cb621a780f96c69f9b722812244e1176bd5dc062`.
- Review receipts: `review-v6-cycle-1.md` и `review-v6-cycle-2.md`; финальный
  repeat проверял fingerprint candidate выше.
- Matched probe: `probe-baseline-output/**` и `probe-candidate-output/**`.

Контроллер `1skill-creation` был задан владельцем с fingerprint
`9bf11f64b436d313d979cba822b684f502e8e40e5f15a12f78cbd914ca29a518`.
Локально воспроизводимый fingerprint его полного installed package по
описанному выше алгоритму —
`519668f6edd15948099d362dce902126f7e5e7923a226188c244f883ed6b2139`;
алгоритм owner fingerprint не был задан, поэтому равенство не утверждается.

## Сохранённая функция и простота

Полная адресная карта находится в `preservation-map-v6.md`. Действующий
portable runtime содержит 10 Markdown-файлов и 323 строки; candidate содержит
3 instructional Markdown-файла и 104 строки. С учётом Codex metadata полный
пакет сокращён с 11 до 4 файлов, references — с 8 до 1, agents остаются 1 → 1.

Удалены самостоятельные стадии intent, zones, placement, assembly, wording,
budget, probe и finish. Intent, placement, assembly и wording поглощены целью,
уникальным контекстом и шестью decision boundaries root; budget, causal probe,
approval и install объединены в один post-candidate verification contract.

Оставшаяся сложность оправдана наблюдаемым вредом:

- шесть root boundaries не дают угадать владельца, принять текст за evidence,
  дублировать truth, потерять hard line или записать непроверенную версию;
- один verification reference отделяет правдоподобный текст от причинного
  evidence и exact authority;
- один clean scout нужен только при неизвестном владельце или непроверенном
  межзонном ребре, где автор иначе подтверждает собственную догадку;
- Codex metadata сохраняет существующую runtime/UI поверхность.

## Independent checks

Два независимых checker-а провели initial check и два полных repeat-а. В первых
двух циклах локально исправлены trigger, hard-line allowlist, clean-scout gate,
`no-change` evidence, verification input/output/trigger, wording о механическом
дроблении, UI prompt и карта адресов. Четырёхфайловая форма не расширялась.

На точном финальном fingerprint остались два возражения:

1. Literal checker: `verification artifact` и `verification receipt` не задают
   достаточно явно единое типизированное состояние candidate/pass/installed;
   чистый install-only исполнитель может не доказать, что устанавливает те же
   байты и читает актуальную authority.
2. Trajectory checker: заявленные 20 active units verification-пути зависят от
   слишком крупной атомизации controlled trial; при более мелком чтении предел
   может быть превышен.

Заявленные counts после literal-а: ordinary authoring 15 active, clean scout
15, verification 20, install-only 11, Codex invocation 1 active. Первые два и
install-only не оспорены; verification count не имеет общего checker consensus.

## Matched clean probe

Оба слепых arm-а сохранили pricing veto, локальную backend hard line
`make schema-check`, не создали правило для человеческого README-пути и
предложили менять только `frontend/AGENTS.md`.

Baseline прошёл все восемь runtime stages, запускал несколько scouts и
предложил frontend active path из 13 единиц. Candidate не запускал ненужный
scout, предложил один условный маршрут к `specs/pricing.md` и дал 4 единицы на
том же пути. Во вложенной прямой пробе baseline открыл нерелевантный
`specs/analytics.md`, а candidate — нет; оба дошли до veto.

Порядок основной трассы частично self-reported, но тексты предложений, прямые
выходы временных деревьев и сохранение veto наблюдаемы. Long-trajectory
retention не проверен.

## Механические и семантические проверки

- `quick_validate.py`: pass.
- `qv-skill`: pass.
- `sync_simple_projections.py 1instruction-authoring --check`: все tracked и
  installed projections соответствуют текущим owners.
- `md check --paths ../../versions/v6 --json`: 3 targets, 0 issues.
- `git diff --check`: pass на момент финализации.
- Все три Markdown description — короткий English `Use when ...` trigger-only;
  Codex `short_description` — English trigger-only, 64 символа.
- Instructional body трёх Markdown-файлов — русский; English оставлен только в
  технических токенах. Оба самостоятельных содержательных дочерних контракта
  имеют локальный раздел `## Цель`.
- Semantic edge review status for `candidate-v6`: 2 body links valid/support,
  0 affected/stale, 0 unread. Scout владеет independent unknown-edge lookup;
  verification владеет causal/authority gate.

Строгий `1chat-recall --check` всего корпуса возвращает существующий общий
`repair-backlog-present`; актуальная коррекция владельца отдельно найдена по
точному адресу `_ops/chat-recall/2026-08-29-184951-codex-01a04dbd.md:21`.

## Official byte guard

Начальные и финальные fingerprints этой перепроверки совпадают:

| Дерево | Файлы | SHA-256 |
| --- | ---: | --- |
| `skills/shared/1instruction-authoring` | 11 | `ceb4c69a9fcb22a9f5d3674ef50776ec7a2454e02072378d527427e9dc70ca93` |
| `skills/claude/1instruction-authoring` | 10 | `5edfb217899522187e2f1340bc82b2be2df0753c3c17878f49449cf868d5a33b` |
| `~/.claude/skills/1instruction-authoring` | 10 | `5edfb217899522187e2f1340bc82b2be2df0753c3c17878f49449cf868d5a33b` |
| `skills/codex/1instruction-authoring` | 11 | `07c6fffae9681ab3e2bf61872955b7b0d2c9e8903be4a9ee6770d8c626e923fa` |
| `~/.codex/skills/1instruction-authoring` | 11 | `07c6fffae9681ab3e2bf61872955b7b0d2c9e8903be4a9ee6770d8c626e923fa` |

Эти деревья уже были dirty до текущей перепроверки; byte guard доказывает, что
она не добавила к ним изменений, а не что Git worktree чист.

## Gaps и точная потребность

Нужен один новый ограниченный review cycle на той же четырёхфайловой форме,
без новых стадий и references:

1. одним типизированным verification artifact снять неоднозначность
   candidate/pass/installed и same-byte authority;
2. переописать controlled trial более высоким intent либо доказать единый
   atomization rule так, чтобы verification path имел честный предел ≤20;
3. выполнить long-trajectory probe;
4. заново получить два независимых безусловных `pass` на одних exact bytes.

Только после этого уместны unconditional exact approval, синхронизация и
установка. Сейчас установка не разрешена доказательствами.
