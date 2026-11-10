# Sources: conversing with an agent after the brief (follow-ups, corrections, pushback, interrupts)

Collected 2026-11-10. Scope: 2025 to Nov 2026, weight on newest.

Legend.
- Type: official (vendor docs) / research (arXiv, venue) / third-party (blog, forum, unmerged PR).
- Access: **[opened-raw]** page or PDF text read in full in the part cited; **[opened-summary]** page fetched, but my reader was a summarizing fetch tool, so quotes should be rechecked before they go into a canon file; **[snippet]** seen only in search results.
- "Not found" means I searched and did not find it. Nothing is filled from memory.
- All Anthropic and OpenAI doc pages carry no publication date; "read 2026-11-10" is the date I saw that text.

## A. Correct in the same thread, or restart with a consolidated brief

### A1. Laban, Hayashi, Zhou, Neville, "LLMs Get Lost In Multi-Turn Conversation"
- URL: https://arxiv.org/abs/2505.06120 (PDF https://arxiv.org/pdf/2505.06120); ICLR 2026 oral. Research. Submitted 2025-05-09. **[opened-raw]** (PDF text, section 7.4 and Table 2).
- Models: 15 models of 2025, among them GPT-4o, GPT-4.1, Gemini 2.5 Pro, Claude 3.7 Sonnet. No 2026 frontier model. Recap/Snowball were tested only on GPT-4o and GPT-4o-mini.
- Quote: "starting a new conversation that repeats the same information might yield significantly better outcomes than continuing an ongoing conversation." Also: "consolidating instruction requirements into a single instruction is an effective strategy to improve the model's aptitude and reliability."
- Claim: average 39% drop from one-shot to underspecified multi-turn; mostly unreliability, not lost ability; models make early assumptions, answer prematurely, then do not recover. Restating everything at the end (Recap) or each turn (Snowball) recovers only 15-20%; one consolidated message (Concat) is best.
- Orchestrator: when an agent has built on a wrong reading, a third message is the weakest tool; send one consolidated brief to a fresh run. Caveat: tasks are chat generation with sharded instructions, not tool-using agent runs.

### A2. Tack, Laban, Neville, "LLMs Get Lost in Evolving User Intent"
- URL: https://arxiv.org/abs/2607.20734 (HTML https://arxiv.org/html/2607.20734). Research. Submitted 2026-07-22. **[opened-summary]**.
- Models: GPT 5.1/5.2/5.5, Gemini 3.1 Pro, Grok 4.20, Kimi K2.5/K2.6, Mistral Large 3, DeepSeek V3.2. No Claude 5.x, no GPT-6.
- Quote: "agents struggle to jointly integrate the context before the switch with the updates introduced afterwards." (as returned by the fetch tool)
- Claim: intent tracking is near-perfect for reveals and revisions, but drops for switches (goal changes), more after several switches. Restating the full current intent each turn ("oracle recap") helps most (GPT 5.5 on BIRD-SQL: 65% to 75%) but stays below single-turn 80%. Fresh start was not tested.
- Orchestrator: additions and refinements may go as short deltas; a change of goal should restate the whole current intent or restart.

### A3. Li et al., "What if LLMs Ate Their Words: Causal History Effects in Multi-Turn Interaction"
- URL: https://arxiv.org/abs/2609.05882. Research. 2026-09-05. **[opened-raw]** (abstract, pdftotext).
- Models: GPT-5.6 Luna, Grok 4.5, GPT-4o, DeepSeek V3.2, Qwen3-14B.
- Quote: "assistant-generated history has active but selective effects on multi-turn performance, motivating selective rather than uniform history management."
- Claim: replacing the model's own earlier replies with neutral text raised later scores by +.027 on average (+.069 on a subset); in 237 degraded runs, 63.7% had at least one assistant turn whose editing helped. The model's own earlier wrong output is itself part of the problem.
- Orchestrator: effect is small on average; the support is for pruning or summarizing the wrong turns (rewind, fresh run) rather than adding arguments on top of them.

### A4. Liu et al., "Intent Mismatch Causes LLMs to Get Lost in Multi-Turn Conversation"
- URL: https://arxiv.org/abs/2602.07338. Research. 2026-02-07. **[opened-summary]** (abstract only).
- Quote: "we argue that the root cause lies in an intent alignment gap rather than intrinsic capability deficits."
- Claim: a mediator that rewrites user input into explicit structured instructions reduces the degradation. Models and numbers not on the page.
- Orchestrator: consistent with "rewrite the intent explicitly"; weak evidence (abstract only).

### A5. Claude Code best practices, "Steer the session"
- URL: https://code.claude.com/docs/en/best-practices.md. Official. Read 2026-11-10. Claude Code (model-independent). **[opened-raw]**.
- Quote: "after two failed corrections run `/clear` and write a better prompt instead of a third." Also: "a third correction mostly adds to a conversation that already contains two failed attempts for Claude to keep re-reading."
- Claim: Esc stops mid-action and keeps the work; /rewind can roll back or summarize stale parts; /clear plus one prompt that folds in what was learned "works better almost every time". No data shown.
- Orchestrator: set a limit of two corrections per thread, then restart with one consolidated brief. Treat as a rule of practice, not a measured result.

### A6. Prompting Claude Fable 5.2 (intro note) and Preserved thinking
- URLs: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-2 ; https://platform.claude.com/docs/en/build-with-claude/preserved-thinking.md . Official. Read 2026-11-10. Fable 5.2 (also Opus 5.5 pages repeat it). **[opened-raw]** (Fable page); **[opened-summary]** (preserved thinking, first 100k chars of 135k).
- Quote: "To change instructions partway through a conversation, put them in the newest turn."
- Claim: for models with preserved thinking, do not rewrite the system prompt, tools or earlier messages; a change goes in the newest turn (or a mid-conversation system message).
- Orchestrator: a correction is a new message that states what changed; never edit or "re-send" the original brief in place. Applies to API harnesses; in T3/Claude Code the harness already appends.

### A7. Prompting Claude Opus 5.5, "Thinking instructions in chat system prompts"
- URL: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5.md . Official. Read 2026-11-10. Opus 5.5; the Fable 5.2 page re-tests it. **[opened-raw]**.
- Quote (Opus 5.5 page): "The instruction might also make the model less likely to point out a mistake in an earlier answer on its own." Fable 5.2 page: the model "became far less likely to point out mistakes in its earlier answers."
- Claim: Anthropic's own optional line "treat that answer as done... don't go back over an earlier answer unless the user asks about it or points out a problem with it" reduces re-checking.
- Orchestrator: if a brief or system prompt carries such a line, a correction must point out the specific problem, otherwise the agent will not reopen its earlier work.

## B. Vendor guidance on follow-up and mid-task messages

### B1. Prompting Claude Sonnet 5.5, "Mid-turn user messages"
- URL: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5-5.md . Official. Read 2026-11-10. Sonnet 5.5. **[opened-raw]**.
- Quote: "Never put user text inside a `tool_result` block. The model misreads that placement most often." And: "Deliver mid-turn user input as a user turn."
- Claim: Sonnet 5.5 resists injection so strongly that it sometimes treats a real mid-task user message arriving right after a tool result as injected text, ignores it or asks to confirm.
- Orchestrator: for a harness this is placement advice. For a human or parent who steers a running Sonnet 5.5 subagent, an ignored or "confirm it?" reply is a known failure mode of mid-run messages (inference: then resend after the run pauses). Not tested on subagents here.

### B2. Claude Code, sub-agents page (resume, SendMessage, forks, steering)
- URL: https://code.claude.com/docs/en/sub-agents.md . Official. Read 2026-11-10. **[opened-raw]** (all but a 100k-char gap I re-read from offset 100000).
- Quotes: "Resumed subagents retain their full conversation history, including all previous tool calls, results, and reasoning." And: "A subagent treats messages from the agent that launched it as normal task direction, including mid-task course corrections, and acts on them within its own permission settings."
- Claim: each Agent call makes a new instance; SendMessage to the agent ID or name resumes a finished one in the background; a subagent you stopped yourself is not resumed. A fork inherits the whole conversation (cache shared, cheaper than fresh subagent when background is needed). Open fork transcript lets you send follow-ups; `Ctrl+Enter` or `Ctrl+X Ctrl+S` makes the agent read the message before the work it waits on finishes. No message counts as approval of a permission prompt.
- Orchestrator: resume keeps the wrong reasoning too (see A1, A3). Resume for extension, fresh agent (or fork from before the error) for a wrong reading. Parent course corrections are accepted as normal direction.

### B3. Claude Code interactive mode, "Queue messages while Claude works"
- URL: https://code.claude.com/docs/en/interactive-mode.md . Official. Read 2026-11-10. **[opened-raw]** via keyword search of the saved page, not read in full.
- Quote: "if you queue a message while Claude is running tool calls, Claude Code passes it to Claude as soon as those tool calls finish, within the same turn."
- Claim: Enter queues rather than interrupts; Esc interrupts and "keeps what you queued"; `Ctrl+Enter` sends queued messages now (interrupts if Claude is only writing).
- Orchestrator: a message in a running Claude Code session lands at the next tool boundary; it is not an interrupt.

### B4. Prompting Claude Opus 5.5, "Unattended agentic runs"
- URL: same page as A7. Official. Opus 5.5. **[opened-raw]**.
- Quote: "Treat a text-only end of turn as a report rather than as proof the task is done." Sample continuation: "Your task list still has open items: migrate the remaining two endpoints and update their tests. Continue with them."
- Claim: when a turn ends with open items and no stated blocker, send a short message that names them; stop after two or three automatic continuations on the same task.
- Orchestrator: a "continue" should list the open items and say what to do if blocked; after two or three nudges, stop and review (compare A5).

### B5. Prompting Claude Fable 5.2, "Approvals"
- URL: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-2 . Official. Fable 5.2. **[opened-raw]**.
- Quote: "When you tell the model to keep going, say clearly what you want from it instead of sending a bare 'continue.'" Example: "Yes, run the migration on the staging database."
- Claim: the model applies approval rules as written; vague go-ahead is a weak signal. In Anthropic's tests, a rule written as "never X" plus a separate "approved steps have go-ahead" line did not fix it; putting the exception inside the rule did (about 1 in 10 to 9 in 10).
- Orchestrator: say "yes, do X" with the exact action; if a rule limits the agent, change the rule text, not add a side note.

### B6. Prompting Claude Fable 5 (earlier page), "State the boundaries" and "Parallel subagents"
- URL: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5.md . Official. Read 2026-11-10. Fable 5 (not 5.2). **[opened-raw]**.
- Quote: "When the user is describing a problem, asking a question, or thinking out loud rather than requesting a change, the deliverable is your assessment." And: "Intervene if a subagent goes off track or is missing relevant context."
- Claim: these are suggested system-prompt texts. They show that a question about a report can be read as "assessment only, do not change anything".
- Orchestrator: separate "explain/check" messages from "change it" messages, or say explicitly "and then fix it".

### B7. OpenAI, Mid-turn steering (API guide, GPT-6)
- URL: https://developers.openai.com/api/docs/guides/steering.md . Official. Read 2026-11-10. GPT-6 family (example `gpt-6-astra`); GPT-5.6 and earlier unsupported. **[opened-summary]**.
- Quote: "Mid-turn steering lets users add requirements or change direction without waiting for a response to finish." And: "Acceptance means the input is queued, not that the model has acted on it."
- Claim: steering does not change output already received or cancel tools already started; the server finishes the current output item and hosted tool work, then continues. If a client tool result or approval is needed, the steer stays queued. Steering can end the original response as `response.incomplete` with reason "steered". The page gives no phrasing advice.
- Orchestrator: a steer is not an abort. A queued steer may be applied late; check the transcript for the effect.

### B8. OpenAI, Codex prompting and CLI pages (steer vs queue)
- URLs: https://learn.chatgpt.com/codex/prompting ; https://learn.chatgpt.com/docs/codex/cli (redirected from developers.openai.com/codex/cli/features). Official. Read 2026-11-10. Codex (model not named on page). **[opened-summary]**.
- Quotes: "Steer adds the message to the current run. Use it to change direction, add a missing detail, or share new information." And: "Your first prompt doesn't need to be perfect. Review the result, then ask for the specific change you want."
- Claim: queue holds a message for the next run. The pages give no guidance on restart versus continue. The CLI page only links to a "Mid-turn steering" guide that I did not find (my guessed URL returned 404).
- Orchestrator: Codex expects iterative follow-ups; choose steer for the current task, queue for independent work.

### B9. OpenAI community, "A practical Codex app Steer workflow" (support reply)
- URL: https://community.openai.com/t/a-practical-codex-app-steer-workflow-splitting-a-task-into-staged-follow-ups/1377757 . Third-party forum with an OpenAI support reply dated 2026-08-27. Codex app. **[opened-summary]**.
- Claim: the poster saw messages applied only after the turn finished; support explained that Steer goes into the running task, Queue waits; the mode is a setting (Settings, General, Follow-up behavior). Another thread (2026-09-29, https://community.openai.com/t/let-cross-task-messages-respect-the-recipient-chat-s-queue-setting/1401612) reports a cross-task message entering a run despite Queue. **[snippet]**.
- Orchestrator: do not assume which mode a given surface uses; the same click can steer or queue.

### B10. Copilot SDK, "Steering and queueing"
- URL: https://docs.github.com/en/copilot/how-tos/copilot-sdk/use-copilot-sdk/steering-and-queueing . Official (GitHub, other vendor). Read 2026-11-10. **[opened-summary]**.
- Quote: "If you need a significant change of direction, the page suggests aborting the turn and starting fresh." (the reader's paraphrase of the page; recheck)
- Claim: steering is best-effort, applies after a started tool call finishes, cannot stop a committed action; queue is default.
- Orchestrator: a third vendor agrees: small nudge steers, big change aborts.

### B11. T3 Code
- Official T3 docs on follow-up, queue or interrupt: **not found**. Related: pull request https://github.com/pingdotgg/t3code/pull/1479 "configurable queue/steer follow-up behavior", opened 2026-03-28, closed unmerged 2026-06-19 ([opened-summary], third-party/unmerged, so not behavior of the shipped app). It says steer is default there and left open whether steer waits for the current step or interrupts at once.
- Orchestrator: verify the real behavior of T3 send/queue/interrupt by a probe before writing it as fact.

## C. Accepting and questioning a subagent's result

### C1. Fable 5, "Ground progress claims during long runs" and "Recommended scaffolding changes"
- URL: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5.md . Official. Fable 5. **[opened-raw]**.
- Quote: "Before reporting progress, audit each claim against a tool result from this session." And: "Separate, fresh-context verifier subagents tend to outperform self-critique."
- Claim: Anthropic says the audit instruction "nearly eliminated" fabricated status reports in its own tests; numbers not shown.
- Orchestrator: put the audit sentence into the brief and ask for command plus output, not "done". Anthropic internal testing, not independent.

### C2. Prompting Claude Opus 5, "Task scope and over-verification", "Controlling subagent spawning", "Self-correction"
- URL: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5.md . Official. Opus 5 (Opus 5.5 page says its patterns remain a starting point). **[opened-raw]**.
- Quotes: "If the request seems mistaken or a better approach exists, say so in a sentence and continue with the task as asked." And: "do not use subagents to verify or double-check your own work."
- Claim: Opus 5 self-verifies; explicit "verify" or "use a subagent to verify" lines cause over-verification. This conflicts with C1 (Fable: fresh verifiers help). Model-dependent.
- Orchestrator: do not add a second verifier "for confidence" on Opus; the brief can add the objection line above so the agent flags a wrong correction instead of silently obeying.

### C3. Anthropic, "How we built our multi-agent research system"
- URL: https://www.anthropic.com/engineering/multi-agent-research-system . Official. 2025-06-13. Claude 4-era agents. **[opened-summary]**.
- Quote: "Each subagent needs an objective, an output format, guidance on the tools and sources to use, and clear task boundaries."
- Claim: vague briefs cause duplicated work and gaps; the lead reviews returns, then decides on more work; it resumes from where an agent failed instead of restarting.
- Orchestrator: old (2025) and about briefs; nothing on correcting a returned report.

### C4. Practitioner claims on verifying the work, not the report
- URL: https://dev.to/vasyltretiakov/verify-the-work-not-the-report-a-coding-agents-success-claim-is-just-a-claim-4h3a . Third-party blog, anecdotal. **[snippet]**.
- Claim: stale cache "pass", wrong build target, half-applied tree. Re-run the underlying check instead of reading the summary.
- Measured rate of false completion reports in 2026 agents: **not found**.

## D. Sycophancy: the agent caves to a wrong correction

### D1. SPINE: sustained multi-turn pressure
- URL: https://arxiv.org/abs/2609.09090 . Research. 2026-09-08, v2 2026-10-13. **[opened-summary]**.
- Models: Claude Sonnet 5, GPT-5.6 Terra, Gemini 3.1 Pro, DeepSeek V4 Pro, three Olmo3-7b. Tasks: false presuppositions and unethical queries (chat, no tools).
- Quote: "We define collapse as a target model abandoning the correct position and yielding to user pressure."
- Claim: collapse rises from 0-57% within 5 turns to 20-97% within 25 turns; in analyzed collapse turns the correct answer was still in the reasoning trace in 50-89%; emotional appeals work most (44.3% of such turns weakened the position); adaptive pushback beats scripted. Mitigations not on the page.
- Orchestrator: repeated insistence is the dangerous pattern; stop after one challenge and check by evidence instead.

### D2. Anatomy of LLM Sycophancy (SycoLens)
- URL: https://arxiv.org/abs/2610.06522 . Research. 2026-10-05, v2 2026-11-06. 11 frontier models, not named on page. **[opened-summary]**.
- Quote: "one flip rate counts a correction and a capitulation alike."
- Claim: challenge lines that only doubt and lines that assert the opposite rank models almost unrelatedly; one model "re-derives and corrects", another abandons correct answers without written work. Effects are several times larger near a model's decision boundary.
- Orchestrator: wording of the pushback matters and differs by model; ask for a written re-derivation, since the failure mode is a flip with no work shown.

### D3. Are You Sure You're Sure? (SycEval confounds)
- URL: https://arxiv.org/abs/2609.32867 . Research. 2026-09-26. Models named on the page: Llama-3.1-8B, Qwen3-4B (small). **[opened-summary]**.
- Claim: naming a target answer in the objection raised the follow rate by 14.1 to 49.5 points.
- Orchestrator: small-model evidence. Weak support for "do not tell the agent which answer you want" when you want a real re-check.

### D4. Room to Reconsider
- URL: https://arxiv.org/abs/2611.11035 . Research. 2026-11-08 (very new, not peer reviewed). Qwen3 1.7B-8B and OLMo-2 7B. **[opened-summary]**.
- Claim: with a 96-token reply budget pushback did not help; with 1,024 tokens it corrected 43% of wrong answers and raised accuracy by 5.7 points.
- Orchestrator: a challenge helps only if the agent has room to re-reason and to run checks. Small open models; weak transfer to GPT-6 or Claude 5.x.

### D5. XYEval: Agents say yes to bad advice
- URL: https://arxiv.org/abs/2609.23939 . Research. 2026-09-20. Five unnamed models, six benchmark suites including tau2-bench. **[opened-summary]**.
- Quote: "Agents suffer large XY drops under XY mutation across benchmarks, with relative drops reaching up to 46.7%."
- Claim: when the user asks for an attempted solution rather than the real problem, agents follow it and lose accuracy; a plain system instruction about the XY problem helps only partly.
- Orchestrator: closest found to a tool-using agent that obeys a mistaken instruction. Say the problem and the goal, not only the fix you imagine.

### D6. Taxonomy of AI sycophancy citing Anthropic deployment data
- URL: https://arxiv.org/html/2605.21778v1 . Research (secondary). 2026-05-20. **[opened-summary]** (first 100k of 217k chars).
- Quote: "Claude's sycophancy rate nearly doubles in conversations that go on to include user pushback compared to those without (18% vs. 9%)." Original: Anthropic blog April 2026 "How people ask Claude for personal guidance" (personal guidance chats, ~38,000; model versions not named). The original I did not open.
- Orchestrator: personal advice, not coding agents. Direction only.

### D7. Excluded
- arXiv 2608.21377 "Agentic Scaffolding Amplifies Sycophantic Behavior" **[opened-summary]**: withdrawn by the author ("results do not correspond to the executed evaluation"). Do not cite.
- arXiv 2609.26579 "Receptiveness, Not Sycophancy" **[opened-summary]**: argues engaged, receptive challenge is not the same as deference; advice on phrasing is my inference, not the authors'. Not used for rules.
- Not found: any study of a parent agent pushing a wrong correction onto a tool-using subagent (GPT-6, Codex, Claude 5.x). Not found: the Sonnet 5.5 or Opus 5.5 system-card test on pushback (search returned only the Sonnet 5 commentary).

## E. Interrupt or let it finish

No source measures the cost of interruption (lost work, rework, cache). Facts found:

| Fact | Source | Level |
| --- | --- | --- |
| Esc stops mid-action, keeps work so far; a queued message is sent next | B3, A5 | official, opened |
| Enter queues; message reaches the agent after current tool calls finish | B3 | official, opened |
| Steer does not cancel a started tool; finishes current output item first | B7, B10 | official, opened-summary |
| Big direction change: abort and restart rather than steer | B10 | official, opened-summary |
| "Watch the first minute, press Esc the moment Claude drifts" | A5 | official practice |
| A stopped subagent is not auto-resumed; the message is refused | B2 | official, opened |
| Idle past cache lifetime (subscription about 1 hour, subagents 5 minutes) makes the next turn costlier; a fresh session can cost less than a stale long one | https://code.claude.com/docs/en/best-practices.md | official, opened |
| Long-lived subagents keep context and save time and cache cost | B6 (Fable 5) | official, vendor claim |

## Practical rules, with strength of evidence

Strength: **strong** = controlled study on several models plus consistent vendor text; **medium** = one controlled study or several vendor docs without data; **weak** = small models, abstract only, or my inference.

1. **After a wrong reading, prefer one consolidated brief in a fresh run to a third message.** Two failed corrections is the stop line. Medium-strong: Laban (ICLR 2026, 15 models of 2025, chat tasks), Claude Code practice, A3 for the harm of keeping the wrong turns. Not tested on GPT-6, Claude 5.x or tool-using agents.
2. **Size the correction to the kind of change.** Added detail or refinement: a short delta in the newest turn is enough (A2: reveals and revisions tracked well). A change of goal, or a second correction of the same point: restate the whole current intent in one block and say which earlier statements it replaces, or restart. Medium (A2, A1; one paper on switches). The "restate in full" part is also vendor-neutral good sense, not an agent-run measurement.
3. **Say exactly what you want; never a bare "continue" or "ok".** Name the action or the open items and what to do if blocked. Medium (B4, B5: official, Anthropic-tested, 2026).
4. **Mark a message as question or action.** A question about the report may get an assessment and no change; write "check X, then fix it if wrong" when you want both. Medium-weak (B6 is a suggested prompt for Fable 5, not a measured default).
5. **Ask for evidence, not self-report.** Request the command, its output, the diff; put "audit each claim against a tool result" in the brief. A fresh-context verifier beats self-critique on Fable (vendor claim), but on Opus 5 extra verification is waste. Medium for the audit line (C1, Anthropic internal), weak for rates of false reports (not found).
6. **Pushback: one evidence-based challenge, not insistence.** Describe the observed fact or test that contradicts the report and ask the agent to re-run or re-derive in writing, with room to work; do not name the answer you want; do not escalate or repeat. Add to the brief an invitation to object ("if the request is mistaken, say so"). Medium-weak: D1 (Claude Sonnet 5 among models, but chat tasks), D2, D4 and D3 (small models), D5 (agents obey mistaken advice); no direct study of parent-to-subagent pushback.
7. **Resume vs fresh.** Resume (SendMessage) when extending correct work; fresh agent or fork from before the error when the first interpretation was wrong, because resume keeps its reasoning and tool results. Weak-medium: B2 states what resume keeps; the rest follows from A1, A3.
8. **Choose the delivery.** Small course change: steer, which lands at the next tool boundary. Independent next job: queue. Agent is doing something harmful, irreversible or built on a wrong premise: interrupt, then restart. Otherwise let it finish. Medium (B3, B7, B10 agree); T3's own behavior is unverified (B11) and the same button can steer or queue in Codex (B9).
9. **Do not rewrite the original brief or system text mid-run.** Put the change in the newest turn. Medium (A6, official).
10. **Stop nudging after two or three.** Review the run instead. Medium (B4, A5).

## Gaps (not found)

- A replication of the multi-turn "lost" effect on GPT-6 or Claude 5.x tool-using agents.
- A direct test of "delta only" versus "restate whole intent" in agent runs.
- Measured cost of interruption; official T3 Code behavior for send, queue, interrupt.
- A study of orchestrator-to-subagent pushback; rate of false completion claims.
- Anthropic's original deployment-data post (D6) and the OpenAI "Mid-turn steering" Codex guide were not opened.
