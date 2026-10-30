# Карта полного авторинга

## Состояние

Полный zero-based draft собран в `reconstructed/`. Он ещё не является новой
candidate-версией: сначала старый пакет используется для проверки потерь и
сравнения пользы.

После первого независимого буквального checker-а исправленная полная версия
собрана в `candidate/`. Official owner не изменён.

## Baseline 1skill-creation

- Source-label из THREAD_CARD:
  `9bf11f64b436d313d979cba822b684f502e8e40e5f15a12f78cbd914ca29a518`.
- Локального алгоритма этой метки нет; она не совпадает с отдельным файлом или
  стандартным manifest SHA.
- Воспроизводимый SHA отсортированного merged Codex manifest:
  `2c07bb4cee4254a643cef1428b10e9a2ecaa327596e782db8d1ade76f525d4fe`.
- SHA `1skill-creation/SKILL.md`:
  `6e6b93e97eef2a31c8922ba8462a28a086c82ec80c6566c39ed63fc6bdc9f6a3`.
- Shared owner, tracked и installed проекции baseline совпадают.

## Применённые авторские режимы

### Кнопка запуска

Сохранён trigger `Use before writing or changing code`: он наблюдаем и
соответствует требованию automatic use при переходе к программированию.
Формула `when strategic view is needed` отклонена, потому что перекладывает
решение о вызове на реактивного агента. Runtime-соседи оставлены только как
near-miss boundary.

### Протокол поведения

Владелец не задавал буквальный четырёхшаговый workflow. Поэтому ни одна строка
не сохраняется как дословный owner-protocol; каждый механизм обязан отдельно
пройти `agent-defaults`.

### Reference-файлы

Самостоятельных стадий нет, active body не перегружен, references не созданы.
Добавление отдельного design-режима противоречило бы функции короткого
переключателя. Локальные разделы «Цель» неприменимы.

### Дефолты агентов

| Добавка | Дефолт → механизм → решение → вред без строки → цена строгости |
| --- | --- |
| Conditional fresh subagent | агент продолжит в собственной рамке, потому что знакомый подход выглядит достаточным → один независимый взгляд при unresolved material uncertainty → решение проверено извне → скрытая будущая связность сохранится → один дополнительный вызов только на открытой развилке |
| Strongest objection до правки | вызов можно формально выполнить и проигнорировать → возражение обязано изменить подход либо быть снято до edit → внешний взгляд входит в решение → subagent станет ритуалом → допустимый подход блокируется, пока сильнейшее обоснованное возражение не снято |
| Runtime contract route | общий engineering prior начнёт сам выбирать seam → точное имя соседнего скила и порядок до решения → contract остаётся у профильного owner-а → `1readable-code` присвоит чужую функцию → дополнительный handoff только при contract choice |
| Same-cost falsifier | обычные тесты могут не проверить заявленную будущую цену → после изменившего подход tradeoff проверяется та же цена → стратегическое решение опровергаемо → зелёный suite прикроет прежнюю structural cost → условная дополнительная проверка без отчёта |

## Первый checker-round

Принято и исправлено:

- дословные owner-цитаты добавлены в `intent.md`;
- Уникальный контекст сделан декларативным и сокращён примерно до 500
  символов;
- функция добавлена в первую trigger-фразу без выхода за trigger-only surface;
- contract route оставлен только во frontmatter, который входит в загруженный
  скил, а дубль из body удалён;
- вместо качественного «не перегружен» добавляется числовой inventory ниже.

## Exact active-set inventory candidate

`candidate/SKILL.md`:

1. use before writing code;
2. use before changing code;
3. strategic view of future system;
4. contract choice → `codebase-design` в Claude;
5. contract choice → `1codebase-design` в Codex;
6. task focus скрывает форму системы, будущую цену и CTO/architect view;
7. три named practices — handles уже имеющегося знания, не tutorial;
8. текущая цена оправдана только более дешёвыми следующими изменениями;
9. анализ без material future cost и strategic uncertainty объявлен
   ритуалом;
10. подход до программирования оценивается из будущего системы;
11. подход не ограничивается текущей задачей;
12. код остаётся цельным;
13. вероятная будущая правка остаётся локальной и читаемой;
14. material stability uncertainty не скрыта;
15. unresolved material uncertainty вызывает одного fresh subagent;
16. прямой owner-request вызывает одного fresh subagent;
17. subagent оспаривает подход с позиции будущей системы;
18. strongest justified objection снимается до правки;
19. изменившая подход будущая цена проверяется после правки;
20. отдельный отчёт не требуется.

Буквальный checker подтвердил 20 units в runtime-union и 19 одновременно
активных units в Claude или Codex: runtime выбирает только один из пунктов
4–5. `candidate/agents/openai.yaml` содержит три UI-настройки. При явном Codex
`default_prompt` верхняя граница instructional set равна 20 из-за дублирующего
trigger; `display_name` и `short_description` не становятся body-обязанностями.

## Terminal verification exact SHA

После двух повторов протокола точно проверена candidate-версия SHA-256
`361faf00c670aa1e2e631c1d09b408c4aa5b3669d1f924f40cd2080c081989e4`.

- Буквальный checker: две findings. `Анализ` слишком широк; две
  самостоятельные launch-units в `description` начинаются не с разных строк.
- Trajectory-checker: одна finding. Абсолютная «текущая цена»
  заменяет многокритериальное CTO-суждение одной future-change метрикой.
- Routing: 6/6 expected use, skip и near-miss decisions в Claude и Codex.
- Clean-run: pass с той же формулировочной оговоркой; ровно один fresh
  subagent изменил storage ownership до правки, `1codebase-design` был добавлен
  только на contract choice, и 9/9 behavior-тестов прошли.

`check-approve.md` требует остановиться после двух повторов. Поэтому SHA
`361faf…` не является approvable candidate: цикл правок остановлен, findings названы,
official owner и projections не изменены.

## Новый bounded pass после owner-границы простоты

Прежний stop-boundary закрыл тот цикл, но новое прямое решение владельца о непереусложнении
открыло один новый bounded pass. Чистый zero-based агент не видел пакет и вывел ту же
минимальную форму, записанную в `simple-zero-based.md`.

Exact candidate SHA-256:
`6aa4ec3785d3c57d2cec142c92e4541dc52e114225661f9c5ffee7382e9496c7`.

### Кнопка запуска

`description` содержит только automatic code trigger и функцию — strategic view будущей
системы. Contract route перенесён в body как runtime-boundary, потому что он не является
отдельным trigger этого скила. Длина собранного description — 78 символов.

### Протокол поведения

Постоянного workflow нет. Остались две развилки, которые не выводятся из общей цели:

1. точный runtime-owner выбора или изменения контракта до решения;
2. ровно один fresh subagent только после unresolved material uncertainty или по прямому
   owner-request.

Strongest-objection disposition и same-cost closure сняты как постоянные runtime-стадии.
Их поведение выводится из целей и обычной engineering verification; clean-run обязан это
опровергнуть или подтвердить.

### Reference-файлы

Самостоятельных стадий и перегруженного body нет; references и локальные reference-goals не созданы.

### Agent-defaults и counterfactual harm

| Hard line | Default без неё | Наблюдаемый вред |
| --- | --- | --- |
| Automatic trigger | Обычная правка не выглядит архитектурной | Task focus уже сузил взгляд, поэтому сам агент не поднимет strategic lens |
| Contract runtime-owner | Общая readability-lens сама выбирает seam | Два владельца порождают расходящиеся контракты |
| Conditional one fresh subagent | Self-confirming подход кажется достаточным; общая «зови reviewer» не задаёт порог | Без вызова скрытая связность остаётся; обязательный вызов на ясной работе даёт задержку и размывает ответственность |

### Active set exact candidate

`candidate/SKILL.md` содержит 19 units в runtime-union и 18 одновременно активных units
в Claude или Codex, потому что один runtime-specific contract handle неактивен. Финальный
буквальный checker обязан подтвердить или исправить этот счёт. `candidate/agents/openai.yaml`
содержит три UI-units и не добавляет runtime-стадии; явный `default_prompt` дублирует trigger.

## Terminal verification минимального candidate

- Буквальный checker: `pass`, находок нет; подтверждены 19 union-units, 18 в одном
  runtime и конкретный counterfactual harm каждой hard line.
- Trajectory-checker: `trajectory_ok`, находок нет; возвращать снятые
  strongest-objection и same-cost stages не нужно.
- Frontmatter routing: 6/6 для use, skip и contract near-miss в Claude и Codex.
- Clean-run: `pass`, 6 behavior-тестов, compile/signature/hard-delete checks прошли.
  `1codebase-design` был вызван на contract choice; fresh subagent не вызван, потому что
  после comparator, domain judgment и prior art материальная неопределённость не осталась.
  Без снятых стадий агент сам сравнил альтернативы, вывел claim-specific falsifier и
  проверил negative paths.

Exact candidate полностью проверен, но остаётся history-only до безусловного approval именно SHA
`6aa4ec3785d3c57d2cec142c92e4541dc52e114225661f9c5ffee7382e9496c7`.

## Отклонённые clean-room добавки

- обязательный молчаливый проход — выводится из trigger и целей;
- перечень `information hiding`, `cohesion`, ownership, blast radius и
  reversibility — учебник поверх уже названных практик;
- тест ближайшего изменения — поглощён целью о вероятной будущей правке;
- отдельный fast path — поглощён Уникальным контекстом и третьей целью;
- общее условие выхода — дублирует три цели и same-cost falsifier.
