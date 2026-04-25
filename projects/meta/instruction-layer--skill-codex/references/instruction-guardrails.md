# Codex Guardrails — каталог механизмов

Открывай этот файл только когда prescription требует конкретный Codex-specific механизм (hook or validator where the runtime supports it, tool permission / approval policy, Codex subagent, MCP, skill). Для generic AI system thinking — `system-building-principles.md`.

Порядок предпочтения при проектировании защиты: **runtime (hook or validator where the runtime supports its or validators where the runtime supports them/tool tool permission / approval policys / approval policy) → local skill → instruction text → task-contract handoff → human checkpoint**. Prompt-level правила — последнее средство, не первое.

## Skills — rigid vs flexible

Skills в плагинах (Codex skill folder или local) — повторяемые workflows с triggers.

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
| Модель пишет не туда | PreToolUse hook or validator where the runtime supports it | Structural block на file write path. |
| Модель забывает читать PROJECT-PLAN | fresh-session instruction load + user prompt handling hook or validator where the runtime supports its or validators where the runtime supports them | Context injection до reasoning. |
| Модель запускает опасную команду | Bash tool permission / approval policy deny + PreToolUse safeguard | Два слоя защиты. |
| Модель не проверяет свою работу | PostToolUse hook or validator where the runtime supports it (validator) + Stop hook or validator where the runtime supports it (done-check) | Автоматический check после action. |
| Модель не следует процедуре | Rigid local skill | Порядок шагов как контракт. |
| Модель делает generic вместо specific | Flexible local skill + reference examples | Рамка + канон. |
| Опасная batch-операция | Subagent isolation (worktree) | Изолированный blast radius. |
| Tool доступ в проекте где не нужен | Project-scope MCP | Precise grant. |


## Референтный паттерн: многослойная защита

Для критичного failure mode — комбинация:

1. **PreToolUse hook or validator where the runtime supports it** блокирует действие.
2. **Permission rule** даёт бэкап (если hook or validator where the runtime supports it fail'ит).
3. **Rigid skill** учит правильный путь.
4. **AGENTS.md** даёт context почему это важно.
5. **task-contract** ловит task-level bypass.

Это defense in depth. Prescription, опирающаяся только на AGENTS.md, — самая слабая. Prescription, опирающаяся только на hook or validator where the runtime supports it, — жёсткая, но без объяснения пользователю. Комбинация — надёжная.
