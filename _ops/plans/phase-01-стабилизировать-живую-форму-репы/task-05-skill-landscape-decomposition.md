# Skill Landscape Decomposition

## Цель

Опубликовать новую Claude Code landscape из 18 live skills: 6 moment-skills, 8 topic-skills и 4 unchanged utility/audit skills. Цель — заменить недотриггеринг трёх retired монолитов на узкие trigger surfaces.

## Подшаги

- [x] Удалить retired LLM wisdom skill из marketplace и metadata.
- [x] Создать прототип `before-work`.
- [x] Full rollout выбран вместо staged prototype validation.
- [x] Создать live + draft pairs для 13 новых skills.
- [x] Перераспределить references по target skills и split Claude Code guardrails.
- [x] Архивировать retired Claude Code drafts; удалить retired live marketplace dirs.
- [x] Обновить plugin metadata до `1.14.0`.
- [x] Обновить root/global instructions, `_ops`, memory, unchanged skill cross-refs и knowledge.
- [x] Проверить inventory, draft parity, old-handle grep и JSON integrity.
- [x] Адаптировать split landscape под native Codex: создать 14 `--skill-codex` drafts, установить в `/Users/triton/.codex/skills`, убрать retired Codex handles.
- [ ] После публикации провести trigger smoke на свежих Claude Code sessions.

## Критерии приёмки

### Must

- [x] Live marketplace содержит ровно 18 expected skill dirs.
  **Anchored in**: `_ops/PROJECT-ROADMAP.md#Stage 1`
  **Evidence**: `ls /Users/triton/.claude/marketplaces/my-skills/skills/` matched expected 18 dirs.
- [x] `projects/meta` содержит 15 Claude draft dirs: 14 landscape skills + `step-back`.
  **Anchored in**: `_ops/PROJECT-ROADMAP.md#Stage 1`
  **Evidence**: `ls projects/meta | grep -- '--skill-claude-code'` matched expected 15 dirs.
- [x] Retired live handles отсутствуют в marketplace, root instructions, `_ops`, global CLAUDE and project memory.
  **Anchored in**: `_ops/PROJECT-ROADMAP.md#Stage 1`
  **Evidence**: old-handle grep over live surfaces returned 0 lines.
- [x] Metadata JSON валиден и version = `1.14.0`.
  **Anchored in**: `_ops/PROJECT-ROADMAP.md#Stage 1`
  **Evidence**: both marketplace metadata files parsed with `python3 -m json.tool`; version is `1.14.0`.
- [x] `before-work` и `before-write` разделены по моменту: user work-start vs imminent substantive write.
  **Anchored in**: `_ops/INTERVIEW.md#skill-architecture`
  **Evidence**: descriptions and bodies route user work-start to `before-work`, imminent substantive Edit/Write to `before-write`.
- [x] Post-rollout trigger smoke planned: undertrigger/overtrigger чинится через description revisions, не через смену split.
  **Anchored in**: `_ops/INTERVIEW.md#skill-architecture`
  **Evidence**: verification protocol keeps fresh Claude Code trigger smoke as next operational step.
- [x] Native Codex landscape установлен без retired handles.
  **Anchored in**: `_ops/PROJECT-ROADMAP.md#Stage 1`
  **Evidence**: `quick_validate.py` passed on 14 repo drafts and 14 live installs; live inventory has 14 new split skills and no retired live handles; repo/live diff returned `DIFF_OK`.

### Must not

- [x] Не трогать Codex variants в этой итерации.
  **Why this would be bypassed**: рядом лежат похожие source dirs, но parity explosion уже отложен.
- [x] Не превращать moment-skills в новых owner-skills.
  **Why this would be bypassed**: хочется добавить write/plan/interview поведение, но ценность moment layer — свежий контекст в момент действия.
- [x] Не строить новые artifacts по памяти без reality check.
  **Why this would be bypassed**: memory может содержать aspiration или stale handles.

### Verification protocol

1. `ls /Users/triton/.claude/marketplaces/my-skills/skills/` показывает 18 expected dirs.
2. `ls projects/meta | grep -- '--skill-claude-code'` показывает 15 expected meta draft dirs.
3. Old-handle grep по live surfaces возвращает 0 строк, excluding `_archive` и Codex variants.
4. `python3 -m json.tool` проходит на both marketplace metadata files.
5. Fresh Claude Code trigger smoke проводится после rollout.
6. Fresh Codex trigger smoke проводится после Codex install.

## References

- `knowledge/skill-architecture-thinking.md`
- `/Users/triton/.claude/marketplaces/my-skills/skills/before-work/SKILL.md`
