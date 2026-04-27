# Output Shape

Форма финального audit result. Секции следуют позвоночнику 8 шагов.

```md
## Тип evidence
- `direct trace` | `user-reported summary` | `structure-only`
- Ограничение: ...

## Refs applied
- references/workflow.md
- references/output-shape.md
- references/audit-lenses.md
- <реально прочитанные: anti-patterns.md, claude-code-guardrails.md, local-skill-contract.md, system-building-principles.md>

Пустая секция = сбой Gate, audit невалиден.

## 1. Telos
- PROJECT-ROADMAP §Goal: <1 строка verdict — заполнен/generic/пуст>
- PROJECT-ROADMAP §Stage (релевантный): <1 строка — заполнен/generic/отсутствует>
- INTERVIEW: <релевантная секция названа | отсутствует>
- learnings.md: <пуст | есть конкретные дельты | generic>
- Состояние `_ops/` truth layer: `hot` | `cold` — что именно отстаёт или отсутствует.

Generic Goal или пустой Stage → audit блокирован, откат в `project-roadmap`.

## 2. As-is Map

Точные handles, не классы. Формат: `<handle> — <что делает> — <покрывает failure class N?>`.

### Hooks
- `<event> × <matcher>` → <действие> — покрывает Failure class <N> | не покрывает ничего видимого

### Permissions
- `<Tool(matcher)>: allow|deny|ask` (<scope>) — комментарий

### Skills
- `<имя>` (<marketplace|user|project>) — triggers: <...> — покрывает класс <N>

### MCP servers
- `<имя>` (<scope>) — реально доступные `mcp__*` prefixes: ...

### Subagents
- `<имя>` — allowed-tools: <...> — use case

### Instruction слои
- `<путь к AGENTS.md/CLAUDE.md>` — precedence: <...> — load-bearing правила: <...>
- Root task-contract routing: <explicit frequent route present | missing | not in scope>

### `_ops/` состояние
- PROJECT-ROADMAP.md: <реально заполнен | шаблон | частично>
- INTERVIEW.md: <...>
- learnings.md: <...>

### Папки в scope (если applicable)
- `<путь>/` — что производит — якорь в PROJECT-ROADMAP/INTERVIEW

### Mismatch между текстом и реальностью
- `<instruction text ссылается на X>` → реально: <не установлено | активно | matcher другой>. Уходит в Failure class <N>.

## 3. Forces

Design constraint на вход. 2-3 силы.

### Force 1: <название>
- **Что это**: <смена модели | рост репо | новый класс задач | pivot | ...>
- **Early signal**: <по чему увижу, что приехала>
- **Constraint**: что я из-за этого **не** буду проектировать — <конкретно>

### Force 2: ...
### Force 3: ...

Generic («AI будет развиваться») отброшено. Если сила без early signal или без constraint — удалить.

## 4. Failure Classes

### Class A: <короткое имя класса>
- **Root**: <общий корень, plan-specific>
- **Failures в классе**:
  - Failure A1: <что конкретно пойдёт не так> — из `learnings.md YYYY-MM-DD` | из inversion по §Stage
    - Где система позволяет: <конкретное слабое место>
    - Что из As-is map должно было покрывать: <handle> — **почему не покрывает**: <не установлено | matcher узкий | prompt-only игнорируется>
  - Failure A2: ...
- **Prescription**: см. Prescription <N> ниже

### Class B: ...

## 5. Leverage Analysis

### Cluster 1 (rank: high|medium|low)
- **Root**: <common root>
- **Systemic fix**: <одна интервенция>
- **Покрывает failures**: A1, A3, B2 (из Шага 4)
- **Становится Prescription**: <N>

### Cluster 2: ...

### Residual (1:1 patches, rank: low)
- Failure C1 → Prescription <M>

## 6. Prescriptions

### Prescription 1
- **Reuse-first gate**:
  - Что уже покрывает частично: <handle из Шага 2 | ничего не покрывает>
  - Почему недостаточно: <одна строка gap>
  - Default: <расширить существующее <handle> | добавить новое, потому что <reason>>
- **Fix-layer**: `runtime guardrail` | `local skill` | `instruction text` | `task-contract handoff` | `human checkpoint`
- **Если не runtime**: почему runtime/skill альтернатива отклонена — одна строка.
- **Механизм** (если runtime): тип hook'а / permission rule / subagent config — с отсылкой на [claude-code-guardrails.md](claude-code-guardrails.md).
- **Backlink**: `→ protects PROJECT-ROADMAP §Goal` / `→ protects §Stage <name>` / `→ addresses learnings entry YYYY-MM-DD` / `→ honors INTERVIEW §<section>`. Без backlink'а невалидна.
- **Observable signal**: один конкретный сигнал через N сессий.
- **Sunset signal**: один конкретный сигнал устаревания. **Обязан соотноситься с early signal одной из Сил (Шаг 3).**
- **Owner**: <какой файл/механизм владеет как source of truth>.
- **Subagent probe** (для load-bearing): краткий итог A/B или adversarial probe. Для мелких — явно `пропущен — prescription косметическая`.

### Prescription 2: ...

## 7. Minimize Pass

Обязательный output (молчание = сбой Gate).

### Удалено
- <правило/файл/папка> — <причина удаления> — Chesterton's fence probe: <что сломал бы, если оставил>

### Смерджено
- <правило A> + <правило B> → <new unified rule> — причина: <>

### Оставлено несмотря на подозрение
- <элемент> — <почему не трогаем>: <Chesterton's fence держит load-bearing state | неясно, без user input не удалить>

Если действительно ничего не сделано — явно: `Ничего не удалено/смерджено/оставлено под вопросом. Система уже минимальна.`

## 8. Handoff + Verification

### Default Route For Fresh Session
- **Читает первым**: <один файл>
- **Skill на типичные триггеры**: <skill X на триггер Y>
- **Когда вызывает `task-contract`**: <task discussion | edits | status/movement | criteria check | closeout>
- **Hooks срабатывают автоматически**: <какие и когда>
- **Буквальная формулировка load-bearing правила**: *«<точная цитата>»*
- **Если `_ops` холодный**: <что блокирует hardening и как уходим в `project-roadmap`>
- **Что блокирует действие до этого шага**: <>

### `task-contract` Handoff (если нужен)
- Durable instruction surfaces как upstream: <AGENTS.md § | skill X | hook Y output | validator Z>
- Task-level constraints наследуются из них: <>

### `project-roadmap` handoff
(Только если вскрыт upstream drift или ownership contamination.)
- Что нужно пересинхронизировать: ...
- Какой из `_ops/PROJECT-ROADMAP.md` / `_ops/INTERVIEW.md` / `_ops/learnings.md` остыл, отсутствует или не отражает реальность: ...
- Какой sign of reality надо туда занести сейчас: ...
- Почему это не owner `skill-architect`: ...
- Следующий шаг `project-roadmap`: ...

### Forces Verification
- **Force 1** → уязвимые prescriptions: <N, M>; совпадает ли sunset signal с early signal: <да/нет; если нет — перепроектирую или удаляю силу>
- **Force 2** → ...
- **Force 3** → ...

Если ни одна prescription не уязвима ни к одной силе — либо силы нерелевантны (признаю), либо design слишком жёсткий (перепроверяю).

## Folder Audit (только если папки в scope)
- `<путь>/`
  - Что производит: ...
  - Якорь: `PROJECT-ROADMAP §Stage <name>` | `INTERVIEW §<section>` | отсутствует
  - Negative list: есть | отсутствует
  - Verdict: `keep` | `archive` | `remove` | `нужен AskUserQuestion`

## Сигналы из текущего диалога (если direct trace)
- Наблюдение: ...
  Что показывает о системе: ...
  В какую Failure class попадает: ...

## Минимальные следующие изменения
1. ...
2. ...
3. ...
```

## Правила использования формы

- Секции `1. Telos`, `2. As-is Map`, `3. Forces`, `4. Failure Classes`, `5. Leverage`, `6. Prescriptions`, `7. Minimize Pass`, `8. Handoff + Verification` — **обязательные, в этом порядке**.
- Prescriptions без reuse-first gate / backlink / observable / sunset — не публикуй.
- Sunset signal, не совпадающий ни с одним early signal из Forces — валидный только если явно помечен как `не связан с Forces — <причина>`.
- `Subagent probe` — обязателен для load-bearing prescriptions. Для косметических — явно `пропущен — причина`, не молчание.
- `Minimize pass` — обязателен; молчание = сбой Gate.
- `Forces Verification` — обязателен даже если по результату ничего не меняется.
- `Folder Audit` — только когда папки реально в scope.
- Если prescription рекомендует конкретный Claude Code-механизм — ссылайся на [claude-code-guardrails.md](claude-code-guardrails.md), не переписывай теорию.
