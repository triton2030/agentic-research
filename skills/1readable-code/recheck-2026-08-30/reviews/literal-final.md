# Буквальная проверка exact candidate

## Verdict

`findings: 2`. Candidate не проходит буквальную проверку без двух минимальных
локальных правок формулировки; бюджет, routing boundary, язык, ссылки и
candidate-only gate проходят.

## Exact версия

- `candidate/SKILL.md` SHA-256:
  `361faf00c670aa1e2e631c1d09b408c4aa5b3669d1f924f40cd2080c081989e4`.
- `candidate/agents/openai.yaml` SHA-256:
  `64f664e75d2254dace69065ffb86e887b36a0258f42f25cbebcaead75ea83f0d`.
- Оба SHA повторно проверены непосредственно перед записью этого receipt.

## Фактически прочитанный scope

Полностью прочитан текущий пакет `/Users/triton/.codex/skills/1skill-creation/`:

- `SKILL.md`;
- `references/agent-defaults.md`;
- `references/behavior-protocol.md`;
- `references/check-approve.md`;
- `references/goal-context.md`;
- `references/install-approved.md`;
- `references/refactor.md`;
- `references/reference-files.md`;
- `references/skill-short-description.md`;
- `agents/check-instructions.md`;
- `agents/check-trajectory.md`;
- `agents/openai.yaml`.

Полностью прочитаны оба файла exact candidate:

- `recheck-2026-08-30/candidate/SKILL.md`;
- `recheck-2026-08-30/candidate/agents/openai.yaml`.

Полностью прочитана вся папка истории в составе, существовавшем до записи
этого независимого review:

- `origin.md`, `cut.md`, `evidence.md`;
- `draft-2026-08-29/SKILL.md` и `draft-2026-08-29/agents/openai.yaml`;
- `draft-2026-08-29/map.md`, `draft-2026-08-29/reviews.md`;
- `draft-2026-08-29/receipts/clean-run.md`;
- `draft-2026-08-29/receipts/installed-routing.md`;
- `draft-2026-08-29/receipts/installed-routing-after-reference-pass.md`;
- `recheck-2026-08-30/intent.md`;
- `recheck-2026-08-30/authoring-map.md`;
- `recheck-2026-08-30/preservation-map.md`;
- `recheck-2026-08-30/clean-room-semantic-draft.md`;
- `recheck-2026-08-30/reconstructed/SKILL.md`;
- `recheck-2026-08-30/reconstructed/agents/openai.yaml`.

Полностью прочитаны три названных owner-source:

- `_ops/chat-recall/2026-08-29-153512-codex-01a04d13.md`;
- `_ops/chat-recall/2026-08-29-163434-codex-01a04d4a.md`;
- `_ops/chat-recall/2026-08-30-130004-codex-01a051ac.md`.

Для применимого project context также полностью прочитаны
`_ops/product-frames/agentic-research.md`,
`_ops/product-frames/agentic-research.principles.md`,
`/Users/triton/.codex/skills/1chat-recall/SKILL.md` и его
`references/retrieval.md`. Выводы других текущих checker-ов не читались.

## Самостоятельные units candidate

### `candidate/SKILL.md` — 20 units в полном runtime-union

1. Использовать перед написанием кода.
2. Использовать перед изменением кода.
3. Функция вызова — стратегический взгляд на будущую систему.
4. При выборе контракта в Claude дополнительно использовать `codebase-design`.
5. При выборе контракта в Codex дополнительно использовать `1codebase-design`.
6. Task focus скрывает форму будущей системы, цену изменений и
   CTO/architect view как один причинный contextual gap.
7. Три named practices являются handles уже известного знания, а не учебником.
8. Текущая цена оправдывается более дешёвыми следующими изменениями.
9. Анализ без материальной будущей цены и стратегической неопределённости
   объявлен ритуалом.
10. Внешний взгляд допустим только при оставшейся материальной стратегической
    неопределённости либо прямом запросе владельца.
11. До программирования подход оценивается из будущего системы, а не только из
    текущей задачи.
12. Код остаётся цельным.
13. Вероятная будущая правка остаётся локальной.
14. Вероятная будущая правка остаётся читаемой.
15. Оставшаяся материальная стратегическая неопределённость вызывает одного
    свежего субагента.
16. Прямой owner-request вызывает одного свежего субагента.
17. Субагент оспаривает подход с позиции будущей системы.
18. Сильнейшее обоснованное возражение о стабильности или сопровождаемости до
    правки либо снимается изменением подхода, либо опровергается фактами.
19. Если материальная будущая цена изменила подход, после правки проверяется
    снятие той же цены.
20. Отдельный отчёт не требуется.

Пункты 6 и 7 считаются по одному: их составные части объясняют один выбор и не
создают независимых действий. Альтернативы пункта 18 являются двумя способами
закрыть одну обязанность, а не двумя одновременно действующими обязанностями.

### `candidate/agents/openai.yaml` — 3 UI units

1. `display_name`.
2. `short_description`.
3. `default_prompt`.

### Active set по runtime

- Claude: 19 units `SKILL.md`; Codex-route unit 5 не действует.
- Codex: 19 units `SKILL.md`; Claude-route unit 4 не действует.
- `agents/openai.yaml` — интерфейсная конфигурация Codex, а не самостоятельный
  role-файл. При явном запуске через его `default_prompt` к Codex instructional
  set добавляется одна дублирующая trigger-unit, поэтому верхняя граница равна
  20; `display_name` и `short_description` не становятся body-обязанностями.

Одновременно применимый набор не превышает 20.

## Findings

1. `candidate/SKILL.md:19-20` — bare `Анализ` расширяет принятую anti-ritual
   границу на любой анализ. Нарушены `check-instructions.md`: «Считай находкой
   добавку сверх слов пользователя без принятого основания» и «Считай находкой
   строку, из которой нельзя однозначно определить … scope». Owner-коррекция
   требует «не превращать tentative wording в обязательный ритуал во вред
   скилу», а принятая history-формула и `authoring-map.md` говорят именно о
   **дополнительном** анализе. Ближайший правдоподобный неверный разбор: при
   отсутствии material future cost агент объявит ритуалом необходимый анализ
   существующего кода, причин бага или проверки корректности. Минимальная
   локальная правка: начать это предложение с новой строки и заменить `Анализ`
   на `Дополнительный стратегический анализ`.

2. `candidate/SKILL.md:4-6` — две независимо применимые launch-unit начинаются
   на одной физической строке: `system. If choosing …`. Нарушено постоянное
   правило `1skill-creation/SKILL.md`: «Каждую самостоятельную инструкцию пиши
   с новой строки». Первая unit включает общий coding trigger и функцию, вторая
   независимо задаёт contract neighbor; одну можно выполнить или нарушить без
   другой. Минимальная локальная правка без изменения folded YAML value:
   закончить строку на `system.` и начать `If choosing a contract …` с новой
   continuation-строки. Та же формальная проблема у двух предложений на
   `candidate/SKILL.md:19`; минимальная правка finding 1 одновременно её
   устраняет.

## Ближайшие неверные разборы, не ставшие findings

- `also use` в contract boundary не заменяет `1readable-code` соседом, а
  добавляет runtime-specific owner до contract decision; оба названных skill
  существуют.
- `Внешний взгляд вне … неопределённости или прямого запроса` можно было бы
  вырвать как объявление owner-request ритуалом, но генитивная конструкция под
  `вне` и явный positive gate протокола однозначно оставляют прямой запрос
  разрешающим условием.
- Step 2 не требует слепо принять возражение: фактическое опровержение является
  явной второй веткой завершения.
- Same-cost acceptance не создаёт отчётный ритуал: `отдельный отчёт не нужен`
  прямо закрывает этот разбор.

Кроме finding 1, добавок сверх owner-слов без записанного основания не найдено:
named practices, conditional one-fresh-subagent mechanism, runtime contract
boundary и same-cost falsifier адресованы owner evidence и preservation map.

## Прочие буквальные проверки

- `description` — английский, trigger + реальная neighbor boundary, 167
  символов; `short_description` — английский trigger, 35 символов.
- Instructional body и `default_prompt` — русские; English оставлен только в
  method/runtime handles.
- Уникальный контекст — 538 символов, примерно в пределах 500; цели — ровно
  три законченных предложения.
- Reference-файлов и внутренних Markdown-ссылок в candidate нет.
- Runtime neighbors существуют:
  `/Users/triton/.claude/skills/codebase-design/SKILL.md` и
  `/Users/triton/.codex/skills/1codebase-design/SKILL.md`.
- Frontmatter и `agents/openai.yaml` разбираются как YAML; `quick_validate.py`
  вернул `Skill is valid!`.
- Changed version существует только в `recheck-2026-08-30/candidate/`.
  Official shared owner, tracked Claude/Codex и обе live projections не
  изменены и всё ещё имеют прежний SHA
  `1bcb9e27fd2e355a2b74501063fec476c105bd2423cbefae5ad66438eda5a42a`.

## Непроверенное

- Runtime use / skip / contract near-miss на exact SHA
  `361faf00c670aa1e2e631c1d09b408c4aa5b3669d1f924f40cd2080c081989e4` в
  Claude и Codex.
- Реалистичный clean-run exact SHA с отрицательной веткой без субагента и
  положительной веткой с одним fresh subagent, изменившим решение до правки и
  замкнутым same-cost acceptance после правки.

Это только внешние acceptance-прогоны; их отсутствие не использовано как
finding exact текста.
