# Code locality hook — 2026-05-22

## Факты

- Installed Claude `PreToolUse` hook:
  `/Users/triton/.claude/hooks/pre-tool-skill-code-locality.py`.
- Wired in `/Users/triton/.claude/settings.json` for
  `Bash|Write|Edit|MultiEdit|NotebookEdit`.
- The hook denies new writes under `~/.claude/skills/**` and
  `~/.codex/skills/**` when the target is outside the declarative whitelist:
  `SKILL.md`, `references/*.md`, `agents/openai.yaml`, `assets/*`.
- Existing non-md helper scripts such as `1cli-tools/scripts/probe-tools.sh`
  were not removed; task-305 explicitly scopes existing non-md scripts out.

## Источник

- `_ops/plans/md-mcp-to-cli-refactor/_archive/2026-05-22-402-instruction-and-docs-update/task.md`
- `knowledge/practical-guides/hooks-runtime-guardrails.md`
- Official Claude hooks reference checked on 2026-05-22.

## Проверка

- `python3 -m py_compile /Users/triton/.claude/hooks/pre-tool-skill-code-locality.py`
  → ok.
- `python3 -m json.tool /Users/triton/.claude/settings.json` → ok.
- Simulated `Write` to `~/.claude/skills/1md-navigator/scripts/new.py` →
  `permissionDecision: deny`.
- Simulated `Write` to
  `~/.claude/skills/1md-navigator/references/tool-catalog.md` → allow.
- Simulated Bash `tee ~/.codex/skills/1md-graph/scripts/new.sh` →
  `permissionDecision: deny`.

## Почему Актуально

This closes task-402's proactive guardrail without breaking existing
non-md helper scripts that are outside this refactor's executable-code move.

## Что Снимет Находку

Archive after the md-mcp-to-cli refactor is committed and pushed with the hook
documented in closeout evidence.
