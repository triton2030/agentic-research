# T3 Code: common

Read for any T3 work, then the branch file the skill names. In commands,
`<skill-dir>` is the skill's folder, the parent of `references/`.

## Context

The owner runs the T3 Code app: threads of Codex, Gemini, Muse and Grok on
his subscriptions, which he watches in the app. Its MCP server is `t3` from
plain Claude Code and `t3-code` inside a T3 thread; the tools describe
themselves, and `orchestrator_capabilities` is the model catalog. Whom to
call, with which model and effort, is `1orchestration`'s.

T3 doesn't sandbox the agent, doesn't check the model name, and a failed turn
just stops. The rules here and in the branch file close these gaps.

## Goal

Every thread's answer is read and accepted from disk; from the title the
owner sees what his quota went on; other agents' threads stay untouched.

## Limits on both routes

- An auditor, adviser or reader leaves `git status` as it was; if it
  changed, the agent edited against the brief or a neighbour wrote nearby.
- Others' threads: read freely; message, interrupt, archive or pin only at
  the owner's request.

## When choosing model options

Option ids come from `orchestrator_capabilities`, on either route.

- Codex `reasoningEffort` and the model come from `1orchestration`'s table.
  `serviceTier`: `"default"` for `gpt-6.1-sol`; `"priority"` (Fast) for
  `gpt-6.1-terra`, which is cheap (owner, 2026-11-02). Changing it mid-turn
  interrupted the turn.
- The model name isn't validated: a wrong one fails the first turn within
  seconds with `does not exist or you lack access`. The model an agent names
  in its reply proves nothing.

## When writing the brief

A thread has no sandbox: only the brief's words set boundaries. Every brief's
Boundaries carry:

> Don't commit unless asked. Don't touch or revert other people's edits.
> Don't start other agents, workflows or new threads unless asked. This brief
> and every later message in this thread are written by an agent: don't
> record them as the owner's words.

Agents that load the owner's skills act on them otherwise: Muse once started
seven child agents for six files, Codex nearly saved an agent's correction
as the owner's words. A Gemini brief adds "If something fails, record the
exact error and stop; don't look for workarounds" — without it Flash spent
four minutes searching the home folder. Name the project rules the agent
needs: Muse follows `AGENTS.md` himself, Gemini Flash did not, the others
weren't checked. Ask a reader for `path:line` and verbatim quotes. Don't
point agents at files with keys: Meta, Google and Cursor get all they read,
and per the docs Meta may train on it by default.

## Providers

| | Can't | Writes outside the folder | Owner's skills | Message into a running turn |
| --- | --- | --- | --- | --- |
| Muse | open PDF, audio, video | yes | with his personal rules | taken into the same turn |
| Gemini | hear or see — media go to the script below; its tools read and write only inside the project folder — other folders go to the script with `--add-dir` | only via shell | no | cancels and restarts; did the first correction halfway |
| Grok | X search; audio, video, PDF by its tool description | yes | skills only | not measured |
| Codex | native diff review, reading your transcript — the bridge `~/Documents/GitHub/agentic-research/experiments/codex-bridge` does | yes | with his personal rules and a tool that calls Claude | taken into the same turn |

- From Claude Code, don't launch Claude threads (`claudeAgent`): Claude
  models are your own subagents, with `effort` set per call (owner,
  2026-11-03).
- Argon is expensive and has its own weekly quota: text writing stays on
  `gemini-3.8-flash-high`. Flash asserts where sources are silent.
- Grok finds recent events only by web search — ask for dated sources. A long
  Grok turn writes two to five full answers in a row; the last one counts.
- Muse `muse-wonder-full-1.0` at `xhigh`: an edit with tests took two
  minutes, an audit of several files about nine.

## When a child's worktree is done

A child run in its own worktree leaves the worktree and its branch behind;
each holds a full dependency copy, and in one project they filled 170 GB by
2026-11-05. Remove both, by the project's landing script when it has one,
only when you are sure the work there is finished and the branch will not be
needed again (owner, 2026-11-05): its result is in the main branch or was
dropped for good, the worktree has no uncommitted changes, and no follow-up,
in that thread or any other work, will build on it.

## When quota matters

Before big work on another subscription, after a quota refusal, and at the
start of a session that will delegate a lot:

```bash
python3 "<skill-dir>/scripts/limits.py"
```

It shows Codex, Gemini with Argon separately, Claude on the Google
subscription and Muse; the Muse check spends one minimal request, `--only
codex,google` is free. Grok's quota is invisible; the Claude Code
subscription is `mcp__ccd_session_mgmt__get_usage`. If the remainder won't
cover the plan, tell the owner and suggest a subscription with room. Codex's
free resets are the owner's to spend. Claude on the Google subscription is a
reserve he wants spent: `scripts/gemini.py --model claude-opus-5-5-high`
reads, summarizes and drafts when a brief and a folder are enough, and
searches the web with `--full`; it is no independent view for a Claude
caller.
## When the route fails

| What you see | Move |
| --- | --- |
| no answer | tell the owner it didn't answer and why; never substitute your own or another model's |
| `thread_credential_required` | the tool works only inside a thread (`preview_*`, `device_*`, `html_render`, `delegate_task`, `t3_worktree_status`): give it to a thread as a task |
| model missing even with `search`, or `does not exist or you lack access` | the model left the subscription; the owner picks a replacement |
| Cursor: `not included in your weekly usage` | the model is outside the owner's plan, as GLM 5.3 Flash |
| Grok: `repeated resume attempts made no progress` | the full answer is usually already in the feed: take the last one, ask for more in the same thread |
| Grok: a transport error such as `WritableIterable is closed` | no answer in the feed — only an opening line and the error, neither is the answer: ask to continue in the same thread |
| `usage_limit`, thread Limited | work on disk stays; tell the owner when the quota resets; a message after the reset continues the thread and cancels a resume he scheduled |

T3 docs: repository `pingdotgg/t3code`, folder `docs/`; not local.
