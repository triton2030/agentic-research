# Routing receipt — `361faf00`

## Exact candidate

- File: `/Users/triton/Documents/GitHub/agentic-research/skills/1readable-code/recheck-2026-08-30/candidate/SKILL.md`
- SHA-256: `361faf00c670aa1e2e631c1d09b408c4aa5b3669d1f924f40cd2080c081989e4`
- Expected SHA-256: `361faf00c670aa1e2e631c1d09b408c4aa5b3669d1f924f40cd2080c081989e4`
- Hash check: **PASS**

## Read scope

Read only YAML frontmatter from:

1. the exact candidate above;
2. `/Users/triton/.codex/skills/1codebase-design/SKILL.md`;
3. `/Users/triton/.claude/skills/codebase-design/SKILL.md`.

The candidate body, neighboring bodies, official or older packages, history, reviews, and other agents' conclusions were not read. The full candidate file was consumed only by `shasum -a 256`; its contents were not printed or inspected.

## Independent routing

| Bare user phrase | Codex | Claude |
| --- | --- | --- |
| **use** — «Добавь мягкое удаление заметок и восстановление, сохрани публичный метод delete.» | **Selected/order:** 1. `1readable-code`.<br><br>**Decisive literal description words:** `Use before writing or changing code`; the design neighbor also says `use 1readable-code when the contract stays stable.` Keeping the public `delete` method is a stable-contract constraint, not a request to choose a contract, so `If choosing a contract, also use ... 1codebase-design in Codex` does not add the design skill.<br><br>**Nearest wrong reading:** treat any mention of a public method as `a contract decision` and add `1codebase-design`; the phrase actually fixes that method instead of asking to choose/review/change it.<br><br>**Expected:** choose `1readable-code`; add design only on a contract choice. **PASS** | **Selected/order:** 1. `1readable-code`.<br><br>**Decisive literal description words:** `Use before writing or changing code`; the Claude design neighbor says `Не вызывай для обычной реализации внутри уже выбранного interface`. Keeping `delete` fixes the existing public interface rather than requesting a seam/interface choice.<br><br>**Nearest wrong reading:** infer a design task from the word “метод” and add `codebase-design`, despite the explicit preservation constraint and the neighbor's ordinary-implementation exclusion.<br><br>**Expected:** choose `1readable-code`; add design only on a contract choice. **PASS** |
| **skip** — «Объясни, что делает модуль удаления заметок; код не меняй.» | **Selected/order:** none.<br><br>**Decisive literal description words:** candidate trigger `before writing or changing code` is negated by `код не меняй`; the neighbor requires `code work reaches a contract decision`, which is also absent.<br><br>**Nearest wrong reading:** select `1readable-code` merely because the explanation concerns code.<br><br>**Expected:** do not choose `1readable-code`. **PASS** | **Selected/order:** none.<br><br>**Decisive literal description words:** candidate trigger `before writing or changing code` is negated by `код не меняй`; the neighbor's triggers `спроектировать или улучшить interface модуля` and `выбрать seam/adapter` are absent.<br><br>**Nearest wrong reading:** select `1readable-code` from the code-related noun “модуль” while ignoring the action “объясни” and the no-change constraint.<br><br>**Expected:** do not choose `1readable-code`. **PASS** |
| **near-miss** — «Выбери контракт между сервисом заметок и хранилищем, но пока не пиши код.» | **Selected/order:** 1. `1codebase-design`.<br><br>**Decisive literal description words:** `Use when code work reaches a contract decision: choosing, reviewing, or changing an interface, seam, adapter, port, component boundary, dependency boundary`; a service/storage contract is an interface/seam/dependency-boundary choice. Candidate trigger `before writing or changing code` is not met because the user says `не пиши код`.<br><br>**Nearest wrong reading:** isolate `If choosing a contract, also use ... 1codebase-design in Codex` from the candidate's first-sentence gate and select both skills; “also” does not independently turn a non-coding design request into writing/changing code.<br><br>**Expected:** design skill yes, `1readable-code` no. **PASS** | **Selected/order:** 1. `codebase-design`.<br><br>**Decisive literal description words:** `спроектировать или улучшить interface модуля` and `выбрать seam/adapter`; the service/storage contract is precisely that seam/interface choice. Candidate trigger `before writing or changing code` is not met because the user says `не пиши код`.<br><br>**Nearest wrong reading:** select both skills because the candidate's second sentence mentions choosing a contract, while ignoring that its trigger is scoped to writing/changing code.<br><br>**Expected:** design skill yes, `1readable-code` no. **PASS** |

## Verdict

**PASS — 6/6 runtime-scenario decisions match the expected routing.** The candidate cleanly routes implementation/change to `1readable-code`, skips explanation-only work, and does not capture a design-only contract choice. Runtime-specific design naming is correct: `1codebase-design` in Codex and `codebase-design` in Claude.

## Gaps

- This is a frontmatter-only routing evaluation; no skill-body behavior or runtime invocation was tested.
- The “use” phrase constrains one public method but does not state whether another interface must be introduced for restoration. Routing therefore follows the bare request and does not invent an unstated contract choice; an implementation that later reaches such a choice should add the runtime-specific design skill then.
