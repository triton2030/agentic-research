# Criteria Generator — Codex

Рабочая папка по Codex-скиллу `criteria-generator`. Это зеркало Claude Code-версии `projects/meta/criteria-generator--skill-claude-code/` с codex-специфичными адаптациями.

## Что Это

Скилл берёт пользовательскую задачу, читает контекст проекта (сначала стратегическую карту `_ops/`, затем локальные источники), быстро фиксирует LLM-устойчивый execution contract и по умолчанию не тормозит ход работы: коротко напоминает, что важно из `_ops/`, и сразу возвращает агента к задаче.

**Основная роль — переводить `Goal` и активный `Stage` из `_ops/PROJECT-PLAN.md` (плюс релевантные предпочтения из `_ops/INTERVIEW.md`) в локальные task-level критерии, чтобы исполнитель маленькой задачи не терял фокус на общей цели.** Каждый `Must` несёт `Anchored in:` со ссылкой на секцию плана / интервью или явную метку `local-only — <reason>`. Это не общее «усиление критериев», это goal-alignment механизм.

## Почему Именно Такая Форма

Форма скилла собрана под одно load-bearing требование: **не дать исполнителю маленькой задачи потерять связь с глобальной целью.** LLM деградирует, когда цель далеко — задачи выполняются слабее. Каждая механика отвечает на эту проблему:

- **Роль сверху вместо процедурного чек-листа.** Канонический порядок сильного системного промпта (`Роль → Успех → Приоритеты`) ставит роль сверху. Скил знает, что он делает и зачем, прежде чем начинает делать шаги. Это ровно [Karpathy-подход](https://x.com/karpathy/status/2015883857489522876) к современным сильным моделям: *«Don't tell it what to do, give it success criteria and watch it go. Change your approach from imperative to declarative»* — мы даём роль и критерии качества контракта, не длинный процедурный скрипт.
- **Success Criteria For The Contract как первый публичный раздел.** Шесть проверок (Plan-traceability, Observable, Unambiguous, Non-bypassable, Minimal, Non-overlapping) — это **проверка выхода**, а не внутренний шаг процесса. Они подняты наверх, чтобы каждый draft гнался через них, а не оставались зарытыми в конце workflow.
- **Plan-traceability через обязательное поле `Anchored in:` на каждом `Must`.** Это главный механизм goal-alignment. Без обязательного якоря модель легко «формально отчитывается» — Must выглядит специфично, но не связан с глобальной целью. Явное поле `Anchored in: <_ops path + section>` или `Anchored in: local-only — <reason>` делает traceability non-bypassable: либо у тебя есть явная ссылка на план / предпочтения, либо явная пометка, что её нет и почему.
- **Weak plan grounding вместо галлюцинации якоря.** Если `_ops/PROJECT-PLAN.md` отсутствует — скилл **честно помечает контракт как weak plan grounding** и держит его тоньше, а не выдумывает план. Это защита от самого опасного failure mode: фабрикация стратегического контекста, которого нет.
- **4 шага вместо 10.** Capture → Discover → Draft+Adversarial+Gate loop → Emit. Процедура свёрнута до минимума. Императивная спина не даёт ценности — ценность даёт порядок чтения (`_ops/` first) и квалити-чек на выходе. Всё остальное — machinery, не judgment.
- **Discover — план и предпочтения first, then local.** `_ops/PROJECT-PLAN.md` и `_ops/INTERVIEW.md` читаются первыми, всегда (если есть). Локальные источники (AGENTS.md, README, docs/) — по роли, не по чек-листу. Это чтобы upstream-рамка попадала в контракт раньше локальной специфики.
- **Hard gate против scope creep без стоп-кадра.** Скилл не создаёт `_ops/` и не тащит в контракт чужие архитектурные решения, но сам `contract` режим больше не делает обязательную паузу: после короткого receipt и простого `_ops`-напоминания агент продолжает текущую задачу.
- **Adversarial pass + Quality Gate в одном loop.** Draft → attack как ленивый агент → прогон через 6 success criteria → повтор. Это TDD для контрактов: сначала тест (adversarial + gate), затем pass (укрепление criteria). Из Karpathy: *«Get it to write tests first and then pass them»*.
- **Budgets 2-4 Must / 0-2 Must not / 1-3 verification steps.** Over-constraint — собственная форма bypass. Короткий контракт, который реально читают, сильнее длинного, который быстро игнорируют.

Все эти механики — ответ на конкретные failure modes. Ни одна не декоративна.

## Отличия От Claude Code Версии

Функционально и структурно идентичны. Различия чисто платформенные:

- **EVPI questions.** В Claude Code используется native `AskUserQuestion` tool с дискретными опциями. В Codex нет аналога — вопрос задаётся в чате свободным текстом, но с тем же разделением на 2-4 опции и tradeoff'ами в description.
- **Активация.** В Claude Code — через `Skill` tool с именем. В Codex — нативно по имени скила.
- **Progressive disclosure references.** В Claude Code `references/` открываются через Skill tool. В Codex — через обычный file read по необходимости.
- **Runtime механизмы в Hard Gate.** В тексте скила упоминаются «validators, approvals» вместо «hooks, permissions» — семантика идентична, терминология подстроена под Codex.

Ни одно из отличий не меняет core discipline: Role-first, Success Criteria с обязательным Anchored in:, 4-step process, Hard Gate, adversarial+gate loop.

## Связь С Другими Скиллами

- **Upstream**: `main-strategy` владеет `_ops/INTERVIEW.md`, `_ops/PROJECT-PLAN.md`, `_ops/learnings.md`. Без этой карты контракт помечается как weak plan grounding.
- **Архитектурный upstream**: `system-architect` переводит план и предпочтения в durable instruction layer (validators, approvals, AGENTS.md, local skills). Если owner / control-surface / system shape ещё не закреплён и живёт только в чате — `criteria-generator` не берёт архитектурное решение на себя, а возвращает задачу в `system-architect`.
- **Обратная связь**: если `criteria-generator` раз за разом пишет одну и ту же Must-not для одного паттерна — это сигнал `system-architect`, что правило должно жить в validator или AGENTS.md, а не в каждом task contract.

## Файлы

- `SKILL.md` — ядро: Role, Success Criteria, Hard Gate, 4-step process, Red Flags.
- `references/discovery-map.md` — карта источников контекста (по типу проекта и типу задачи).
- `references/failure-modes.md` — каталог типовых LLM-халтур с пробами и контрмерами (для adversarial pass).
- `references/format-examples.md` — три рабочих примера output (bugfix / research / skill creation) с `Anchored in: local-only — ...` как демонстрация корректного поведения без `_ops/`.
- `agents/openai.yaml` — Codex metadata для routing и UI.

Во время исполнения скилл ничего не пишет в `_ops/`. Его выход в `contract` режиме — компактный receipt, короткое напоминание что держать в голове из `_ops/`, затем немедленный возврат к работе.

## Куда Деплоить

В пользовательский каталог скиллов Codex (ориентировочно `~/.codex/skills/criteria-generator/`). Путь подтвердить по текущей конфигурации Codex перед деплоем.
