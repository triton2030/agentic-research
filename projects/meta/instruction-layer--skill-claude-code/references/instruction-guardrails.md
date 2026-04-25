# Claude Code Guardrails — каталог механизмов

Открывай этот файл только когда prescription требует конкретный Claude Code-specific механизм (hook, permission, subagent, MCP, skill). Для generic AI system thinking — `system-building-principles.md`.

Порядок предпочтения при проектировании защиты: **runtime (hooks/permissions) → local skill → instruction text → task-contract handoff → human checkpoint**. Prompt-level правила — последнее средство, не первое.

## Skills — rigid vs flexible

Skills в плагинах (marketplace или local) — повторяемые workflows с triggers.

### Rigid skill

Следует точно, без адаптации. Каждый шаг обязателен.

Когда использовать: когда дисциплина и порядок сами создают ценность.
Примеры: `project-strategy` (thinking workflow для durable bet), `task-contract` (task-level контракт), TDD, security review.

### Flexible skill

Задаёт рамку и сильные defaults, но адаптируется к контексту. Какие шаги применять — зависит от задачи.

Когда использовать: когда variance в задачах высокая, но общая рамка помогает.
Примеры: `instruction-layer` (audit + design), frontend-design, research audit.

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
5. **task-contract** ловит task-level bypass.

Это defense in depth. Prescription, опирающаяся только на AGENTS.md, — самая слабая. Prescription, опирающаяся только на hook, — жёсткая, но без объяснения пользователю. Комбинация — надёжная.
