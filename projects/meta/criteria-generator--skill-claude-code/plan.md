# Criteria Generator Implementation Plan

> Historical note: this plan describes an older implementation pass. The current Claude Code version of the skill lives in `SKILL.md` and `references/`, including the `ops/` and `ops/NORTH-STAR.md` behavior.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a global Claude Code skill `criteria-generator` that turns any user task into the same task augmented with LLM-proof acceptance criteria.

**Architecture:** A skill directory at `~/.claude/skills/criteria-generator/` containing one `SKILL.md` (≤300 lines) and three progressive-disclosure references. The skill runs 10 sequential steps: Capture → Discovery → Read → Intent → EVPI gate → Draft → Adversarial → Quality gate → Emit → Offer execution. Each step has a required artifact and TodoWrite pairing.

**Tech Stack:** Plain Markdown. YAML frontmatter for skill metadata. No code. Claude Code Skill tool is the runtime.

**Note on commits:** The working repo `agentic-research` is not a git repository. "Commit" steps below are replaced with "Verify file written, list contents". The deployed skill lives in `~/.claude/skills/`, which may or may not be versioned separately — out of scope.

---

### Task 1: Scaffold directory structure

**Files:**
- Create: `~/.claude/skills/criteria-generator/` (directory)
- Create: `~/.claude/skills/criteria-generator/references/` (directory)

- [ ] **Step 1: Check skill root exists**

Run: `ls ~/.claude/skills/ 2>/dev/null || echo "MISSING"`
Expected: either directory listing or `MISSING`. If MISSING, create it:
`mkdir -p ~/.claude/skills`

- [ ] **Step 2: Check that target skill does not already exist**

Run: `ls ~/.claude/skills/criteria-generator/ 2>/dev/null && echo "EXISTS" || echo "CLEAR"`
Expected: `CLEAR`. If `EXISTS`, stop and ask user whether to overwrite.

- [ ] **Step 3: Create skill directories**

Run: `mkdir -p ~/.claude/skills/criteria-generator/references`
Expected: no output, exit 0.

- [ ] **Step 4: Verify**

Run: `ls -la ~/.claude/skills/criteria-generator/`
Expected: empty directory plus `references/` subdir.

---

### Task 2: Write SKILL.md

**Files:**
- Create: `~/.claude/skills/criteria-generator/SKILL.md`

- [ ] **Step 1: Write SKILL.md with full content below**

```markdown
---
name: criteria-generator
description: Use BEFORE implementing any non-trivial task to augment the user prompt with LLM-proof acceptance criteria. Analyzes project context (CLAUDE.md, AGENTS.md, READMEs, docs/, memory/, recent git) to infer true intent, then generates criteria as guardrails against LLM failure modes (hallucination, premature completion, mock verification, formal-pass-bad-work). Required when the task is ambiguous or agent quality matters. Output is the augmented prompt only — no implementation.
---

# Criteria Generator

Turn an ambiguous user task into a prompt armored with LLM-proof acceptance criteria.

**Announce at start:** "I'm using the criteria-generator skill to produce acceptance criteria."

## When to use

- Non-trivial task where execution quality matters.
- Task formulation is vague or could be interpreted multiple ways.
- Before delegating a task to another agent or subagent.
- Before starting work on anything whose "done" state is not obvious.

## When NOT to use

- Trivial one-line fixes (typo, obvious rename).
- Pure questions that do not request action.
- Tasks already accompanied by explicit acceptance criteria.

## Hard gate

Do not implement the user's task while running this skill. The only output of this skill is the augmented prompt. Implementation begins only after the user answers Step 10.

## Process

Create one TodoWrite item per step below. Each step has a required artifact. Do not advance without producing it.

### Step 1: Capture

Quote the user's original task verbatim. This becomes the `Original task` block in the final output.

Artifact: verbatim quote of user input, stored for Step 9.

### Step 2: Discovery

Probe for available context sources. Do not assume; check.

Required probes (skip only if the path obviously cannot exist):

- `CWD/CLAUDE.md`, `~/.claude/CLAUDE.md`
- `CWD/AGENTS.md`, `CWD/GEMINI.md`
- `CWD/README*`
- `CWD/docs/`
- `CWD/ops/`, `CWD/_research/`, `CWD/knowledge/guides/`
- Memory index: `~/.claude/projects/<project-slug>/memory/MEMORY.md`
- Git: `git log --oneline -20` and `git status` (only if `.git` exists in CWD or an ancestor)

For non-standard project layouts see `references/discovery-map.md`.

Artifact: list of paths found, grouped as `will read` vs `noted, skipped`.

### Step 3: Selective read

Read only the sources likely relevant to the task topic. For each read, record one sentence of what changed in your understanding.

Red flag: reading everything "just in case". That is rationalization. Pick by topic match.

Artifact: bulleted list of `<path>: <one-line takeaway>`.

### Step 4: Intent distillation

Produce two blocks:

- **Understood intent** (1-3 sentences): what the agent must actually do.
- **Unknowns**: explicit list of facts that would change the criteria if known.

Artifact: both blocks written out.

### Step 5: EVPI gate

For each unknown, answer two questions:

1. Does available context resolve it? If yes, resolve and continue.
2. If not, does asking the user one targeted question materially change the criteria?

If 1-3 unknowns pass the EVPI test, stop and ask the user now via AskUserQuestion. Wait for answers before continuing.

Otherwise record each surviving unknown as an explicit Assumption in the output.

Artifact: either user answers captured, or an Assumptions list finalized.

### Step 6: Draft criteria

Draft three buckets:

- **Must** — conditions that, if missing, mean the task is not done.
- **Must not** — anti-patterns that would look correct but represent a bypass.
- **Verification protocol** — concrete commands or actions that prove the Must items.

Every Must item requires an `Evidence:` subfield naming the observable artifact that proves it (file contents, command output, URL, specific number, screenshot).

See `references/format-examples.md` for worked examples across task types.

Artifact: draft of all three buckets.

### Step 7: Adversarial pass

Play a lazy agent. For each Must item answer: "How would I formally pass this while doing the task badly?"

For every bypass you name, add or strengthen a criterion until the bypass is blocked.

Common bypasses to probe (non-exhaustive — full catalog in `references/failure-modes.md`):

- Claiming verification without running the command.
- Mock-only implementations that look real.
- Skipping edge cases not named explicitly.
- Renaming or moving code instead of fixing logic.
- Summary-based review instead of reading the actual artifact.
- Adding superficial comments in place of behavioral change.
- Declaring success on the happy path only.

Artifact: list of bypasses found plus the criterion that now closes each.

### Step 8: Quality gate

Check each criterion against three axes:

- **Observable** — does it name a concrete artifact, not "I checked"?
- **Unambiguous** — can only one reading pass it?
- **Non-bypassable** — can Step 7 find a formal-pass-bad-work route? If yes, return to Step 7.

Drop or rewrite any criterion that fails any axis.

Artifact: final criteria set with all three axes satisfied.

### Step 9: Emit output

Print the augmented prompt in this exact format. Emit nothing else outside this block:

    ## Original task
    <verbatim quote>

    ## Understood intent
    <1-3 sentences>

    ## Assumptions (not verified with user)
    - ...

    ## Acceptance criteria

    ### Must (blocks completion)
    - [ ] <criterion> — **Evidence**: <artifact>

    ### Must not (anti-patterns)
    - [ ] <forbidden pattern> — **Why this would be bypassed**: <bypass mechanic>

    ### Verification protocol
    1. <command or action>
       Expected: <observable output>

If there is nothing to put in Assumptions or Must not, omit that heading entirely rather than leaving it empty.

Artifact: full output in chat.

### Step 10: Offer execution

Ask the user exactly one question:

> "Acceptance criteria generated. Want me to execute the task using these criteria as a hard contract?"

If yes: stop this skill; proceed to execution treating each Must item as blocking and each Must-not as forbidden. Announce the transition.
If no: stop. Return control.

## Red flags (rationalizations to block)

| You catch yourself thinking | Actually |
|---|---|
| "Task is obvious, skip Discovery" | Discovery is always cheap. Skipping is the #1 source of wrong criteria. |
| "Adversarial pass is overkill here" | The skill exists for this step. If you skip it, use a different tool. |
| "User context is thin, make a judgment call" | That is exactly when the EVPI gate matters. Ask. |
| "Evidence field is implied by the criterion" | Implied ≠ enforced. LLMs skip implied. Write it out. |
| "Three axes are a formality" | Each one blocks a distinct failure mode. Run them. |
| "One-shot is faster than 10 steps" | Speed is not the goal. Non-bypassability is. |

## Output constraint

The skill produces the augmented prompt and nothing else. No code, no implementation, no partial work. Implementation begins only after the user answers Step 10.
```

- [ ] **Step 2: Verify file written**

Run: `wc -l ~/.claude/skills/criteria-generator/SKILL.md`
Expected: between 150 and 300 lines.

- [ ] **Step 3: Verify frontmatter parses**

Run: `head -5 ~/.claude/skills/criteria-generator/SKILL.md`
Expected: first line `---`, then `name: criteria-generator`, then `description: Use BEFORE...`, then `---`.

---

### Task 3: Write references/discovery-map.md

**Files:**
- Create: `~/.claude/skills/criteria-generator/references/discovery-map.md`

- [ ] **Step 1: Write file with full content below**

```markdown
# Discovery Map

Extended patterns for Step 2 of `criteria-generator`. Use when the default probe list in SKILL.md is insufficient.

## Default probes (repeated from SKILL.md)

- `CWD/CLAUDE.md`, `~/.claude/CLAUDE.md`
- `CWD/AGENTS.md`, `CWD/GEMINI.md`
- `CWD/README*`
- `CWD/docs/`
- `CWD/ops/`, `CWD/_research/`, `CWD/knowledge/guides/`
- `~/.claude/projects/<project-slug>/memory/MEMORY.md`
- `git log --oneline -20`, `git status` (if `.git` exists)

## By project type

### Node / TypeScript repo

- `package.json` — scripts, dependencies shape the verification protocol.
- `tsconfig.json` — strictness affects what "passes" means.
- `.eslintrc*`, `.prettierrc*` — style constraints become Must-not items.
- `tests/`, `__tests__/`, `*.test.*` — existing test patterns to match.

### Python repo

- `pyproject.toml` / `setup.py` / `requirements*.txt`
- `pytest.ini`, `tox.ini`, `conftest.py`
- `mypy.ini`, `.ruff.toml`

### Go repo

- `go.mod`, `go.sum`
- `Makefile` if present
- `*_test.go` patterns

### Rust repo

- `Cargo.toml`
- `tests/`, `benches/`
- `clippy.toml`

### Docs-only / knowledge repo

- Top-level `_`-prefixed folders (often convention folders).
- `MKDocs.yml`, `mkdocs.yaml`, `docusaurus.config.*`, `astro.config.*`.
- Any `CONTRIBUTING.md`, `STYLE.md`.

### Claude Code plugin / skill project

- `.claude/settings.json`
- `plugins/*/plugin.json`
- `skills/*/SKILL.md`
- `agents/*.md`

## By task type

### "Fix this bug"

Add to reads: recent `git log -p` for the file in question; any failing test output if the user quoted one; issue tracker mention if present in a linked `ISSUES.md` or `ops/`.

### "Add this feature"

Add to reads: the closest sibling feature (pick by directory adjacency); any design doc matching the feature keywords in `docs/` or `_research/`.

### "Research / investigation"

Add to reads: `_research/` and memory files that mention the topic keywords. Skip source code unless the question is about code behavior.

### "Refactor"

Add to reads: all current consumers of the target symbol (Grep). Refactors without a consumer map are a bypass risk.

### "Write documentation"

Add to reads: existing docs in the same section, style guide if any, audience profile in memory or team docs.

## What not to read

Skip unless the task explicitly demands it:

- Generated files (`dist/`, `build/`, `node_modules/`, `.venv/`, `target/`).
- Large lockfiles (`package-lock.json`, `yarn.lock`, `Cargo.lock`) — date and version are enough.
- Entire `docs/` when only one page is relevant.
- Full git history when `-20` gives you the tone.

Reading too much is itself a bypass — it dilutes the criteria by drowning the model in irrelevant constraints.
```

- [ ] **Step 2: Verify**

Run: `wc -l ~/.claude/skills/criteria-generator/references/discovery-map.md`
Expected: 70-120 lines.

---

### Task 4: Write references/failure-modes.md

**Files:**
- Create: `~/.claude/skills/criteria-generator/references/failure-modes.md`

- [ ] **Step 1: Write file with full content below**

```markdown
# LLM Failure Modes

Catalog of ways language models produce formal-pass-bad-work. Use during Step 7 (adversarial pass) of `criteria-generator`. For each mode there is a probe question and a countermeasure criterion.

## 1. Claimed verification

**Pattern:** Model writes "I verified X" without running the command or reading the file.
**Probe:** Does the criterion allow a pass with the string "verified" alone?
**Countermeasure:** Require command and expected output, not a claim. `Evidence: output of <cmd>` not `Evidence: I ran it`.

## 2. Mock-shaped implementation

**Pattern:** Function returns the happy-path value hardcoded; passes one test but implements nothing.
**Probe:** Can the Must criterion be satisfied by returning a constant?
**Countermeasure:** Include at least two input variants with different expected outputs, or require a property-style check.

## 3. Silent edge case skipping

**Pattern:** Empty input, null, large input, unicode, concurrency — model handles the cases it thought of and omits the rest.
**Probe:** What inputs outside the happy path would break the naive solution?
**Countermeasure:** Enumerate at least the edge cases the context implies (from existing tests, similar code, or user examples).

## 4. Rename without refactor

**Pattern:** Model moves or renames a symbol instead of changing behavior.
**Probe:** Would the criterion pass if nothing behavioral changed, only the name?
**Countermeasure:** Tie the Must item to observable behavior change (output diff, metric, log line, regression test).

## 5. Summary-based review

**Pattern:** Agent says "I reviewed the file" but only saw the first chunk.
**Probe:** Does the criterion require a specific line or section of the file to be cited?
**Countermeasure:** Name a specific artifact to quote back — a line range, a function, a config key.

## 6. Comment as behavior

**Pattern:** Model adds a `// TODO: handle X` or a docstring instead of handling X.
**Probe:** Does the criterion differentiate behavioral change from textual change?
**Countermeasure:** Require test-level or runtime-level evidence, not just file diff.

## 7. Happy-path-only success claim

**Pattern:** "All tests pass" meaning only the one test that was written.
**Probe:** Does the criterion require the full suite, the specific new tests, and no-regressions?
**Countermeasure:** Break verification into: new tests pass, existing suite passes, no skipped tests added.

## 8. Stale-context hallucination

**Pattern:** Model cites a function, file, or flag that existed once but is gone.
**Probe:** Could the criterion be satisfied by referencing something that no longer exists?
**Countermeasure:** Require a read of the current file as part of verification, not memory of it.

## 9. Tool not actually invoked

**Pattern:** Model narrates a tool call in prose but never emits it.
**Probe:** Can the criterion be satisfied from chat text alone?
**Countermeasure:** Require a tool_use block as evidence, named by tool and arg shape.

## 10. Scope creep as diversion

**Pattern:** Model fixes the easy adjacent thing and reports success on both.
**Probe:** Is the criterion narrow enough that adjacent fixes do not satisfy it?
**Countermeasure:** State the target file and target symbol explicitly; forbid unrelated changes in Must not.

## 11. Test-passing-but-wrong

**Pattern:** Test is written loosely enough that a wrong implementation passes it.
**Probe:** Could the test pass with a pathological implementation?
**Countermeasure:** Require at least one negative assertion (something that must NOT happen) alongside positive ones.

## 12. Specification drift

**Pattern:** Model gradually reinterprets the task mid-work to match what it found easy.
**Probe:** Does the criterion lock the scope in a way the model cannot soften?
**Countermeasure:** Quote the user's exact phrasing in the Must items; forbid paraphrase-as-spec.

## 13. Confidence theatre

**Pattern:** Model writes "clearly", "obviously", "as expected" to paper over uncertainty.
**Probe:** Does any Must item depend on agent self-report of confidence?
**Countermeasure:** Replace any self-report with an external check (command, file, number, human review).

## Using this catalog

In Step 7, do not copy every item. Pick the 2-5 modes most relevant to the task type:

- Code changes: 1, 2, 3, 4, 6, 7, 10, 11.
- Refactors: 4, 5, 10, 12.
- Research / writing: 5, 8, 12, 13.
- Config / infra: 1, 4, 8, 10.
- Tool integration: 1, 9, 10.

For each chosen mode, run the Probe against your draft criteria and apply the Countermeasure.
```

- [ ] **Step 2: Verify**

Run: `wc -l ~/.claude/skills/criteria-generator/references/failure-modes.md`
Expected: 80-140 lines.

---

### Task 5: Write references/format-examples.md

**Files:**
- Create: `~/.claude/skills/criteria-generator/references/format-examples.md`

- [ ] **Step 1: Write file with full content below**

```markdown
# Format Examples

Worked examples of `criteria-generator` output across task types. Use as shape templates, not as content to copy.

## Example 1: Code bugfix

**Input:**
> "Пользователь жалуется, что при экспорте CSV пропадают строки. Почини."

**Output:**

    ## Original task
    Пользователь жалуется, что при экспорте CSV пропадают строки. Почини.

    ## Understood intent
    Найти и устранить причину, по которой часть строк не попадает в экспортированный CSV. "Починено" означает: конкретный баг идентифицирован, исправлен, и существует тест, который падал бы без фикса.

    ## Assumptions (not verified with user)
    - Речь про экспорт в функции `exportToCSV` в `src/exports/csv.ts` (единственный матч по grep).
    - "Пропадают" означает отсутствуют в выводе, а не дублируются.

    ## Acceptance criteria

    ### Must (blocks completion)
    - [ ] Root cause сформулирован одним предложением со ссылкой на строку кода — **Evidence:** строка вида `src/exports/csv.ts:LINE — <причина>`.
    - [ ] Регрессионный тест написан и падает на текущем коде — **Evidence:** вывод `npm test -- csv` до фикса с конкретным `expected N rows, got M`.
    - [ ] Фикс применён — **Evidence:** diff в `src/exports/csv.ts`, не более 20 строк изменений, не затрагивает не связанные функции.
    - [ ] Регрессионный тест проходит после фикса — **Evidence:** вывод `npm test -- csv` с `N passed`.
    - [ ] Полный тестовый набор проходит — **Evidence:** вывод `npm test` с итоговой строкой `All tests passed`.

    ### Must not (anti-patterns)
    - [ ] Не добавлять `if (rows.length === 0) return` или аналогичный silencing — **Why this would be bypassed:** заставит тест "пройти" путём скрытия проблемы.
    - [ ] Не менять форматирование или стилистику файла вне зоны фикса — **Why this would be bypassed:** раздувает diff и маскирует реальное изменение.
    - [ ] Не перезаписывать входной массив перед экспортом — **Why this would be bypassed:** имитирует корректный вывод, но не устраняет причину.

    ### Verification protocol
    1. `git diff --stat src/exports/csv.ts`
       Expected: одно-два изменённых места, <20 строк.
    2. `npm test -- csv 2>&1 | tail -20`
       Expected: регрессионный тест в списке PASSED.
    3. `npm test 2>&1 | tail -5`
       Expected: строка `Tests: X passed`, ноль failed.

## Example 2: Research

**Input:**
> "Разберись, какие новые техники prompt compression появились в 2026 году и что применимо у нас."

**Output:**

    ## Original task
    Разберись, какие новые техники prompt compression появились в 2026 году и что применимо у нас.

    ## Understood intent
    Собрать обзор техник prompt compression 2026 года, отфильтровать по применимости в нашем текущем стеке (Claude Code + Anthropic SDK), и вернуть короткий рабочий список "что внедрять" с обоснованием.

    ## Assumptions (not verified with user)
    - "У нас" = проект `agentic-research` и соседние Claude Code workflows.
    - Применимость оценивается по трём осям: reduction %, complexity cost, зависимость от кастомной инфраструктуры.

    ## Acceptance criteria

    ### Must (blocks completion)
    - [ ] Минимум 5 техник с 2026 года названы, у каждой есть источник — **Evidence:** markdown-список с прямыми ссылками (URL) на статьи или репозитории 2026 года.
    - [ ] Для каждой техники указано одно предложение о механизме — **Evidence:** поле `Mechanism:` под каждой техникой, не копия аннотации, а своя формулировка.
    - [ ] Применимость оценена по трём осям — **Evidence:** таблица `technique | reduction | complexity | infra dep`.
    - [ ] Итоговый короткий список "внедрять / отложить / мимо" — **Evidence:** раздел `Verdict` с 3 сегментами и обоснованием из одной строки на каждую технику.

    ### Must not (anti-patterns)
    - [ ] Не включать техники старше 2026 года — **Why this would be bypassed:** легко набрать объём за счёт классики и прикрыть отсутствие реально нового.
    - [ ] Не ссылаться на блоги без первичного источника (paper / repo) — **Why this would be bypassed:** вторичные пересказы часто искажают механизм.
    - [ ] Не делать вывод "применимо" без конкретного места в нашем стеке — **Evidence:** каждая техника в Verdict ссылается на конкретный скрипт, скилл или workflow.

    ### Verification protocol
    1. Проверить, что все URL-ы в источниках отдают 200 — **Expected:** нет 404.
    2. Прочитать одну статью целиком и сверить с полем `Mechanism` — **Expected:** формулировка точная, не вводит в заблуждение.

## Example 3: Skill or agent creation

**Input:**
> "Сделай мне скилл для ревью пулл-реквестов."

**Output:**

    ## Original task
    Сделай мне скилл для ревью пулл-реквестов.

    ## Understood intent
    Создать Claude Code скилл, который по запросу анализирует PR (diff + описание) и возвращает структурированный ревью: блокирующие замечания, предложения, вопросы, общий вердикт.

    ## Assumptions (not verified with user)
    - Скилл глобальный (`~/.claude/skills/`), не привязан к одному репозиторию.
    - Источник PR — команда `gh pr view` или URL.
    - Формат вывода — markdown в чат.

    ## Acceptance criteria

    ### Must (blocks completion)
    - [ ] Файл `~/.claude/skills/pr-review/SKILL.md` существует — **Evidence:** `ls ~/.claude/skills/pr-review/SKILL.md`.
    - [ ] Frontmatter содержит `name` и `description` с явным "when to use" — **Evidence:** первые 5 строк файла.
    - [ ] Рабочий ход имеет нумерованные шаги с артефактами — **Evidence:** раздел `## Process` с шагами Step 1…N, у каждого `Artifact:` строка.
    - [ ] Раздел Red Flags присутствует с минимум 3 пунктами — **Evidence:** таблица или список под заголовком `## Red flags`.
    - [ ] Smoke test пройден на 1 реальном PR — **Evidence:** вывод скилла на конкретном PR, прикреплённый к диалогу.

    ### Must not (anti-patterns)
    - [ ] Не писать скилл как "общие правила ревью" без рабочего хода — **Why this would be bypassed:** превращается в энциклопедию, не в инструмент.
    - [ ] Не требовать внешних сервисов кроме `gh` — **Why this would be bypassed:** ломает портативность.
    - [ ] Не возвращать размазанный вывод без структуры — **Evidence:** выход должен иметь фиксированные секции Blocking / Suggestions / Questions / Verdict.

    ### Verification protocol
    1. `ls ~/.claude/skills/pr-review/` — **Expected:** `SKILL.md` плюс `references/` при необходимости.
    2. Invoke skill on a sample PR URL — **Expected:** вывод в заданном формате, без отклонений.

## How to pick the right shape

- **Code changes:** всегда Evidence = команда + ожидаемый вывод.
- **Research / writing:** Evidence = ссылки, цитаты, таблицы.
- **Infra / config:** Evidence = вывод `diff`, `kubectl get`, `terraform plan`, etc.
- **Skill / agent authoring:** Evidence = путь к файлу плюс структурная проверка.
```

- [ ] **Step 2: Verify**

Run: `wc -l ~/.claude/skills/criteria-generator/references/format-examples.md`
Expected: 130-200 lines.

---

### Task 6: Smoke-test the skill on three sample tasks

This task runs the skill end-to-end in a fresh Claude Code session and checks that the output matches the contract. Since the skill is purely instructional, the "test" is an execution trace.

**Files:**
- Create: `projects/meta/criteria-generator--skill-claude-code/smoke-tests.md` (inside the working repo, not the deployed skill)

- [ ] **Step 1: Reload skill visibility**

Open a new Claude Code session in any directory. In that session run: `/skills` (or check the list of available skills).
Expected: `criteria-generator` appears.

- [ ] **Step 2: Run test A — ambiguous code task**

In the new session, say: "Активируй criteria-generator. Задача: `добавь логирование ошибок в бэкенд`."
Expected behavior:
1. Skill announces itself.
2. Discovery happens (probes listed).
3. At least one EVPI question asked (which backend, which logger, where to send) OR explicit assumptions recorded.
4. Output in the exact template, Evidence fields present.
5. Step 10 offer printed.

Record the output in `smoke-tests.md` under `## Test A`.

- [ ] **Step 3: Run test B — research task**

Same session or fresh. Say: "Активируй criteria-generator. Задача: `собери обзор self-healing CI систем за 2026`."
Expected:
- Assumptions include scope (what "review" means).
- Must items name sources, mechanism field, verdict section.
- Must-not names "no pre-2026 material".

Record as `## Test B`.

- [ ] **Step 4: Run test C — trivial task (should still produce minimal criteria)**

Say: "Активируй criteria-generator. Задача: `поправь опечатку в README`."
Expected:
- Discovery minimal.
- Must items: opеchatka identified, diff is 1-3 chars, no unrelated changes.
- Output short but in full template.

Record as `## Test C`.

- [ ] **Step 5: Grade outputs**

For each of A, B, C, in `smoke-tests.md` fill in:

```
Template compliance: pass / fail
Evidence fields present on every Must: pass / fail
Adversarial pass visible (Must not section non-trivial): pass / fail
EVPI gate triggered correctly: pass / fail / n/a
Notes: <free text>
```

Expected: all three tests pass all four checks. If any fail, return to the corresponding SKILL.md step and tighten wording before proceeding.

- [ ] **Step 6: Verify the smoke-tests file**

Run: `wc -l /Users/triton/Documents/GitHub/agentic-research/projects/meta/criteria-generator--skill-claude-code/smoke-tests.md`
Expected: >50 lines with three test blocks and a grading table.

---

### Task 7: Update project inventory

**Files:**
- Modify: `/Users/triton/Documents/GitHub/agentic-research/meta/inventory-claude-code.md`

- [ ] **Step 1: Read current inventory**

Read the file. Locate sections `Что Есть` and `Чего Не Хватает`.

- [ ] **Step 2: Remove `criteria-generator` from "Чего Не Хватает" if listed**

If an entry for criteria/acceptance/intent skill exists under `Чего Не Хватает`, delete it.

- [ ] **Step 3: Add entry under `Что Есть`**

Insert the following entry in alphabetical order within `Что Есть`:

```md
### criteria-generator
- Тип: skill
- Источник: наш
- Что делает: превращает пользовательскую задачу в тот же запрос с добавленными LLM-устойчивыми критериями приёмки.
```

- [ ] **Step 4: Verify inventory still parses under AGENTS.md rules**

Run: `head -60 /Users/triton/Documents/GitHub/agentic-research/meta/inventory-claude-code.md`
Expected: valid markdown, three-field entries, no broken headings.

---

### Task 8: Final acceptance — run criteria-generator on itself

This is the self-application test: the skill should be able to generate acceptance criteria for the task "build criteria-generator skill". If the generated criteria match or exceed this plan, the skill is working.

**Files:**
- Create: `/Users/triton/Documents/GitHub/agentic-research/projects/meta/criteria-generator--skill-claude-code/self-application.md`

- [ ] **Step 1: Start fresh session, cwd = agentic-research**

- [ ] **Step 2: Invoke skill on itself**

Prompt: "Активируй criteria-generator. Задача: `собрать глобальный Claude Code skill criteria-generator, который по запросу пользователя возвращает тот же промпт с добавленными LLM-устойчивыми критериями`."

- [ ] **Step 3: Capture output**

Save full skill output to `self-application.md`.

- [ ] **Step 4: Compare against this plan**

In `self-application.md` below the captured output, add a comparison block:

```md
## Comparison to plan

| Plan item | Covered by generated criteria? | Notes |
|---|---|---|
| Global deployment to ~/.claude/skills/ | yes / no | ... |
| SKILL.md with frontmatter description | yes / no | ... |
| 10-step process with artifacts | yes / no | ... |
| Three references files | yes / no | ... |
| Red Flags block | yes / no | ... |
| Smoke tests | yes / no | ... |
```

Expected: at least 4 of 6 rows = yes. Missing items are either genuine plan gaps or signals to strengthen the skill.

- [ ] **Step 5: If gaps found, iterate**

For each row marked "no":
- Decide: is this a plan gap (this plan should have it) or a skill gap (the skill should have surfaced it)?
- Plan gap → add a task to this plan.
- Skill gap → edit SKILL.md or references to strengthen the corresponding step.

---

## Self-review

Spec coverage check against `projects/meta/criteria-generator--skill-claude-code/README.md`:

- [x] EVPI-гибрид режим работы → SKILL.md Step 5.
- [x] Адаптивный discovery → SKILL.md Step 2 + `references/discovery-map.md`.
- [x] Два прохода (draft + adversarial) → Steps 6-7.
- [x] Три оси качества → Step 8.
- [x] Жёсткий шаблон output → Step 9.
- [x] Offer execution → Step 10.
- [x] Учёт LLM-потребления скиллов → frontmatter description, TodoWrite per step, Red Flags block, progressive disclosure в references/.
- [x] Структура файлов → Task 1 + Tasks 2-5.
- [x] Открытый вопрос "качество самого скилла" → Task 6 (smoke tests) + Task 8 (self-application).

Placeholder scan: no TBD, no "TODO", no "similar to Task N". All code/content blocks contain full text. Expected outputs named for every verification command.

Type consistency: skill name `criteria-generator` used everywhere. File paths under `~/.claude/skills/criteria-generator/` consistent across tasks. Step numbers 1-10 match between SKILL.md Task 2 and smoke test expectations in Task 6.

Open questions from spec answered:
- Fast mode → rejected by Step 10; if задача тривиальна, output получается короткий естественным образом.
- Overly strict criteria → quality gate Step 8 plus adversarial pass caps overreach.
- Codex variant → explicitly out of scope, flagged in spec as future work.

## Execution handoff

**Plan complete and saved to `projects/meta/criteria-generator--skill-claude-code/plan.md`. Two execution options:**

**1. Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review between tasks, fast iteration.

**2. Inline Execution** — Execute tasks in this session using executing-plans, batch execution with checkpoints.

**Which approach?**
