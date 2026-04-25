# System Building Principles

Открывай этот файл, когда вопрос касается не только текста инструкций, а самой формы ИИ-системы: runtime layer, tools, memory, approvals, guardrails, eval, multi-agent split.

Это короткая выжимка из:

- `knowledge/wisdom-agents.md`
- `knowledge/wisdom-LLM.md`
- `knowledge/research/meta/learnings.md`

Для Claude Code-specific механизмов (hooks, permissions, subagents, MCP) — см. соседний файл `claude-code-guardrails.md`.

## Goal-Driven System Design

Это рамка, в которой работают все принципы ниже:

- **Path of least resistance.** ИИ идёт по пути наименьшего сопротивления. Архитектор делает этот путь совпадающим с путём к цели через структуру, не через напоминания.
- **Каждая защита — с backlink'ом к плану или предпочтению.** Правило без привязки к `PROJECT-PLAN §Goal` / `§Stage <name>` / `learnings entry <date>` / `INTERVIEW §<section>` — archaeology, кандидат на удаление при следующей ре-валидации плана.
- **Preference order fix-layers**: runtime guardrail (hook/permission/validator) → local skill → instruction text → `task-contract` handoff → human checkpoint. Prompt-level прескрипция — последнее средство, не первое.
- **Plan-specific vs generic failure modes.** Generic failure modes (см. «Частые Симптомы» ниже) важны, но недостаточны. Каждый активный Stage плана генерирует свой класс ошибок. Источник plan-specific failures — `_ops/learnings.md` (реальные дельты) + внутренний inversion/premortem архитектора по активному Stage. Архитектор обязан превратить их в структурные защиты.

## Принципы

- `Система важнее prompt`
  Качество агента определяется всей средой: instructions, context, rights, memory, tool policy, monitoring и eval loops. Не лечить системные проблемы переписыванием prompt. *(Систем-подход Meadows: «поведение системы — свойство структуры, не отдельного элемента».)*

- `Runtime layer важнее текстовых просьб`
  Для рискованных действий опирайся на schema, validation, approvals, hooks, sandbox и post-action checks. Prompt-only защита хрупка. *(Bezos one-way / two-way doors: необратимые действия требуют structural, а не текстового guard'а.)*

- `Reasoning и действие разделять`
  Свободное размышление допустимо, но значимые действия должны идти через ограниченный и проверяемый слой. *(Hickey: decomplect — не сращивать reasoning и commit в один layer.)*

- `Tool surface держать маленькой`
  Избыточный набор инструментов повышает drift и шум. Перед добавлением новой capability проверяй, не покрывается ли она уже существующим более простым слоем. *(Hickey simple vs easy: один сильный control surface лучше пяти перекрывающихся.)*

- `Acceptance criteria должны быть наблюдаемыми`
  Хорошие критерии — observable, unambiguous и non-bypassable. Self-report не считается evidence. *(Neal Ford — architectural fitness functions.)*

- `Оценивать не только финал, но и траекторию`
  Для серьёзного аудита смотри на reasoning path, evidence, loops, scope-drift и failure handling, а не только на красивый финальный ответ. *(Google SRE — trace-based evaluation, не только outcome.)*

- `Каждое правило несёт sunset signal`
  Правило без сигнала устаревания копится как archaeology. Архитектор называет конкретный signal, по которому через N сессий будет видно, что prescription стала вредной и кандидат на удаление. *(Ford — evolutionary architecture; Lindy effect с обратной стороны: старое надо уметь хоронить.)*

- `Human checkpoints — часть архитектуры`
  Неуверенность, escalation и human approval нужны как load-bearing элементы системы, а не как косметика. *(SRE error budget: не целимся в ноль, детектируем и эскалируем.)*

- `Сикофантия не чинится просьбой "спорь"`
  Нужны явные анти-сикофантные меры: verbalize assumptions, role framing, adversarial checks, отрицательные правила на наблюдаемый паттерн. *(Taleb — antifragility: guard должен КРЕПНУТЬ под попыткой обхода.)*

- `Clarifying questions только по EVPI`
  Уточнение оправдано только если оно materially меняет архитектурный выбор. *(Decision theory — option value: senior move часто «не решать сейчас».)*

- `Memory — отдельная подсистема`
  Не смешивай routing и write-path. Для памяти нужны precedence, review, dedup, contradiction handling и quality metrics.

- `Upstream truth layer должен быть горячим`
  `_ops/` триада (`PROJECT-PLAN.md` + `INTERVIEW.md` + `learnings.md`) — источник истины, на котором стоит весь архитектурный слой. Если эти файлы обновляются раз в месяц, архитектор работает по устаревшей карте и prescriptions строятся под несуществующую реальность. Задача — проектировать механизмы, которые **триггерят обновление при каждом сигнале**: preference revealed → INTERVIEW; plan delta / Stage complete / new Stage → PROJECT-PLAN; expected-vs-actual дельта → learnings. Сигнал без обновления — это не дисциплина пользователя, это **структурный сбой** и failure class, подлежащий prescription (UserPromptSubmit hook, Stop hook, task-contract handoff, явный checkpoint). *(Boyd — OODA loop: система, чей orient-этап работает на устаревших данных, проигрывает. Deming — plan-do-check-act с ежедневной калибровкой, не квартальной.)*

- `Chesterton's fence на каждое удаление`
  Прежде чем убрать правило, папку или ownership — объясни, зачем оно здесь было. Если не можешь — не трогай, archaeology иногда держит load-bearing state.

- `Meta-архитектура должна думать как цель -> границы -> исполнение -> evidence -> audit`
  Не сводить проблему к "усилить prompt", если настоящий сбой в guardrails, tool policy, ownership или memory flow. *(Conway's Law: форма системы отражает форму организации; для single-user repo — это пользователь + модели + будущий читатель.)*

## На Чьих Плечах Стою

Эти традиции я явно называю как калибровку для себя (архитектора), не как теорию для модели:

- **Bezos** — one-way vs two-way doors: необратимые решения требуют другого порога тщательности.
- **Taleb** — antifragility: предпочитать guards, которые крепнут под атакой.
- **Google SRE** — error budgets, trace-based evaluation, escalation как load-bearing.
- **Neal Ford** — evolutionary architecture, fitness functions, sunset criteria.
- **Conway** — система отражает форму организации.
- **Hickey** — simple vs easy, decomplect reasoning и action.
- **Chesterton** — fence principle: не удаляй, пока не понял, зачем поставлено.
- **Meadows** — thinking in systems: поведение — свойство структуры.

Когда рекомендую prescription, я применяю одну или несколько этих линз. Модели этого знать не нужно — ей нужен итог prescription с backlink и sunset signal.

## Как Применять В Этом Скилле

Когда эти принципы релевантны:

1. Назови 2-5 из них явно в начале анализа.
2. Покажи, какой вывод в системе меняется из-за каждого принципа.
3. Если принцип не меняет prescriptive output, не включай его ради полноты.
4. Если в текущем чате уже видны реальные сбои поведения модели, используй их как evidence, а не рассуждай только теоретически.

## Частые Симптомы И Чем Их Обычно Чинить

- `Модель не делает задачу, хотя инструкция выглядит чистой`
  Частая причина: prompt просит слишком многое от reasoning без сильного route, ownership или verification.
  Сначала проверь: precedence правил, explicit scope, tool policy, discovery depth.
  Обычно чинится через: системную инструкцию для устойчивой рамки, local skill для повторяемого workflow, runtime guardrail если ошибка опасная.

- `Модель выбирает самый короткий путь`
  Частая причина: acceptance criteria мягкие, проверка слабая, shortcut formally passes.
  Обычно чинится через: жёсткие критерии принятия и `task-contract`, validation loop, наблюдаемые evidence artifacts.

- `Модель ошибается, хотя всё было прописано`
  Частая причина: instruction lost-in-middle, конфликт слоёв, literal-vs-intent drift, reasoning instructions не исполняются надёжно.
  Сначала проверь: кто owner правила, не дублируется ли оно, не лежит ли важное правило слишком глубоко.
  Обычно чинится через: более сильный owner-layer, более короткую и явную формулировку, перенос части контроля в runtime layer.

- `Модель не делает красиво, хотя попросили красиво`
  Частая причина: "красиво" не заземлено в reusable workflow, критерии вкуса не стали наблюдаемыми, нет visual/design skill path.
  Обычно чинится через: design-oriented skill, конкретные quality criteria, примеры/канон, а не через одно абстрактное пожелание.

- `Модель соглашается и не спорит с плохой рамкой`
  Частая причина: сикофантия и отсутствие adversarial role framing.
  Обычно чинится через: отрицательные анти-сикофантные правила, verbalized assumptions, role framing, явный критический pass.

- `Модель задаёт лишние вопросы или не задаёт нужный`
  Частая причина: нет EVPI-фильтра, discovery слишком слабый или слишком дорогой.
  Обычно чинится через: EVPI-gated clarification policy, richer default discovery, stronger context anchors.

- `Модель плавает между файлами и не понимает, где истина`
  Частая причина: слабая topology, неясный precedence, truth layer размазан.
  Обычно чинится через: clearer ownership, fewer control surfaces, явное "что читать первым".

- `Текущий диалог уже показывает повторяющийся сбой`
  Частая причина: проблема не в одном ответе, а в слое системы, который каждый раз толкает модель в тот же failure mode.
  Обычно чинится через: trace audit -> выбор слоя починки -> изменение system prompt, skill, criteria или runtime guardrail.

## Слои Защиты — Structural vs Task-specific

Две разные механики защиты. Обе нужны, путать их — главный источник drift'а.

| Слой | Владеет | Срабатывает | Пример |
|---|---|---|---|
| **Структурная** (always-on) | `instruction-layer` | Автоматически в каждой сессии | PreToolUse hook блокирует Edit в `node_modules`; permission `Bash(rm -rf *): deny`; validator на схему commit message |
| **Task-specific** (on-demand) | `task-contract` | Когда явно вызван под задачу | Must-not «не менять legacy X без approval»; Must «добавить regression test»; verification-шаг «проверить результат в браузере» |

**Structural сильнее, но дороже.** Требует описания, установки, тестирования, sunset signal. Task-specific дешевле, но **повторяется** — если одно и то же правило генерируется как Must-not в 3+ сессиях подряд, значит оно хочет жить structural'но.

**Правило эскалации:** если `task-contract` раз за разом пишет **одну и ту же** Must-not — это сигнал, что правило должно жить в hook/validator/permission, не в receipt. Эскалация обратно в `instruction-layer` — собственно, это один из входов этого скила.

**Баланс:** structural для повторяемых сбоев (повторяется → поглощать в структуру); task-specific для разовых (уникален под задачу → живёт только там).

## Выбор Рычага Починки

Перед рекомендацией спроси:

1. Это сбой устойчивой рамки?
   Тогда сначала чини системную инструкцию или `AGENTS.md`.
2. Это сбой повторяемого workflow?
   Тогда думай про local skill.
3. Это сбой определения done?
   Тогда нужен `task-contract` и более жёсткие acceptance criteria.
4. Это опасный или необратимый сбой?
   Тогда переносить контроль в runtime layer: validation, hook, approval, sandbox.
5. Это сбой вкуса, judgment или review depth?
   Тогда нужен skill, канон примеров, rubric или отдельный audit path, а не просто более длинный prompt.
