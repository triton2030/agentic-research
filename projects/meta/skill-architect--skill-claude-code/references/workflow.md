# Workflow — Восемь Шагов

Порядок rigid. Не переставляй. **As-is map и Forces идут до failure scan**, иначе архитектор сканит вслепую.

## 1. Telos — Upstream Check

Читаю:
- `_ops/PROJECT-PLAN.md` — Goal + Approach & Why + активный Stage + Anti-goals.
- `_ops/INTERVIEW.md` — только секции, ограничивающие архитектурный выбор.
- `_ops/learnings.md` — реальные дельты план-vs-реальность.
- корневые и локальные `AGENTS.md` / `CLAUDE.md` / `GEMINI.md` в затронутой зоне.

**Content gate:**
- `Goal` — одна строка результата, не процесса.
- `Approach & Why` — непустой.
- Есть хотя бы один активный `Stage` со Steps.
- `INTERVIEW.md` — хотя бы одна релевантная секция (или явно: «для этого домена предпочтений нет»).
- `learnings.md` — может быть пустым в начале; но если есть, дельты конкретные (named scenario + дата), не generic.

Generic Goal или пустой Stage → **блокирую audit**. Верну: чего не хватает, почему без этого audit слабый, откат в `project-strategy`. Не компенсирую слабую карту generic архитектурой.

**Freshness check.** `_ops/` триада должна быть **горячей**, а не snapshot'ом:
- Когда каждый из трёх файлов последний раз обновлялся? (`git log -1 --format=%ad -- _ops/<file>`).
- Есть ли в текущем диалоге или недавних сессиях сигналы, требующие обновления, но обновления не случилось? Сигналы: **preference revealed** (пользователь сказал «предпочитаю X», «не люблю Y», «давай в таком стиле») → INTERVIEW; **plan delta** (Stage завершён, новый Stage начался, Goal смещён, Anti-goal появился) → PROJECT-PLAN; **expected-vs-actual дельта** (что-то пошло не так, не как ожидали) → learnings.
- Stale триада с явными непогашенными сигналами — это **default failure class** для Шага 4 («upstream truth layer не горячий»). Не молчаливо проходить.

Если триада горячая и сигналы отработаны — отметь это в output Шага 1 явно: «триада горячая, сигналы отработаны». Если холодная — failure class обязателен.

## 2. As-is Map — Capability Inventory

**First-order артефакт.** Не линза, не проверка мимоходом. Без него Шаг 6 невозможен.

### Что инвентаризирую

- **Hooks** — `.claude/settings.json` (project scope) + `~/.claude/settings.json` (user scope). Event × matcher × действие. Включая: PreToolUse, PostToolUse, UserPromptSubmit, Stop, SessionStart.
- **Permissions** — allow / deny / ask правила, scope каждого.
- **Skills** — marketplace (установленные плагины), user-global (`~/.claude/skills/` и `~/.claude/marketplaces/*/skills/`), project-local (`projects/*/SKILL.md` и `.claude/skills/`). Триггеры и границы, не только имена.
- **MCP servers** — зарегистрированные, в каком scope, реально доступные `mcp__*` tool prefixes.
- **Subagents** — определённые, с `allowed-tools`.
- **Instruction слои** — корневой `AGENTS.md` / `CLAUDE.md` + локальные, precedence правил при конфликте.
- **`_ops/` состояние** — реально ли заполнен или стоит шаблонами.
- **Папки проекта** — `projects/`, `knowledge/`, `docs/` и т.п.: что производят, что потребляют.

### Правила строгости

- **Точные handles, не классы.** Не «hooks есть», а «PreToolUse на Write, matcher `_ops/**`, blocks with exit 2».
- **Реальная установка, не текстовое упоминание.** README может врать. `settings.json` и `installed_plugins.json` — нет. Сомневаюсь — subagent probe с минимальным prompt'ом, проверяю поведение.
- **Mismatch между instruction text и реальностью** (*«AGENTS.md ссылается на skill X, skill не установлен»*) — это failure (уходит в Шаг 4), не silent pass.

### Output шага

Список существующих capabilities с пометкой, какие из них **уже должны покрывать** будущие failure classes (Шаг 4). Это вход в reuse-first gate (Шаг 6). Без такого списка prescriptions невалидны.

## 3. Forces — Design Constraint На Вход

**Не epilogue.** Forces — это констрейнты, ограничивающие проектирование **сейчас**, чтобы не сделать prescriptions, устаревающие под первой же силой.

Для каждой силы (2-3 штуки):
- **Что это** — смена основной модели, рост репо, новый класс задач, pivot, рост контекстного окна, смена tool surface.
- **Early signal** — по чему увижу, что она приехала (*«модель начинает игнорировать короткий AGENTS.md в 2+ сессиях подряд»*).
- **Constraint** — что я из-за этого **не** буду проектировать (*«не фиксирую имя текущей модели в hook matcher'е — через квартал смена, hook сломается»*).

### Строгость

- Нет early signal → сила не в scope.
- Generic («AI будет развиваться», «проект вырастет») → отбрасываю.
- Каждая сила обязана порождать хотя бы одно решение *«не буду проектировать X»*. Если не порождает — сила косметическая.

В Шаге 8 проверяется: sunset signals prescriptions должны совпадать с early signals этих сил.

## 4. Failure Classes

Теперь, зная Telos (Шаг 1), As-is map (Шаг 2), Forces (Шаг 3), читаю failure modes правильно.

Источник — две линии:
1. **`_ops/learnings.md`** — реальные дельты. Лучший источник: факт, а не гипотеза.
2. **Внутренний inversion/premortem** по активному Stage. Внутреннее мышление, **не видимая секция в файлах**.

Для каждого failure:
- **Что конкретно пойдёт не так** — plan-specific, не generic.
- **Где система сейчас это позволяет** — конкретное слабое место в instruction layer / hooks / правах.
- **Что из Шага 2 уже должно было это покрывать** — и почему не покрывает: не установлено / не активировано / matcher узкий / prompt-only игнорируется / skill есть, но триггер слабый.

Plan-specific пример: *«Активный Stage требует шипить MVP, модель склонна рефакторить. PreToolUse на Refactor-класс edits отсутствует. Prompt в AGENTS.md есть, но игнорируется под давлением token economy»*.

Группирую failures в **классы** — общий корень, не разрозненный список. Это подготовка к Шагу 5.

### Default failure class — Cold Upstream Triad

Всегда проверяю: есть ли в системе механизм, который **триггерит обновление `_ops/` триады при сигналах**?

- Сигнал «preference revealed» приходит — что заставляет записать в INTERVIEW? UserPromptSubmit hook? Правило в AGENTS.md? Или ничего, и запись происходит только если пользователь сам попросит?
- Сигнал «plan delta» приходит — что заставляет обновить PROJECT-PLAN? Stop hook при завершении Stage? Или никто?
- Сигнал «expected-vs-actual дельта» приходит — что заставляет записать в learnings? Или дельты исчезают в истории чата?

Если ответ «ничего / только дисциплина» — это **structural failure**, а не косметический. Попадает в Шаг 5 (leverage) как кандидат на systemic fix. Обычный fix — связка из трёх hooks (UserPromptSubmit / PostToolUse / Stop) или один compose skill для hot-keeping.

Это default failure class — не исчезает, даже если в learnings.md он явно не записан, потому что stale триада это системный tilt, а не разовая дельта.

## 5. Leverage Analysis

**Не «1 failure → 1 prescription».** Это инженерная гигиена, а не архитектура. Ищу одну интервенцию, которая убивает класс.

Для каждого класса:
- **Root** — общий корень, а не симптом.
- **Systemic fix** — одна интервенция, которая его вырезает.
- **Какие failures из Шага 4 она покрывает** — явно перечислить.
- **Leverage rank**:
  - `high` — закрывает 3+ сбоя одним механизмом.
  - `medium` — закрывает 2.
  - `low` — 1:1 patch.

Пример: 5 сбоев из разряда «модель не читает `_ops/` в начале сессии» → один SessionStart hook с context injection = класс закрыт. Не 5 prescriptions.

Prescriptions в Шаге 6 строятся из:
- systemic fixes (leverage `high`/`medium`) — первого приоритета;
- остатка (не покрытого systemic) — как 1:1 prescriptions.

**Высокий leverage предпочтительнее низкого даже когда он сложнее в имплементации** — уменьшает общий surface правил, снижает долг.

## 6. Prescriptions

Для каждой prescription обязательно всё ниже.

### Reuse-first gate (обязательно перед всем остальным)

Явная строка:
- **Что уже покрывает частично** — конкретный handle из Шага 2.
- **Почему недостаточно** — одна строка конкретного gap.
- **Default** — расширить существующее, не добавить новое.

Если существующий механизм покрывает полностью — **не добавляй prescription, перемаршрутизируй**: *«failure закрывается hook X, пользователь/ИИ не знает об этом; единственное изменение — добавить явный вызов в default route fresh session (Шаг 8)»*.

### Root-instruction task-contract routing

Если root `AGENTS.md` / `CLAUDE.md` в scope, проверь, есть ли прямое routing-правило часто вызывать `task-contract`. Оно должно покрывать обсуждение задачи, уточнение подхода, status/movement, редактирование текста/кода/артефакта, сверку текущей работы с Подшагами / Must / Must-not / Verification protocol task-файла и closeout после выполнения.

Если такого правила нет, prescription обычно живёт в `instruction text` layer. Не дублируй тело `task-contract`: root docs должны сказать **когда вызывать**, а не переписать lifecycle.

### Fix-layer в preference order

1. **Runtime guardrail** (hook / permission / validator) — для необратимых и опасных сбоев.
2. **Local skill** — для повторяемого workflow.
3. **Instruction text** (AGENTS.md / системный prompt) — для устойчивой рамки.
4. **`task-contract` handoff** — для task-level контракта.
5. **Human checkpoint** — где нужна эскалация.

Prompt-level допустима **только после явного отказа** от runtime и skill с причиной.

### Backlink

`→ protects PROJECT-PLAN §Stage <name>` / `→ protects §Goal` / `→ addresses learnings entry YYYY-MM-DD` / `→ honors INTERVIEW §<section>`. Без backlink'а невалидна.

### Observable signal

Один конкретный сигнал, по которому через N сессий видно, сработало ли. Пример: *«через 3 сессии файлы из `node_modules` перестают появляться в Edit calls»*.

### Sunset signal

Один конкретный сигнал устаревания. **Обязан соотноситься с early signal одной из Сил из Шага 3.** Если не соотносится — либо Сила косметическая (удали из Шага 3), либо prescription слепая к форсам.

Пример: *«sunset сработает, когда token economy удвоится и короткий AGENTS.md начнёт игнорироваться в 2+ сессиях подряд»* — соотносится с силой «рост контекстного окна».

### Конкретный механизм (если runtime)

Тип hook'а, matcher, event. Детали — [claude-code-guardrails.md](claude-code-guardrails.md).

### Owner

Какой файл / механизм владеет этим правилом как source of truth. Одно правило — один owner. Дублирование в двух местах → drift.

Используй `AskUserQuestion` (header `Fix layer`) если несколько fix-layer кандидатов с неочевидным tradeoff.

## 7. Minimize Pass

**Перед emit — обязательный прогон.** Архитектор убирает столько же, сколько добавляет.

Вопросы:
- Какое существующее правило новая prescription делает избыточным?
- Какие две prescriptions можно смерджить?
- Какое правило больше не служит своему backlink'у (PROJECT-PLAN сдвинулся, правило осталось)?
- Какая папка / файл без якоря в PROJECT-PLAN или INTERVIEW?

**Chesterton's fence probe.** Прежде чем удалить — что сломаю? Если не могу объяснить, зачем это было здесь, — рано трогать. Archaeology иногда держит load-bearing state.

### Output шага обязателен, даже если «ничего не удалено»

Три варианта эмита:
- `Удалено: <список>` с обоснованием каждого удаления.
- `Смерджено: <список>` с ссылками на исходные правила.
- `Оставлено: <что и почему не удалено, несмотря на подозрение>`.

Молчание = сбой Gate. Минимизация без эмита = её не было.

## 8. Handoff + Verification

### Default Route For Fresh Session

Один файл, который новая сессия читает первым. Какой skill вызывается на типичные триггеры. Какие hooks сработают автоматически.

Буквальная формулировка load-bearing правила, чтобы новая сессия считывала его без интерпретации.

### `task-contract` Handoff (если нужен)

Если диагноз — shortcut, formal pass или weak done-state — явно рекомендую handoff. Называю:
- durable instruction surfaces, которые `task-contract` читает как upstream;
- task-level constraints, которые он наследует из них.
- literal root-instruction wording, если fresh-session default route должен чаще вызывать `task-contract`.

Если архитектор отработал хорошо, `task-contract` делает **меньше** работы — правила уже живут в fabric.

### Forces Verification

**Перечитываю Шаг 3.** Для каждой силы:
- Какие prescriptions станут уязвимы, когда она приедет?
- Совпадает ли их sunset signal с early signal этой силы?
- Не совпадает → либо сила косметическая (удаляю из Шага 3), либо prescription слабая (перепроектирую).

Это не повтор Шага 3. Это **проверка, что Шаг 3 был честный**, а не формальный.

Если Verification показывает, что ни одна prescription не уязвима ни к одной силе — подозрительно: либо силы действительно нерелевантны (признаю, оставляю), либо design слишком жёсткий и не адаптируется (перепроверяю).

## Инструмент Проверки — Subagent С Чистым Контекстом

Для load-bearing prescriptions (hook matcher, новое правило в AGENTS.md, новый skill trigger, смена ownership) не полагайся на гипотезу — проверь эмпирически. Subagent приходит с чистым context window и своей role framing.

- **A/B probe** — два subagent'а на идентичной задаче: с prescription активным и без. Разница = real effect, не гипотеза.
- **Adversarial probe** — задача, где самый лёгкий путь = обойти правило. Non-bypassable prescription упрётся; легко обходимая — слабая, усиль или перенеси fix-layer.
- **Capability verification probe** — для Шага 2: subagent с минимальным prompt'ом видит ли реально установленный hook / skill / MCP в действии. Это честный тест на «реально установлено vs текстовое упоминание».

Для мелких правок — overkill, пропусти с явной пометкой.

## Инструмент Вопросов — `AskUserQuestion`

Native tool (deferred — `ToolSearch("select:AskUserQuestion")`).

**EVPI-дисциплина.** Перед каждым вопросом: «Ответ A → prescription X. Ответ B → всё равно X?». Если одинаково — не задавай. Каждый вопрос обязан менять архитектурный выбор.

### Применяю
- Развилка меняет fix-layer или ownership.
- 2-4 дискретных кандидата.
- Уверенность <70% или высокая стоимость ошибки.
- `Build or route` — новый механизм vs расширение существующего (reuse-first gate неоднозначен).

### Не применяю
- Open-ended → chat.
- Leading *«согласен с моим анализом?»* — сикофантия.
- Ответ меняет формулировку, не fix-layer.

### Типичные точки срабатывания
1. **Scope** — durable vs task-level.
2. **Fix layer** — runtime / skill / instruction / human checkpoint.
3. **Folder** — keep / archive / remove.
4. **Build or route** — создать новый механизм или расширить существующий.

Правила: symmetric options без `Recommended` при неопределённости; description опции называет tradeoff, не хвалит вариант.
