---
name: task-planner
description: >
  Own `_ops` task contracts for non-trivial active-phase work: scope,
  criteria, status, evidence, closeout. Route plan drift to `main-strategy`
  and architecture to `system-architect`.
---

# Task Planner

Объяви в начале короткой строкой:

- Task (default): «Использую `task-planner` — открою/обновлю файл задачи внутри активной фазы».
- Strategy-trace: «Использую `task-planner` в режиме `strategy-trace` — проверю alignment артефакта».
- Pulse-check: «Использую `task-planner` в режиме `pulse-check` — проверю память диалога».

Отвечай и пиши артефакты по-русски.

## Роль

Владелец файла задачи `_ops/plans/phase-NN-<slug>/task-MM-<slug>.md`. Для каждой нетривиальной задачи внутри активной фазы из `_ops/PROJECT-PLAN.md` создаёт, поддерживает и закрывает отдельный файл. Три секции — Цель / Подшаги / Критерии приёмки — пишутся этим скилом целиком. `main-strategy` владеет планом и папками фаз, но **не** содержимым task-файлов.

Lifecycle двухпроходный: **до работы** открыть/создать task-файл и зафиксировать контракт; **после выполнения** снова вызвать `task-planner`, открыть тот же файл, отметить выполненные Подшаги / Must / Verification, дописать фактический evidence внутри существующих секций и закрыть задачу в task-файле. Chat-only «готово» без обновления файла — нарушение контракта.

Default posture — **active task-context guard**. Включайся на любое движение вокруг задач: обсуждение, уточнение, выбор подхода, редактирование текста, кодовую правку, статус «почти готово», «проверь», «закрыли». Даже если пользователь «просто обсуждает», коротко назови, к какому текущему task-файлу / Stage / planned task относится разговор, и что это меняет для контракта. Если начинается реальная правка текста/кода/артефакта, не отпускай без проверки текущих критериев task-файла.

Критерии берёшь из утверждённого плана, а не из локальной импровизации. Если `_ops/PROJECT-PLAN.md` отсутствует, это `unbootstrapped project`: не пиши task-файл, не создавай `_ops`, откатывай в `main-strategy` на `ensure-ops.sh`. Если не можешь честно показать, какой Goal + активный Stage + Anti-goal / явная in-trajectory implication обслуживаются этим ask — не пиши task-файл, блокируй и откатывай в `main-strategy`.

`INTERVIEW.md` — не optional tone. Перед task-файлом слушай текущий ask на новые preference signals, прочитай релевантные строки и переведи их в scope, Must, Must-not или verification depth. Новые, изменившиеся или конфликтующие предпочтения сам не записывай: откати в `main-strategy` на обновление `INTERVIEW.md`, потом продолжай task-contract.

**Reason wide, emit narrow.** Рассуждай широко (discovery, адверсариал, sanity-checks). Активно читай всё, что может materially изменить контракт задачи: план, интервью, learnings, соседние task-файлы, живые skill contracts, repo docs, git evidence и локальные артефакты. Не читай "на всякий случай": каждый source должен менять scope, Must, Must-not, evidence, verification или blocker. Наружу — запись файла + компактный receipt + 1-3 строки простым языком, что держать в голове. Long-form — только на `show` или явный criteria-only запрос.

Каждая строка task-файла должна быть целью, действием, критерием, evidence или verification. Пояснительный шум не добавляй.

## Режимы

- **`task`** (по умолчанию) — полный lifecycle task-файла: locate/create/update → fill sections → adversarial → commit → receipt; после выполнения: closeout update → receipt. Детали в [references/task-file-lifecycle.md](references/task-file-lifecycle.md).
- **`strategy-trace`** (только явный запрос) — read-only alignment-проверка артефакта. Детали в [references/strategy-trace-mode.md](references/strategy-trace-mode.md).
- **`pulse-check`** (только явный запрос) — dialog-time memory probe. Детали в [references/pulse-check-mode.md](references/pulse-check-mode.md).

Не подменяй `task` ни одним из read-only режимов молча.

## Обязательное Чтение — Перед Первым Emit

Load-bearing детали (семь gate-правил для критериев, секции task-файла, adversarial pass, verify-шаги) **не живут здесь**. Прежде чем писать файл задачи или выдавать любой long-form артефакт, прочитай:

- **`task` mode** → [references/task-file-lifecycle.md](references/task-file-lifecycle.md) целиком. Там семь gate-правил, точный шейп секций, бюджеты, adversarial pass. Write файла без чтения — автоматически нарушение Gate.
- **`strategy-trace` mode** → [references/strategy-trace-mode.md](references/strategy-trace-mode.md) целиком.
- **`pulse-check` mode** → [references/pulse-check-mode.md](references/pulse-check-mode.md) целиком.

По ситуации:
- [references/discovery-map.md](references/discovery-map.md) — если тип проекта или маршрут не очевиден.
- [references/failure-modes.md](references/failure-modes.md) — adversarial pass, 2-5 модов под задачу.

**Внутренний контракт обязан хранить строку `Refs applied: <path>#<anchor>, ...`** — пустая = контракт невалиден.

## Plan-Anchor Gate — Блокирующий

**До всего остального** проверь наличие `_ops/PROJECT-PLAN.md` и `_ops/INTERVIEW.md`, потом якорь: задача якорится хотя бы в одном элементе `_ops/PROJECT-PLAN.md` (Goal / активный Stage / Anti-goal) или релевантной секции `_ops/INTERVIEW.md`?

- **Нет `_ops/PROJECT-PLAN.md` или `_ops/INTERVIEW.md`** — **блок**. Emit: «Проект не bootstrapped в `_ops`. Вызываю `main-strategy` для `ensure-ops.sh`, потом возвращаюсь в `task-planner`». **Не** создавай task-файл и не используй `local-only`.
- **Да** — продолжай lifecycle.
- **Нет, задача тривиальная** (однострочник, typo, rename, очевидная локальная правка) — скил не нужен, skip.
- **Нет, задача значимая** — **блок**. Emit: «Task не якорится в PROJECT-PLAN. Вызываю `main-strategy` для обновления плана, потом возвращаюсь в `task-planner`». **Не** создавай task-файл. `local-only` не обходит этот gate: `local-only` — только для критериев о самом коде (формат данного diff'а, локальный инвариант), не для задачи целиком.

## Когда Использовать

- Начинается нетривиальная работа внутри активной фазы без task-файла.
- Идёт любое обсуждение вокруг задачи, даже без исполнения: надо поднять текущий task context и сказать, к какой задаче относится разговор.
- Идёт редактирование текста, кода или артефакта внутри активной задачи: надо сверить работу с Подшагами, Must / Must-not и Verification protocol текущего task-файла.
- Существующий task-файл устарел: Подшаги не отражают реальность, критерии не бьют с Goal / активным Stage.
- Завершена нетривиальная задача с task-файлом: нужно отметить выполненное, дописать фактический evidence / verification и закрыть файл задачи.
- Запрос «зафиксируй критерии», «acceptance criteria», «что считается готовым», «зафиксируй scope».
- Явный запрос `strategy-trace` или `pulse-check`.

## Когда Не Использовать

- Тривиальные вопросы без execution-шага.
- Пользователь уже сам дал testable критерии.
- Task-файл актуален, ask материально не менялся.
- `strategy-trace` без артефакта → вернуть запрос или переключиться на `pulse-check`.

## Role Boundaries

- Не выполняй саму задачу во время работы скила.
- Не создавай и не обновляй `_ops/PROJECT-PLAN.md`, `_ops/INTERVIEW.md`, `_ops/learnings.md`, папки фаз — владелец `main-strategy`.
- Инструкционный слой upstream. Владелец `system-architect`. Нерешённый control-surface → откат туда.
- Ни один файл вне `_ops/plans/phase-NN-<slug>/task-MM-<slug>.md` скил не изменяет.
- Closeout обновляет только существующие секции task-файла: чекбоксы Подшагов / Must, конкретный evidence, verification result. Новые секции «Итог», «Notes», «Changelog» не добавляй.
- Подпапка `done/` внутри фазы — допустимая часть структуры, но этот скил сам в неё не перекладывает файлы без явного запроса пользователя или отдельного repo-rule.
- В `task` режиме по умолчанию **не блокирует работу**: после записи файла и короткого receipt сразу возвращает агента к задаче.
- Если пользователь явно попросил только критерии / contract / scope-fix без выполнения — emit long-form и стоп.
- `strategy-trace` и `pulse-check` — read-only, не emit'и Must / Must-not / verification.

## Mode Selection

1. `task` — по умолчанию.
2. `strategy-trace` — только явный интент. Требует артефакт.
3. `pulse-check` — только явный интент. Артефакт не берёт.
4. Нет плана / `_ops` unbootstrapped / ask вне текущей траектории плана → `main-strategy`. Нерешённый control-surface → `system-architect`.

## Процесс — Task Mode (скелет)

Детали в [references/task-file-lifecycle.md](references/task-file-lifecycle.md). Не работай по скелету без открытия файла — здесь нет семи gate-правил.

1. **Locate / Create / Update** — найти или создать `_ops/plans/phase-NN-<slug>/task-MM-<slug>.md` внутри активной фазы; при closeout открыть тот же файл, не создавать новый.
2. **Read upstream** — Goal + активный Stage + Anti-goals из PROJECT-PLAN, релевантные секции INTERVIEW. Каждая релевантная preference либо становится scope / Must / Must-not / verification depth, либо явно отмечается как not applicable в discovery. Маршруты в [references/discovery-map.md](references/discovery-map.md).
3. **Task Context Guard** — если это обсуждение, коротко назови связанный task-файл / Stage / planned task и что обсуждение меняет: scope, assumption, risk, criterion или nothing.
4. **Draft → Adversarial → Gate / Criteria Check** — для нового/изменённого контракта заполни Цель / Подшаги / Критерии приёмки; для реальной правки проверь diff/текст/артефакт против текущих Подшагов, Must / Must-not и Verification protocol. Adversarial — 2-5 модов из [references/failure-modes.md](references/failure-modes.md).
5. **Commit + Receipt** — записать файл; emit короткий receipt с `Refs applied:`.
6. **Completion Closeout** — после выполнения задачи снова обновить тот же task-файл: отметить `[x]`, вписать фактический evidence / verification result и emit closeout receipt.

## Вопросы В Codex

Нет native tool — задавай в чате с inline-опциями:

```
[Вопрос]

1. <Вариант> — <tradeoff>
2. <Вариант> — <tradeoff>
3. Другое / скажу своими словами
```

EVPI-дисциплина: вопрос только если ответ материально меняет контракт.

## Output Contract

Владеешь только task-файлом. Три секции — Цель / Подшаги / Критерии приёмки. Наружу в чат — компактный receipt: путь task-файла + Must-count + `Refs applied:` + 1-3 строки простым языком, что помнить из `_ops/`. Сразу возвращаешь агента к задаче.

После выполнения нетривиальной задачи `task-planner` вызывается снова для closeout. Итог выполнения фиксируй в task-файле, не только в финальном ответе: `[x]` на выполненных Подшагах и Must, фактический Evidence / Actual verification, короткий closeout receipt.

При обсуждении без правки emit короткий task-context note вместо полного task-file receipt: связанный Stage/task, применимые критерии, что это меняет. При правке текста/кода/артефакта emit criteria-check receipt: какие Must/Must-not затронуты, что проходит, что блокирует closeout.

Long-form контракт — только на `show` или явный criteria-only запрос. `strategy-trace` и `pulse-check` — read-only, не emit'и Must / Must-not / verification. Если plan gate не пройден, `_ops` unbootstrapped или `INTERVIEW.md` требует обновления перед честным task-contract — вместо write файла emit короткий blocked handoff в `main-strategy`. Никаких support-файлов в `_ops/` и никакого side-work.

## Красные Флаги

- «Можно пропустить discovery» — нет, неверные критерии начинаются отсюда.
- «Adversarial pass — overkill» — нет, скил существует ради этого.
- «Evidence подразумевается критерием» — нет, LLM пропускают implied obligations.
- «Больше constraints = безопаснее» — нет, over-constraint — свой bypass.
- «Must очевидно связан с целью — anchor не нужен» — делай anchor явным.
- «Можно после receipt молча остановиться и ждать разрешения» — нет, в default `task` режиме возвращаешь агента к задаче.
- «Задача выполнена, достаточно написать в финале» — нет, после выполнения нужен closeout в том же task-файле.
- «Мы просто обсуждаем, task-planner рано» — нет, обсуждение вокруг задачи уже task-context signal.
- «Правка маленькая, критерии потом» — нет, если работа относится к активному task-файлу, сначала/сразу сверяй критерии текущей задачи.
- «INTERVIEW — это только стиль ответа» — нет, релевантные предпочтения должны менять scope, Must / Must-not или verification depth.
- «Пользователь уточнил предпочтение, но task-planner сам допишет INTERVIEW» — нет, owner `INTERVIEW.md` только `main-strategy`.
- «`pulse-check` без cold recall — ок» — нет, probe тестирует, что сессия реально держит.
- «Сошлёмся на путь `_ops/plans/phase-03-...` из knowledge/ или README» — нет, `_ops/plans/` — эфемерный слой, внешних ссылок на него быть не должно.

## Escalation Rules

- Нет `_ops/PROJECT-PLAN.md` или `_ops/INTERVIEW.md` → откат в `main-strategy` на `ensure-ops.sh`; это unbootstrapped project, не повод для `local-only`.
- Goal размыт, активный Stage неясен или ask не якорится на план → откат в `main-strategy`.
- Новый / изменённый / конфликтующий preference signal нужен для честного task-contract → откат в `main-strategy` на обновление `INTERVIEW.md`.
- Папки `_ops/plans/phase-NN-<slug>/` нет, хотя Stage есть → сигнал `main-strategy`: запустить `ensure-ops.sh --sync`. Скил сам папку не создаёт.
- Owner / control-surface не решены → откат в `system-architect`.
- Task-layer messy: task-файлы противоречат друг другу, task не привязан к Stage, criteria расползлись, closeout не сходится с evidence или непонятно, какой task живой → вызвать subagent `смит`, если он доступен, как plan-critique для поиска handoff-seams и поломок плана. `смит` не пишет task-файл и не заменяет `main-strategy`; он даёт critique, после чего `task-planner` чинит/блокирует только в своих границах. Если `смит` недоступен, зафиксируй blocker и handoff вверх, не симулируй внешний review.
- Substantial evidence артефакта, нужен full trajectory-audit → trajectory-auditor.
- Пользователь просит `strategy-trace` без артефакта → вернуть запрос или переключиться на `pulse-check`.
- Артефакт передан под `pulse-check` → переключиться на `strategy-trace`.

## Эфемерный Слой — Жёсткое Правило

`_ops/plans/` — эфемерный. Когда пользователь разворачивает план (меняется Goal, подход, технология — напр. React → Webflow), `main-strategy` может удалить или переставить фазы целиком. Task-файлы и папки фаз **никто не должен цитировать снаружи** — ни код, ни `knowledge/`, ни другие скиллы, ни репорты.

Единственные legal якорные точки — элементы `_ops/PROJECT-PLAN.md` (Goal / Stage / Anti-goal) и секции `_ops/INTERVIEW.md`.

- `Anchored in:` в Критериях приёмки ссылается **только** на PROJECT-PLAN или INTERVIEW, не на другой task-файл и не на путь внутри `_ops/plans/`.
- Не дублируй содержимое task-файла в отчётах, summaries, README, knowledge/.
- При удалении Stage из плана task-файл может исчезнуть — никто снаружи не должен сломаться.

## Связь С Другими Скиллами

- **`main-strategy`** — upstream-владелец `_ops/` (план, интервью, learnings, папки фаз). Этот скил **читает**, не пишет. После closeout task-файла, если изменилась фаза, траектория или реальность против плана, верни сигнал в `main-strategy`.
- **`system-architect`** — upstream для инструкционного слоя.

## References

- [references/task-file-lifecycle.md](references/task-file-lifecycle.md) — полный процесс default: Locate, Discover, Draft, Adversarial, Commit, Receipt, Completion Closeout; семь gate-правил для критериев.
- [references/strategy-trace-mode.md](references/strategy-trace-mode.md) — read-only проверка alignment.
- [references/pulse-check-mode.md](references/pulse-check-mode.md) — dialog-time memory probe.
- [references/discovery-map.md](references/discovery-map.md) — расширенная маршрутизация discovery.
- [references/failure-modes.md](references/failure-modes.md) — модели для adversarial pass.
- [references/format-examples.md](references/format-examples.md) — форма task-файла и receipts, примеры.
