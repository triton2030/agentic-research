# TODO — остаточные задачи по main-strategy rollout

Claude Code версия скила (проект + глобал) на актуальной goal-driven редакции. Дальше — догнать остальное.

## 1. Sync codex-варианта

Claude-code ушёл вперёд. Надо подтянуть codex-вариант к той же редакции:

- `projects/meta/main-strategy--skill-codex/references/file-contracts.md` → переписать в goal-driven формат (три файла × Цель / Как цель регулирует форму / Работает / Дрейфует), добавить `Applies to:` в схему записи `learnings.md`.
- `projects/meta/main-strategy--skill-codex/SKILL.md` → Hard Block: требовать цитаты **обеих** сторон конфликта (существующая строка + новый запрос). Без обеих — симуляция.

## 2. Зачистка стр. ссылок на старые файлы

Grep по `NORTH-STAR|CURRENT-STRATEGY|RATIONALE` ещё находит в:

- `AGENTS.md`
- `knowledge/research/meta/inventory-codex.md`

Обновить на `INTERVIEW.md` / `PROJECT-PLAN.md` / `learnings.md` где уместно.

## 3. `_ops/` port-then-delete

- Извлечь `Goal` из `_ops/1-NORTH-STAR.md` → новый `_ops/PROJECT-PLAN.md` (Goal).
- Strategic lines + anti-goals из `_ops/3-CURRENT-STRATEGY.md` → начальные `Stages` в `PROJECT-PLAN.md`.
- Handoffs "Для Criteria Generator" из текущих файлов → seed-предпочтения в `_ops/INTERVIEW.md` (как authoring-профиль владельца репо).
- Удалить `_ops/1-NORTH-STAR.md`, `_ops/2-RATIONALE.md`, `_ops/3-CURRENT-STRATEGY.md`.
- Переписать `_ops/learnings.md` под формат `Expected / Actual / Delta / Applies to:` (обязательное новое поле).

## 4. Установить downstream-скилы в marketplace

Свежие версии в `projects/meta/` ушли вперёд относительно установленных:

- `cp -R projects/meta/criteria-generator--skill-claude-code/{SKILL.md,references,README.md}` → `~/.claude/marketplaces/my-skills/skills/criteria-generator/`
- `cp -R projects/meta/system-architect--skill-claude-code/{SKILL.md,references,README.md}` → `~/.claude/marketplaces/my-skills/skills/system-architect/`

Проверить существование целевых каталогов перед cp. Убедиться, что grep внутри них после копирования чист.

## 5. Verification pass

- `grep -rn "NORTH-STAR\|CURRENT-STRATEGY\|RATIONALE" projects/ ~/.claude/marketplaces/my-skills/skills/ _ops/ AGENTS.md CLAUDE.md knowledge/` → ноль.
- Свежий чат в repo: "хочу добавить новый скилл" → main-strategy gate срабатывает, заводит INTERVIEW.md и PROJECT-PLAN.md.
- Свежий чат вне этого repo: никакого spam-reminder про interview-файл.
- `criteria-generator` в новом чате → `Anchored in:` ссылается на PROJECT-PLAN/INTERVIEW.
- `system-architect` в новом чате → не падает из-за отсутствующих RATIONALE-секций.
- Hard Block: воспроизвести противоречие в тесте — убедиться, что скил цитирует обе стороны.
- learnings.md: записи без `Applies to:` не добавляются.

## Вне скоупа этого rollout'а

- Hooks (`UserPromptSubmit`, `SessionStart`) — решили не делать глобально. Если после verification обнаружим misfire, добавить repo-scoped в `agentic-research/.claude/settings.json`.
