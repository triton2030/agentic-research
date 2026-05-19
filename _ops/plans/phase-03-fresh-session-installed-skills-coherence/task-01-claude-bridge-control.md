# Task 01 — Claude Bridge Control

## Цель

Выбрать и прототипировать управляемый глобальный мост Codex -> Claude Code,
чтобы Claude можно было часто вызывать из Codex с контролем режима, памяти,
скилов, системных инструкций, потока вывода и evidence чтения контекста.

## Применимые критерии

- [_ops/criteria/external-agent-control.md](../../criteria/external-agent-control.md)
- [_ops/criteria/repo-structure-and-runtime-guards.md](../../criteria/repo-structure-and-runtime-guards.md)
- [_ops/criteria/skill-authoring.md](../../criteria/skill-authoring.md)

## Подшаги

1. Проверить готовые основы.
   EN: Evaluate existing official and community bases before building anything custom: `claude mcp serve`, `ai-cli-mcp`, `claude-code-mcp`, and any stronger current candidate found during research.

2. Выбрать форму моста.
   EN: Decide whether the first version should be CLI wrapper, MCP server, fork of an existing project, or a thin local runner with later MCP exposure.

3. Описать профили запуска.
   EN: Define the minimal Claude run profiles for clean mode, no-skills mode, read-only review, streaming observation, skill-audit, and normal delegated execution.

4. Сделать ручной прототип.
   EN: Run one manual prototype with streaming output, controlled flags, and saved logs before creating durable scripts, skills, or global configuration.

5. Проверить чтение скилов.
   EN: Create a smoke test that proves whether Claude actually read the intended skill/context, using logs or observable output rather than self-report alone.

## Критерии приёмки

- Готовая основа выбрана или отклонена с коротким evidence по поддержке, возможностям и рискам.
- Есть минимальный набор профилей запуска Claude под разные ситуации.
- Долгий запуск можно наблюдать по ходу работы и остановить, если Claude зациклился или понял задачу неверно.
- Проверка Claude-скилов включает evidence того, что нужный скилл или контекст был реально прочитан.
- Глобальная установка, MCP-регистрация или правка live Claude/Codex surfaces не выполняется до ручного прототипа.

## Must-not

- Не строить свой мост с нуля до проверки существующих решений.
- Не путать `--dangerously-skip-permissions` с настоящей sandbox-защитой; в v1
  это осознанный пользовательский tradeoff, а не безопасность.
- Не считать финальный ответ Claude доказательством, что он прочитал нужный скилл.

## Closeout evidence

- Built repo-contained bridge under `experiments/claude-bridge` with Node runner,
  MCP stdio server, profiles, ignored local `runs/`, fake-Claude smoke fixture,
  and repo-local Codex skill source.
- Hardened run state: every run writes `state.json`; `peek/result` reconstruct
  from files after restart; orphan state and post-restart `kill` use conservative
  PID plus `debug.log`/run-dir fingerprint checks.
- Removed v1 agent/subagent surface from runner, CLI, MCP tools, profiles,
  README, and `claude-mcp` skill; smoke asserts those tools stay absent.
- Added normalized `milestones`, cleaner `final_output_summary`, strict
  `claude_audit_skill` evidence, and `claude_cleanup_runs` / CLI `cleanup`
  with 14-day dry-run default and `--confirm` deletion.
- Added chat relay support: `wait/result` return `chat_relay.text` /
  `chat_relay.markdown`; `peek` accepts `cursor` and returns `next_cursor`,
  `relay_updates`, and incremental `chat_relay.text` for Codex chat updates.
- Registered global Codex MCP `claude-mcp` pointing to
  `node /Users/triton/Documents/GitHub/agentic-research/experiments/claude-bridge/src/server.js`.
- Synced repo-local and installed `/Users/triton/.codex/skills/claude-mcp`;
  both pass `quick_validate.py`, warn that prompt/debug/stdout logs may contain
  secrets, and instruct Codex to relay Claude answers from `chat_relay.text`
  instead of raw JSON.
- Verified `npm run smoke`, `npm run doctor`, `codex mcp get claude-mcp`,
  `codex mcp list`, both skill validations, and real MCP `claude_result` for
  run `2026-04-30T16-27-55-520Z-2cd0fea6`: `BRIDGE_REAL_OK`, completed, no
  warnings.
- Verified existing real run through MCP after relay change:
  `claude_result.chat_relay.text = BRIDGE_REAL_OK`,
  `claude_peek.next_cursor = 17`, and peek relay includes `BRIDGE_REAL_OK`.
