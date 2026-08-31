# Trajectory-check минимального candidate

## Вердикт

`trajectory_ok`. Самая простая достаточная runtime-форма удержана; реалистичного
ухода от commander's intent не найдено. Снятые `strongest-objection disposition`
и `same-cost closure` не нужно возвращать как постоянные стадии: компетентный
агент выводит использование decision-relevant возражения и его самый дешёвый
фальсификатор из цели, профессионального суждения и конкретного material risk.

## Receipt exact scope

- Exact candidate:
  `recheck-2026-08-30/candidate/SKILL.md`.
- Фактический и ожидаемый SHA-256 совпали:
  `6aa4ec3785d3c57d2cec142c92e4541dc52e114225661f9c5ffee7382e9496c7`.
- `candidate/agents/openai.yaml` прочитан полностью; SHA-256:
  `64f664e75d2254dace69065ffb86e887b36a0258f42f25cbebcaead75ea83f0d`.
- Контракт проверки `1skill-creation/agents/check-trajectory.md` прочитан
  полностью; SHA-256:
  `2171d05a2fb6fd7115d5b09cda92226077a01ad7ef0de20fb49887cf00f828b0`.
- Полностью прочитаны 23 файла, составлявшие `skills/1readable-code/` до этой
  записи, включая history, старые historical reviews, recheck maps, receipts,
  reconstructed и exact candidate. Выводы других текущих checker-ов не
  читались.
- Полностью прочитаны три заданных owner-holder-а:
  `_ops/chat-recall/2026-08-29-153512-codex-01a04d13.md`,
  `_ops/chat-recall/2026-08-29-163434-codex-01a04d4a.md` и
  `_ops/chat-recall/2026-08-30-130004-codex-01a051ac.md`.
- Дополнительно прочитаны `1skill-creation/SKILL.md`, `1chat-recall/SKILL.md`,
  его Retrieval-контракт и project-wide Product Frame + Product Principles.

## Независимо восстановленное намерение

**Проблема.** При переходе к коду умный агент реактивно сужает внимание до
локального патча и теряет форму будущей системы, цену следующих изменений и
CTO/architect perspective, хотя сами инженерные практики ему уже известны.

**Желаемое состояние.** Любое написание или изменение кода автоматически
включает короткую стратегическую линзу named practices. Подход одновременно
служит текущей задаче и будущей системе; ответственность и сложность оставляют
вероятную следующую правку локальной и читаемой, не вытесняя безопасность,
корректность, производительность, совместимость или явные требования.

**Не-цель.** Не создавать учебник, checklist, design-процесс, обязательный
отчёт, отдельную проверочную стадию или внешний review ясной работы.
`1readable-code` также не становится владельцем contract design.

**Материальная развилка.** Ровно один fresh subagent нужен только после
собственного суждения, если стратегическая неопределённость всё ещё способна
изменить будущую стабильность подхода, либо по прямому запросу владельца.

**Commander's intent.** При любом переходе к программированию автоматически
вернуть умному агенту стратегический CTO/architect взгляд уже известных
практик, чтобы до кода выбрать цельную и изменяемую форму, сохраняя полное
профессиональное суждение и привлекая один свежий взгляд только на настоящей
материальной развилке или по прямому запросу.

## Эталонная траектория одной строкой

`coding transition -> automatic strategic lens -> current task + future system judgment -> contract choice только у runtime-owner -> ясная работа сразу идёт в код; unresolved material uncertainty или owner-request получает один fresh challenge -> decision-relevant objection влияет на подход -> implementation -> обычная профессиональная проверка фальсифицирует material claim -> цельная форма и локальная читаемая следующая правка`

## Предсказанная траектория candidate

`дефолт task-local edit -> description меняет первое решение на pre-code future-system judgment -> named practices активируют ownership/locality без tutorial -> contract fork уходит в codebase-design -> unresolved fork получает один fresh challenge -> его конкретное возражение становится входом решения -> реализация и risk-shaped verification -> завершение без отдельного strategic report`

## Реалистичные случаи

### Positive material fork

Запрос: добавить cache повторных чтений профиля, сохранив публичный API; кроме
service, в тот же store пишет importer.

Task-local default помещает cache в service. Candidate меняет первое решение:
до правки агент рассматривает ownership и будущую coherence. Выбор владельца
cache достигает contract boundary, поэтому до решения используется runtime
`codebase-design`. Если факты всё ещё не разрешают store-vs-service fork,
вызывается ровно один fresh subagent. Его реалистичное возражение — service
cache станет stale после `Importer -> Store.save` — decision-relevant: оставить
исходный подход означало бы сохранить ту самую материальную неопределённость,
ради которой был вызван challenge, и не достичь целей candidate. Умный агент
переносит cache к store и инвалидирует его в `save`.

Проверка material structural claim также выводится без общей стадии: самое
дешёвое опровержение буквально задано возражением — прогреть cache, записать
новое значение через importer и потребовать новое значение при следующем
чтении. Вместе с проверкой повторных чтений это проверяет конкретную coherence,
а не создаёт универсальный same-cost отчёт. Игнорирование feedback или один
generic happy-path test было бы не альтернативным разумным прочтением
candidate, а незавершённым professional judgment относительно уже названного
material risk.

### Clear trivial path

Запрос: локально переименовать `value` в `total` без изменения поведения.
Skill автоматически загружается, но короткая named-practice линза не находит
contract choice, material future cost или unresolved uncertainty. Поэтому
`codebase-design` и subagent не вызываются, отдельный анализ или отчёт не
создаются; выполняются один локальный edit и обычная локальная проверка. Третья
цель явно оставляет этот escape path.

## Вклад каждого блока

| Блок | Вклад в цель |
| --- | --- |
| `description` | Сохраняет automatic code trigger и сразу называет функцию, не заставляя уже реактивного агента самому распознать архитектурный момент. |
| Уникальный контекст, абзац 1 | Называет исправляемый task-focus default и возвращает CTO/architect horizon. |
| Уникальный контекст, абзац 2 | Активирует `strategic programming`, `deep modules` и `conceptual integrity` как сжатые handles; явно закрывает tutorial/procedure drift. |
| Уникальный контекст, абзац 3 | Сохраняет многокритериальное professional judgment и не позволяет future-change lens вытеснить safety, correctness, performance, compatibility или requirements. |
| Цели 1–2 | Задают outcome: двойной горизонт решения, conceptual integrity и locality вероятной будущей правки. |
| Цель 3 | Одновременно удерживает material uncertainty и отрицательную ветку без ceremony. |
| Contract boundary | Не позволяет общему readability-skill присвоить runtime-owner contract design. |
| Fresh-subagent boundary | Даёт точный порог, количество и независимый взгляд только там, где собственное суждение не закрыло material fork либо владелец прямо запросил его. |
| `agents/openai.yaml` | Даёт UI-имя, короткое описание и нейтральный explicit prompt; новой когнитивной стадии не создаёт. |

## Оставшиеся ограничения, свобода и counterfactual harm

| Hard line | Исправляемый default | Вытесненная свобода | Конкретный вред без строки / escape path |
| --- | --- | --- | --- |
| Automatic use перед writing/changing code | Обычная code-edit не выглядит архитектурной и пропускает strategic lens. | Пропустить skill на тривиальной правке. | Task focus закрепляет тактическую форму первым diff; escape — skill загружается, но цель 3 не добавляет ceremony. |
| Full professional judgment не подменяется изменяемостью | Future-system framing может стать единственной метрикой. | Пожертвовать safety/correctness/performance/compatibility/requirements ради locality. | Обязательная сложность может быть ошибочно отвергнута; escape не нужен, потому что строка сохраняет, а не сужает профессиональный выбор. |
| Contract choice до решения у runtime-owner | Общий coding prior сам выбирает seam. | Решить contract без профильного skill-owner. | Два смысловых владельца дают расходящуюся границу; escape — вне выбора или изменения контракта route не действует. |
| Один fresh subagent после unresolved material uncertainty или owner-request | Self-confirming подход кажется достаточным; без порога reviewer легко становится ритуалом. | Вызвать ноль, несколько или несвежего reviewer-а на этой развилке. | Скрытая связность остаётся непроверенной либо ясная работа получает latency и размытое владение; escape — собственное суждение разрешило неопределённость и прямого запроса нет. |

## Проверка снятых стадий и paths of escape

- `Strongest-objection stage` не нужен как отдельная hard line. В positive
  fork challenge вызывается именно из-за decision-relevant unresolved
  uncertainty; компетентный агент использует конкретное возражение как вход
  решения. Candidate не требует слепого принятия: фактическое опровержение
  сохраняет свободу оставить подход.
- `Same-cost closure` не нужен как общий completion-stage. Когда material risk
  изменил подход, его конкретный falsifier выводится из professional
  verification; когда такого claim нет, дополнительной проверки формы нет.
- Нет contract choice — соседний skill не вызывается.
- Нет unresolved material uncertainty и owner-request — subagent не вызывается.
- Нет material structural claim — обычная проверка задачи завершает работу.
- Subagent не нашёл обоснованного возражения либо оно опровергнуто фактами —
  candidate не создаёт фиктивный blocker и не требует смены подхода.

## Осталось непроверенным

Статический trajectory-check не является поведенческим clean-run exact SHA и
не доказывает runtime discovery в Claude/Codex. Это внешний acceptance gap, но
не текстовая trajectory-находка: exact `description` прямо сохраняет automatic
trigger, а реалистичные positive и negative paths не имеют внутреннего выхода
от commander's intent.

## Находки

Находок нет.
