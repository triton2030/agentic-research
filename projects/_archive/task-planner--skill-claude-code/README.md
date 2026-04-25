# Task Planner — Claude Code

Клодовская версия скилла `task-contract`. Рядом лежит кодексовская версия: `projects/meta/task-contract--skill-codex/`.

## Что Это

Владелец файла задачи `_ops/plans/phase-NN-<slug>/task-MM-<slug>.md`. Под каждый активный Step из `_ops/PROJECT-PLAN.md` создаёт, поддерживает и закрывает один task-файл. Три секции — Цель / Подшаги / Критерии приёмки — пишутся этим скилом целиком.

Если `_ops/PROJECT-PLAN.md` и `_ops/INTERVIEW.md` существуют, считает их upstream картой от `project-strategy`. Критерии приёмки — Must / Must-not / Verification protocol, каждый `Must` несёт `Anchored in:` со ссылкой на секцию плана / интервью, либо явную метку `local-only — <reason>` (разрешена только для критериев о самом коде). Это goal-alignment механизм, не общее "усиление критериев".

## Ключевые Правила

- **Один файл на Step**. Путь задан: `_ops/plans/phase-NN-<slug>/task-MM-<slug>.md`. Сам скил папки фаз не создаёт — ими владеет `project-strategy`.
- **Plan-Anchor Gate (блокирующий)**: если задача не якорится ни в одном элементе PROJECT-PLAN — откат в `project-strategy`. `local-only` как обход запрещён.
- **Эфемерный слой**: `_ops/plans/` может быть переставлен или удалён `project-strategy` целиком. Ничто снаружи не должно цитировать пути внутри `_ops/plans/`. `Anchored in:` ссылается только на `PROJECT-PLAN.md` или `INTERVIEW.md`.
- **В default режиме не блокирует работу**: после записи файла и компактного receipt сразу возвращает агента к задаче.

## Отличия От Кодекс-Версии

- В Claude Code можно использовать `AskUserQuestion` для 1-3 load-bearing EVPI-вопросов, когда инструмент доступен.
- Нет `agents/openai.yaml`; routing держится на frontmatter Claude Code.

## Файлы

- `SKILL.md` — ядро, адаптированное под Claude Code.
- `references/task-file-lifecycle.md` — полный процесс default-режима: Locate, Discover, Draft, Adversarial, Commit, Receipt + семь gate-правил.
- `references/strategy-trace-mode.md` — read-only режим alignment-проверки артефакта.
- `references/pulse-check-mode.md` — read-only dialog-time memory probe.
- `references/discovery-map.md` — карта источников контекста.
- `references/failure-modes.md` — каталог типовых LLM-халтур с пробами и контрмерами.
- `references/format-examples.md` — рабочие примеры output на разных типах задач.

Во время исполнения скил пишет **только** task-файл. `_ops/PROJECT-PLAN.md`, `_ops/INTERVIEW.md`, `_ops/learnings.md` — зона `project-strategy`, сюда не пишет.

## Куда Деплоить

В `~/.claude/skills/task-contract/` для персонального Claude Code skill, либо в `.claude/skills/task-contract/` внутри проекта.
