# Meta — Инвентарь Codex

Снимок на 22 апреля 2026.

Инвентарь смешанный: здесь перечислены и repo-local project artifacts, и globally available handles, которые реально доступны в рабочей среде. Если локальной проектной папки нет или она ушла в `projects/_archive/`, сначала проверяй installed handle; archived folder сам по себе не делает capability живой.

## Что Есть

### criteria-generator
- Тип: skill
- Источник: наш
- Что делает: превращает пользовательскую задачу в тот же запрос с добавленными LLM-устойчивыми критериями приёмки

### main-strategy
- Тип: skill
- Источник: наш
- Что делает: владеет durable project framing через `_ops/PROJECT-PLAN.md`, `_ops/INTERVIEW.md` и `_ops/learnings.md`

### system-architect
- Тип: skill
- Источник: наш
- Что делает: аудирует и улучшает систему агентных инструкций, папок и capabilities так, чтобы новая сессия модели понимала truth layer, приоритеты, routing и границы работы

### step-back
- Тип: skill
- Источник: наш
- Что делает: делает один короткий zoom-out / reframe, когда разговор ушёл в sycophancy drift, tunnel vision или debug loop

### subagents (native)
- Тип: agent
- Источник: OpenAI
- Что делает: позволяют запускать в Codex специализированных агентов с отдельным контекстом и распределять работу по ролям

### guide-subagents
- Тип: skill
- Источник: наш
- Что делает: помогает подготовить запуск native Codex subagents через чат — отделяет локальный следующий шаг от параллельных потоков, пишет сильные brief'ы и только потом просит явное подтверждение пользователя

### llm-wisdom
- Тип: skill
- Источник: наш, globally available; repo-local версия архивирована
- Что делает: даёт переносимую библиотеку знаний о поведении LLM, типовых failure modes, shortcutting и сильных control levers при создании агентов, промптов и скиллов

### skills
- Тип: skill
- Источник: OpenAI
- Что делает: задают повторяемый workflow-слой поверх обычного поведения Codex

### plugins
- Тип: plugin
- Источник: OpenAI
- Что делает: упаковывают skills, app integrations и MCP в расширяемый слой Codex

## Чего Не Хватает

- Memory skill — гибридная активация и безопасная запись пользовательских, проектных и стратегических знаний в scoped память с confirmation, merge и audit
- Builder-agent для typed `AgentSpec`, tool bundle и eval bundle
- Promotion rule: когда знание остаётся в `_research/`, а когда переходит в устойчивые правила
