# Task — Knowledge frontmatter descriptions cleanup

**Status**: Active, not started
**Created**: 2026-05-21 (surfaced during md-tools refactor audit)
**Owner skill**: `1planning` (task content), `1user-truth` или manual user pass (description authoring)

Применимые инструкции: `AGENTS.md` (project root), `CLAUDE.md` (project root), `_ops/AGENTS.md`.

## Цель

27 из 37 файлов в `knowledge/` не имеют `description` в frontmatter. Это блокирует `md_search --scope descriptions` (file-level orientation) и понижает quality `md_orient` output. Каждый файл должен иметь однострочное `description` — что в нём, для cold-start agent.

## In scope

Добавить frontmatter `description` (1 строка) к 27 файлам:

```
examples/README.md
examples/anthropic-design-generator/CLAUDE.md
examples/anthropic-design-generator/ds/README.md
examples/anthropic-design-generator/takeaways.md
guides/design-review-playbook.md
guides/perfect-context-engineering.md
guides/perfect-project-shape.md
guides/perfect-system-prompts.md
guides/progressive-task-planning-playbook.md
guides/structural-critique-playbook.md
practical-guides/hooks-runtime-guardrails.md
research/business/inventory.md
research/design/inventory.md
research/design/learnings.md
research/dev/code-aware-tooling-2026-q2.md
research/dev/inventory.md
research/dev/learnings.md
research/meta/inventory.md
research/meta/learnings.md
research/meta/links.md
wisdom-claude-code.md
wisdom-claude-opus-4.7.md
wisdom-codex.md
wisdom-gpt-5.5.md
wisdom-llm.md
wisdom-skills-plugins.md
wisdom-systems-thinking.md
```

## NOT in scope

- Полный rewrite content файлов (только frontmatter)
- Добавление graph fields `read-before-edit` / `edit-after-edit` (отдельная задача)
- Корпус-аудит на duplicate content (это `md_audit` job, отдельно)

## Definition of done

- Каждый из 27 файлов имеет frontmatter с `description: "..."` (1 строка, ≤120 chars)
- Description honest (не fluff): что файл owns, не «about X» — конкретный outcome или claim
- `md_orient knowledge` показывает `description_gap_count: 0`
- `md_search --scope descriptions knowledge "X"` возвращает meaningful results

## Stop rules

- Если файл по essence не нужен (orphan, outdated), вместо добавления description — пометить для archive

## Подшаги

1. Прочитать каждый файл (через `md_cat` или Read)
2. Sсформулировать одну строку description, captures owner-truth (что file *defines* или *contains*)
3. Добавить YAML frontmatter в начало:
   ```yaml
   ---
   description: "Одна строка о том что owns этот файл"
   ---
   ```
   Если файл уже имеет frontmatter — добавить ключ `description`
4. После batch (5-10 файлов) — re-index:
   ```bash
   md_navigator.py index /path/to/knowledge
   ```
5. Verify: `md_orient knowledge` → `description_gap_count` уменьшается

## Verification

- `md_orient knowledge` → `description_gap_count: 0`
- Sample 3 random descriptions — captures essence, не generic
- Re-run `md_audit knowledge` — no `discovery_gaps` class findings

## Anchors / Evidence

- Surfaced during md-tools refactor audit 2026-05-21
- Related: `_ops/plans/md-tools-refactor/task-001-md-tools-unified-backend.md`
- Tool ready: `md_orient` shows `description_gap_count` baseline
