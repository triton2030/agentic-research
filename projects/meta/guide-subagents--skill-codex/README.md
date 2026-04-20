# Guide Subagents — Codex

Рабочая папка по Codex-скиллу `guide-subagents`.

## Что Это Закрывает

Нативные субагенты в Codex полезны не сами по себе, а только когда у них есть ясная роль, узкая зона ответственности и хороший brief на входе.

Без этого мультиагентность легко превращается в шум: дублирование работы, слабые формулировки, пересечение ownership и красивые, но пустые ответы.

`guide-subagents` нужен для другой точки в процессе. Он не заменяет платформенную возможность `subagents`, а готовит её к нормальному запуску:

- сначала понять, действительно ли делегация здесь нужна;
- потом отделить локальный следующий шаг главного агента от параллельных потоков;
- потом написать brief для каждого субагента;
- и только после этого спросить пользователя, хочет ли он запуск.

## Чем Он Отличается От Native `subagents`

Native `subagents` в Codex — это исполнительный слой. Они позволяют реально запустить отдельных агентов с отдельным контекстом.

Этот skill — помощник и слой подготовки. Он отвечает за качество развилки до запуска:

- нужен ли вообще запуск;
- сколько субагентов должно быть;
- какие роли и границы уместны;
- как должен звучать prompt, чтобы субагент не дрейфовал и не дублировал соседей;
- где нужна пауза и прямое подтверждение пользователя.

Коротко: `subagents` как platform feature делают работу. Наш `guide-subagents` skill помогает правильно подготовить эту работу до запуска.

## На Что Опирается

Скилл собран как короткий reusable workflow на базе этих материалов репозитория:

- [knowledge/wisdom-agents.md](/Users/triton/Documents/GitHub/agentic-research/knowledge/wisdom-agents.md)
- [knowledge/wisdom-skills-plugins.md](/Users/triton/Documents/GitHub/agentic-research/knowledge/wisdom-skills-plugins.md)
- [knowledge/wisdom-codex.md](/Users/triton/Documents/GitHub/agentic-research/knowledge/wisdom-codex.md)
- [knowledge/research/meta/learnings.md](/Users/triton/Documents/GitHub/agentic-research/knowledge/research/meta/learnings.md)
- [knowledge/guides/perfect-skills.md](/Users/triton/Documents/GitHub/agentic-research/knowledge/guides/perfect-skills.md)
- [projects/meta/criteria-generator--skill-codex/SKILL.md](/Users/triton/Documents/GitHub/agentic-research/projects/meta/criteria-generator--skill-codex/SKILL.md)

Главная идея, которую он заимствует у `criteria-generator`: сначала укрепить рамку и критерии хорошего handoff-а, потом переходить к действию.

## Файлы

- `SKILL.md` — тонкое ядро workflow.
- `references/` — шаблон brief'а, shape ответа, split-паттерны и red flags.
