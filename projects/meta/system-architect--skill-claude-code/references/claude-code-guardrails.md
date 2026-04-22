# Claude Code Guardrails — каталог механизмов

Открывай этот файл только когда prescription требует конкретный Claude Code-specific механизм (hook, permission, subagent, MCP, skill). Для generic AI system thinking — `system-building-principles.md`.

Порядок предпочтения при проектировании защиты: **runtime (hooks/permissions) → local skill → instruction text → criteria-generator handoff → human checkpoint**. Prompt-level правила — последнее средство, не первое.

## Hooks — события и когда их использовать

Hooks — shell-команды или prompt'ы, которые Claude Code выполняет на определённых событиях. Настраиваются в `.claude/settings.json` (project) или `~/.claude/settings.json` (user). Это **самый сильный защитный слой**, потому что работает до/после tool call, не завися от reasoning модели.

### PreToolUse

Срабатывает **до** выполнения tool call. Может заблокировать tool (`exit 2`) или изменить аргументы.

Use cases:
- Блок опасных Bash-команд (`rm -rf`, `git push --force` без явного разрешения).
- Проверка что Write путь не выходит за project scope (sandbox enforcement).
- Валидация что commit не содержит секретов до `git commit`.
- Блок Edit файла если в пути есть запрещённые папки (`node_modules/`, `.git/`).

Пример prescription: *«Для failure "модель правит файлы в node_modules" → PreToolUse hook на Write, matcher `node_modules/**`, exit 2 с объяснением».*

### PostToolUse

Срабатывает **после** tool call. Не может отменить уже выполненное действие, но может:
- Запустить validator (eslint, prettier, test subset) и, если fail, сказать модели исправить.
- Обновить log / learnings / state file.
- Инъектировать контекст для следующего шага (*«файл X изменён, проверь связанный Y»*).

Use cases:
- Post-commit validator (lint / typecheck после Edit).
- Автоматическая запись learnings при корректировке пользователем.
- Обновление `_ops/learnings.md` когда session завершается.

### UserPromptSubmit

Срабатывает когда пользователь отправляет сообщение, **до** обработки моделью. Может инъектировать дополнительный контекст.

Use cases:
- Автоматически добавить `Read: _ops/PROJECT-PLAN.md` если prompt затрагивает архитектурное решение.
- Предупредить если session давно не ре-валидировала активный Stage (*«PROJECT-PLAN last touched 2 months ago — revisit?»*).
- Инъектировать напоминание про активный Stage в начале сессии.

### Stop / SubagentStop

Срабатывает когда модель завершает ответ (Stop) или subagent завершает работу (SubagentStop). Может заставить продолжить или выполнить финальный check.

Use cases:
- Проверка что `Done when` условия скилла реально выполнены перед завершением сессии.
- Финальный lint / test пройдёт перед тем как модель объявит «готово».
- Assertion что durable файлы (`_ops/*.md`) обновлены если sessional работа это требовала.

### SessionStart

Срабатывает при старте сессии. Инъектирует контекст один раз.

Use cases:
- Загрузка `_ops/PROJECT-PLAN.md` в системный prompt как context anchor.
- Проверка свежести активного Stage в PROJECT-PLAN.
- Warning пользователю если `_ops/` давно не обновлялся.

## Permission rules

В `settings.json` → `permissions` задают allow/deny/ask для tool calls. Syntax: `Tool(matcher)`.

### Allow / Deny / Ask

- `allow` — tool выполняется без prompt'а.
- `deny` — tool блокируется, модель видит refusal и должна искать другой путь.
- `ask` — пользователю показывается prompt с Y/N.

Примеры matcher'ов:
- `Bash(git push:*)` — все `git push` команды.
- `Bash(npm install:*)` — инсталлы.
- `Write(~/.ssh/**)` — writes в SSH keys.
- `Edit(CLAUDE.md)` — edits к root CLAUDE.md.

### Scope

- **User scope** (`~/.claude/settings.json`) — применяется во всех проектах.
- **Project scope** (`<repo>/.claude/settings.json`) — только в этом проекте. Precedence выше user.
- **Local scope** (`<repo>/.claude/settings.local.json`) — не коммитится, персональные overrides.

### Когда использовать permission vs hook

Permission = **бинарный allow/deny/ask на основе matcher**. Простой, декларативный.
Hook = **выполняет код/prompt**, может анализировать аргументы tool call, давать контекстный refusal.

Для «никогда не выполнять `rm -rf /`» — permission. Для «блокировать Edit если файл содержит секреты» — hook (нужна логика).

## Subagent isolation

Subagents (Agent tool) запускаются в отдельном context. Опция `isolation: "worktree"` создаёт временный git worktree — subagent работает на изолированной копии репо.

Use cases:
- Эксперименты, которые могут сломать main branch.
- Batch/destructive операции.
- Параллельная работа агентов без гонок.
- Untrusted tool calls.

Допустимые инструменты subagent'а задаются в его frontmatter (`tools: [Read, Grep]` — read-only). Для высокорисковых ролей это критично: **default к read-only + worktree** снижает blast radius.

## MCP scope

MCP-серверы (`mcp__*` tool prefixes) регистрируются в `settings.json` → `mcpServers`.

- User scope — доступен во всех проектах.
- Project scope — только в этом проекте.
- `extraKnownMarketplaces` — для directory-based плагинов.

Use case в prescription'ах: *«Для failure "модель пытается реальный browser action без проверки" → project-scoped MCP `playwright` с explicit tool list, user не получает доступ к browser в несвязанных проектах»*.

## Skills — rigid vs flexible

Skills в плагинах (marketplace или local) — повторяемые workflows с triggers.

### Rigid skill

Следует точно, без адаптации. Каждый шаг обязателен.

Когда использовать: когда дисциплина и порядок сами создают ценность.
Примеры: `main-strategy` (thinking workflow для durable bet), `criteria-generator` (task-level контракт), TDD, security review.

### Flexible skill

Задаёт рамку и сильные defaults, но адаптируется к контексту. Какие шаги применять — зависит от задачи.

Когда использовать: когда variance в задачах высокая, но общая рамка помогает.
Примеры: `system-architect` (audit + design), frontend-design, research audit.

### Allowed tools в frontmatter

Можно ограничить инструменты, доступные скиллу. Снижает drift.

```yaml
allowed-tools: Read, Grep, Glob, Bash(git log:*)
```

Use case: skill, который только читает и анализирует — никогда не должен писать. Prescription: *«audit-skill с `allowed-tools: Read, Grep, Glob` — архитектурная гарантия, что он не изменит файлы даже если reasoning решит это сделать»*.

## Как выбрать механизм

| Симптом | Первый выбор | Почему |
|---|---|---|
| Модель пишет не туда | PreToolUse hook | Structural block на Write path. |
| Модель забывает читать PROJECT-PLAN | SessionStart + UserPromptSubmit hooks | Context injection до reasoning. |
| Модель запускает опасную команду | Bash permission deny + PreToolUse safeguard | Два слоя защиты. |
| Модель не проверяет свою работу | PostToolUse hook (validator) + Stop hook (done-check) | Автоматический check после action. |
| Модель не следует процедуре | Rigid local skill | Порядок шагов как контракт. |
| Модель делает generic вместо specific | Flexible local skill + reference examples | Рамка + канон. |
| Опасная batch-операция | Subagent isolation (worktree) | Изолированный blast radius. |
| Tool доступ в проекте где не нужен | Project-scope MCP | Precise grant. |

## Референтный паттерн: многослойная защита

Для критичного failure mode — комбинация:

1. **PreToolUse hook** блокирует действие.
2. **Permission rule** даёт бэкап (если hook fail'ит).
3. **Rigid skill** учит правильный путь.
4. **AGENTS.md** даёт context почему это важно.
5. **criteria-generator** ловит task-level bypass.

Это defense in depth. Prescription, опирающаяся только на AGENTS.md, — самая слабая. Prescription, опирающаяся только на hook, — жёсткая, но без объяснения пользователю. Комбинация — надёжная.
