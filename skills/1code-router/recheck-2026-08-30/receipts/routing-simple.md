# Simple routing receipt

## Scope

- Candidate: `/Users/triton/Documents/GitHub/agentic-research/skills/1readable-code/recheck-2026-08-30/candidate/SKILL.md`
- Exact SHA-256: `6aa4ec3785d3c57d2cec142c92e4541dc52e114225661f9c5ffee7382e9496c7` — matches expected.
- Content inspected: YAML frontmatter only from the candidate, `/Users/triton/.codex/skills/1codebase-design/SKILL.md`, and `/Users/triton/.claude/skills/codebase-design/SKILL.md`.
- Excluded: candidate body, official or old packages, history, reviews, and other agents' conclusions.

## Routing matrix

| Runtime | Phrase | Selected skills / order | Literal decisive description words | Nearest wrong reading | Result |
| --- | --- | --- | --- | --- | --- |
| Codex | Use: «Добавь мягкое удаление заметок и восстановление, сохрани публичный метод delete.» | `1readable-code` | Candidate: “before writing or changing code”; Codex profile: “use 1readable-code when the contract stays stable” | Treat “публичный метод delete” as a request to choose or change an interface, although the phrase explicitly says to preserve it. | PASS |
| Claude | Use: «Добавь мягкое удаление заметок и восстановление, сохрани публичный метод delete.» | `1readable-code` | Candidate: “before writing or changing code”; Claude profile excludes “обычной реализации внутри уже выбранного interface” | Infer a new interface design from the new soft-delete behavior, although the public method is fixed. | PASS |
| Codex | Skip: «Объясни, что делает модуль удаления заметок; код не меняй.» | none | Candidate requires “writing or changing code”; Codex profile requires “code work” reaching “a contract decision” | Route on the code-adjacent noun “модуль”, despite the explicit no-change explanation request and no contract decision. | PASS |
| Claude | Skip: «Объясни, что делает модуль удаления заметок; код не меняй.» | none | Candidate requires “writing or changing code”; Claude profile requires “спроектировать или улучшить interface” or “выбрать seam/adapter” | Treat explanation of an existing module as interface improvement or design. | PASS |
| Codex | Near-miss: «Выбери контракт между сервисом заметок и хранилищем, но пока не пиши код.» | `1codebase-design` | Codex profile: “contract decision: choosing … an interface, seam, adapter, port … dependency boundary”; candidate requires “writing or changing code” | Select `1readable-code` because contract selection may precede later coding, despite “пока не пиши код” and the dedicated contract-decision trigger. | PASS |
| Claude | Near-miss: «Выбери контракт между сервисом заметок и хранилищем, но пока не пиши код.» | `codebase-design` | Claude profile: “спроектировать или улучшить interface модуля” and “выбрать seam/adapter”; candidate requires “writing or changing code” | Select `1readable-code` as generic preparation for future code instead of the explicit interface/seam owner. | PASS |

## Verdict

**PASS — 6/6.** The frontmatter descriptions separate ordinary code change, read-only explanation, and contract selection as required in both runtimes.

## Gaps

- This is a frontmatter-only semantic routing evaluation; it does not execute a runtime selector.
- Skill bodies and package behavior were intentionally not inspected, so this receipt makes no claim about instruction quality after routing.
