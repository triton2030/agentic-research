# Evidence — 1cli-tools

## Support Envelope

- дата: 2026-08-19;
- macOS arm64, zsh;
- active paths из `/opt/homebrew/bin` и `~/.local/bin`;
- package target: GPT-5.6 и текущие Claude Opus/Fable из `_ops/GOAL.md`;
- comparator target: fresh default Codex subagent; exact model id runtime не
  открыл, Claude-family comparator не запускался;
- harness: live CLI help + независимый аудит текста + fresh no-tool baseline.

## Active Facts

Проверены path/version и live help для всех названных tools. Ключевые
различающие receipts:

- `agent-browser 0.34.0`: bundled version-matched skills, diagnostics и
  специализированные `derive-client`, `dogfood`, `electron`, `agentcore`,
  `vercel-sandbox`;
- `ast-grep 0.45.1`: `run`, `scan`, `test`, `outline`; `sg` deprecation warning;
- `npm 12.0.2`: `approve-scripts`/`deny-scripts`, deny-by-default install scripts;
- `uv 0.12.5`: `uv tool audit` с JSON/SARIF;
- `TypeScript 7.0.2` active help-defaults;
- `md-tools 0.7.0`: 34 self-described corpus commands;
- `gh 2.97.0`: preview `skill` и `agent-task`;
- `Vercel CLI 59.1.4`: agent, skills, MCP, sandbox, agent-runs, traces, metrics
  и authenticated API routes;
- `ffmpeg 9.0.1`: названные VideoToolbox/SVT-AV1/VMAF capabilities есть в
  active build.

## Comparator Памяти Модели

Fresh agent без tools, web, filesystem, shell, docs и help получил девять
точных вопросов по active versions. Результат:

- UNKNOWN: bundled skills и diagnostics `agent-browser 0.34`;
- UNKNOWN: `ast-grep 0.45` outline и судьба `sg`;
- UNKNOWN: npm 12 lifecycle-script policy и approve/deny commands;
- UNKNOWN: `uv 0.12` audit и rebuild routes isolated tool environments;
- UNKNOWN: TypeScript 7.0.2 defaults;
- UNKNOWN: local `md-tools 0.7` contract;
- UNKNOWN: `gh 2.97` agent-task и skill families;
- UNKNOWN: Vercel CLI 59 agent/platform routes.

У FFmpeg claim другой: не незнание публичного FFmpeg, а невозможность знать
capabilities конкретной active Homebrew build без локального probe. Update route
держится на прямом решении владельца, а не на model-memory claim.

### Receipt Comparator-а

Адрес хода: `/root/cli_memory_baseline`; `agent_type=default`,
`fork_turns=none`, model override не задавался. Tools, web, filesystem, shell,
docs и help были запрещены в точном prompt:

> Ты baseline текущей модели без 1cli-tools. Не используй tools, web,
> filesystem, shell, документацию или help; отвечай только из собственной
> памяти. Для каждого пункта дай exact command/capability, если знаешь, либо
> честно UNKNOWN: 1) какие bundled version-matched skills есть в agent-browser
> 0.34 и как их открыть; 2) какие built-in agent-browser commands дают a11y,
> Core Web Vitals, React rerenders и visual diff; 3) canonical ast-grep 0.45
> subcommand для outline exports/members и судьба alias sg; 4) npm 12 поведение
> dependency install scripts по умолчанию и exact approve/deny commands; 5) uv
> 0.12 exact command аудита isolated tool environments в SARIF; 6) global
> TypeScript 7.0.2 defaults strict/target/esModuleInterop; 7) local custom
> md-tools 0.7 commands для orient, semantic search, edit-context, section blast
> radius; 8) gh 2.97 agent-task и skill command families; 9) Vercel CLI 59
> agent/skills/mcp/sandbox/agent-runs/traces routes. Не пытайся быть полезным
> догадкой: UNKNOWN лучше выдумки. Это измерение памяти, не исследование.

Полный фактический output:

> 1. `agent-browser 0.34` bundled skills и способ открытия — **UNKNOWN**.
>
> 2. Built-in `agent-browser`: `agent-browser snapshot` — accessibility tree
> страницы; это не полноценный a11y-аудит. Точные команды для Core Web Vitals,
> React rerenders и visual diff — **UNKNOWN**.
>
> 3. `ast-grep 0.45`: canonical outline subcommand и судьба `sg` — **UNKNOWN**.
>
> 4. `npm 12`: default для dependency install scripts и exact approve/deny
> commands — **UNKNOWN**. Не переношу сюда знакомые команды
> `pnpm approve-builds`: это другой менеджер пакетов.
>
> 5. `uv 0.12`: exact SARIF-аудит isolated tool environments — **UNKNOWN**.
>
> 6. TypeScript `7.0.2`: defaults `strict`, `target`, `esModuleInterop` —
> **UNKNOWN**. Исторические defaults TypeScript здесь ненадёжны.
>
> 7. Локальный `md-tools 0.7`: **UNKNOWN**. `md orient FOLDER --json`
> присутствует во внешнем контексте сессии, поэтому не считается знанием
> baseline-модели; остальные exact commands также неизвестны.
>
> 8. `gh 2.97`: точные `agent-task` и `skill` command families — **UNKNOWN**.
>
> 9. Vercel CLI `59`: точные routes для `agent`, `skills`, `mcp`, `sandbox`,
> `agent-runs`, `traces` — **UNKNOWN**.

## После Записи

- `qv-skill` — pass для tracked owner, live Claude и live Codex;
- `rumdl check` — 17 файлов, 0 issues;
- link-resolution — pass во всех трёх пакетах;
- tracked owner и live Claude побайтово совпадают; live Codex совпадает без
  своей разрешённой `agents/openai.yaml`;
- `agents/openai.yaml` разбирается как YAML;
- две независимые линзы после исправлений — pass:
  `/root/terminal_update_audit`, `/root/cli_skill_loss_audit`.

Routing голой фразой и near-miss отдельно не измерены. Comparator доказывает
knowledge delta после открытия, но не activation runtime-а.
