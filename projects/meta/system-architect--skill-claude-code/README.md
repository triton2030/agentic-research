# System Architect — Claude Code

Скилл-архитектор проекта: проектирует среду, в которой **и пользователь, и ИИ дешевле делают правильное действие, чем неправильное**.

## Что делает

Проектирует систему как целое: runtime (hooks, permissions, MCP), skills (marketplace + local), папки и навигацию, AGENTS.md-слои, память (`_ops/`). Горизонт 6-24 месяца, не одна задача. Учитывает двух пользователей системы — человека и AI-сессию.

## Позвоночник мышления — 8 шагов

1. **Telos** — зачем система (PROJECT-PLAN Goal).
2. **As-is map** — что уже установлено. First-order артефакт.
3. **Forces** — что будет давить 6-24 месяца. Design constraint на вход.
4. **Failure classes** — сбои, сгруппированные в классы.
5. **Leverage analysis** — одна правка, убивающая класс.
6. **Prescriptions** — reuse-first gate + preference order + backlink + sunset.
7. **Minimize pass** — перед emit пытаюсь удалить.
8. **Handoff + verification** — default route, criteria handoff, forces verification.

**Ключевое:** As-is map и Forces стоят **до** failure scan. Иначе архитектор сканит вслепую и изобретает то, что уже установлено.

## Работает downstream от `main-strategy`

- **Upstream**: `main-strategy` владеет PROJECT-PLAN + INTERVIEW + learnings. Без заполненных Goal и активного Stage архитектор блокируется и возвращается к стратегу.
- **Downstream**: `criteria-generator` получает handoff с указанием durable instruction surfaces как upstream. Если архитектор отработал хорошо, `criteria-generator` делает меньше работы — правила живут в fabric.

## Два уровня защиты

- **Структурная** (always-on) — `system-architect` через hooks, permissions, AGENTS.md, skill routing. Автоматически в каждой сессии.
- **Task-specific** (on-demand) — `criteria-generator` через acceptance criteria. Когда явно вызван.

Если `criteria-generator` раз за разом пишет одну Must-not для одного паттерна — правило должно жить в hook/validator, эскалация обратно в архитектора.

## Preference order fix-layers

1. Runtime guardrail (hook / permission / validator).
2. Local skill.
3. Instruction text (AGENTS.md / prompt).
4. `criteria-generator` handoff.
5. Human checkpoint.

Prompt-level — **последнее средство**. Canon: *«runtime layer важнее текстовых просьб»*.

## Обязательные Gates

- **Upstream content gate** — без конкретного Goal и активного Stage аудит блокируется.
- **Capability inventory gate** — prescriptions без As-is map невалидны.
- **Reuse-first gate** — prescription на новое без показа gap в существующем невалидна.
- **Backlink + sunset** — каждая prescription несёт оба.
- **Minimize gate** — перед emit обязателен прогон удаления.
- **Forces verification gate** — sunset signals обязаны совпадать с early signals сил.

## Файлы

- `SKILL.md` — ядро: позвоночник, gates, AskUserQuestion, preference order, Done when.
- `references/workflow.md` — детальные 8 шагов + subagent probe + AskUserQuestion.
- `references/output-shape.md` — форма финального audit result.
- `references/audit-lenses.md` — линзы для Reality, Navigation, Legibility, Pressure, Trace.
- `references/system-building-principles.md` — принципы AI system design.
- `references/claude-code-guardrails.md` — каталог Claude Code механизмов.
- `references/local-skill-contract.md` — proof gate для нового skill.
- `references/anti-patterns.md` — «чему я не верю».

Все references открываются progressive disclosure'ом, только когда вопрос возник. Не читать всё заранее.
