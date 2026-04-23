# Task Planner — Codex

Рабочая папка по Codex-скиллу `task-planner`. Это зеркало Claude Code-версии `projects/meta/task-planner--skill-claude-code/` с codex-специфичными адаптациями.

## Что Это

Владелец файла задачи `_ops/plans/phase-NN-<slug>/task-MM-<slug>.md`. Для нетривиальных задач внутри активной фазы из `_ops/PROJECT-PLAN.md` создаёт, поддерживает и закрывает task-файлы. Три секции — Цель / Подшаги / Критерии приёмки — пишутся этим скилом целиком.

Upstream-карта — `_ops/PROJECT-PLAN.md` и `_ops/INTERVIEW.md`, владеет ими `main-strategy`. Критерии приёмки — Must / Must-not / Verification protocol, каждый `Must` несёт `Anchored in:` со ссылкой на секцию плана / интервью, либо `local-only — <reason>` (разрешена только для критериев о самом коде). Это goal-alignment механизм, не общее «усиление критериев».

## Почему Именно Такая Форма

Форма скилла собрана под одно load-bearing требование: **не дать исполнителю маленькой задачи потерять связь с глобальной целью.** LLM деградирует, когда цель далеко — задачи выполняются слабее. Каждая механика отвечает на эту проблему:

- **Роль сверху вместо процедурного чек-листа.** Канонический порядок сильного системного промпта (`Роль → Успех → Приоритеты`) ставит роль сверху. Скил знает, что он делает и зачем, прежде чем начинает делать шаги. Это ровно [Karpathy-подход](https://x.com/karpathy/status/2015883857489522876) к современным сильным моделям: *«Don't tell it what to do, give it success criteria and watch it go. Change your approach from imperative to declarative»*.
- **Владение task-файлом целиком.** Три секции (Цель / Подшаги / Критерии приёмки) — одна зона ответственности, одна точка правды. `main-strategy` владеет планом и папками фаз, но **не** содержимым task-файлов.
- **Plan-Anchor Gate (блокирующий).** Без якоря в PROJECT-PLAN значимая задача не начинается; `local-only` как обход запрещён. Это защита от самого опасного failure mode: фабрикация стратегического контекста.
- **Семь gate-правил на критерии.** Anchor traceability, Observable, Unambiguous, Non-bypassable, Minimal, Non-overlapping, On-trajectory. Каждый `Must` гонится через них. План — whitelist, а не wishlist: критерий на будущее, через которое траектория не проходит, отбрасывается.
- **5 шагов вместо 10.** Locate → Discover → Draft+Adversarial+Gate loop → Commit → Receipt. Ценность даёт порядок чтения (`_ops/` first) и квалити-чек на выходе, а не длинный процедурный скрипт.
- **Default не блокирует работу.** После записи файла и компактного receipt агент сразу возвращается к задаче. Скил — контракт, не пауза.
- **Budgets 2-4 Must / 0-2 Must not / 1-3 verification steps.** Over-constraint — собственная форма bypass. Короткий контракт, который реально читают, сильнее длинного, который быстро игнорируют.
- **Эфемерный слой `_ops/plans/`.** `main-strategy` может переставить или удалить фазы целиком (например, при смене Goal или технологии). Поэтому ничто снаружи не ссылается на пути внутри `_ops/plans/`; `Anchored in:` указывает только на `PROJECT-PLAN.md` или `INTERVIEW.md`, а сам план не перечисляет task-файлы.

Все эти механики — ответ на конкретные failure modes. Ни одна не декоративна.

## Отличия От Claude Code Версии

Функционально и структурно идентичны. Различия чисто платформенные:

- **EVPI questions.** В Claude Code используется native `AskUserQuestion` tool с дискретными опциями. В Codex нет аналога — вопрос задаётся в чате свободным текстом, но с тем же разделением на 2-4 опции и tradeoff'ами в description.
- **Активация.** В Claude Code — через `Skill` tool с именем. В Codex — нативно по имени скила.
- **Progressive disclosure references.** В Claude Code `references/` открываются через Skill tool. В Codex — через обычный file read по необходимости.
- **Runtime механизмы в Hard Gate.** В тексте скила упоминаются «validators, approvals» вместо «hooks, permissions» — семантика идентична, терминология подстроена под Codex.

Ни одно из отличий не меняет core discipline: Role-first, Plan-Anchor Gate, семь gate-правил, 5-step lifecycle.

## Связь С Другими Скиллами

- **Upstream**: `main-strategy` владеет `_ops/INTERVIEW.md`, `_ops/PROJECT-PLAN.md`, `_ops/learnings.md`, папками фаз в `_ops/plans/`. Без этой карты значимая задача блокируется.
- **Архитектурный upstream**: `system-architect` переводит план и предпочтения в durable instruction layer (validators, approvals, AGENTS.md, local skills). Нерешённый control-surface → `task-planner` возвращает задачу в `system-architect`.
- **Обратная связь**: если `task-planner` раз за разом пишет одну и ту же Must-not для одного паттерна — это сигнал `system-architect`, что правило должно жить в validator или AGENTS.md, а не в каждом task contract.

## Файлы

- `SKILL.md` — ядро: Role, режимы, Plan-Anchor Gate, 5-step lifecycle, Red Flags.
- `references/task-file-lifecycle.md` — полный процесс default-режима: Locate, Discover, Draft, Adversarial, Commit, Receipt + семь gate-правил.
- `references/strategy-trace-mode.md` — read-only режим alignment-проверки артефакта.
- `references/pulse-check-mode.md` — read-only dialog-time memory probe.
- `references/discovery-map.md` — карта источников контекста (по типу проекта и типу задачи).
- `references/failure-modes.md` — каталог типовых LLM-халтур с пробами и контрмерами.
- `references/format-examples.md` — рабочие примеры output на разных типах задач.
- `agents/openai.yaml` — Codex metadata для routing и UI.

Во время исполнения скил пишет **только** task-файл. `_ops/PROJECT-PLAN.md`, `_ops/INTERVIEW.md`, `_ops/learnings.md` и папки фаз — зона `main-strategy`.

## Куда Деплоить

В пользовательский каталог скиллов Codex (ориентировочно `~/.codex/skills/task-planner/`). Путь подтвердить по текущей конфигурации Codex перед деплоем.
