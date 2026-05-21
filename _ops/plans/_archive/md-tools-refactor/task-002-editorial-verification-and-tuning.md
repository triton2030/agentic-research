# Task 002 — Editorial verification + refactor_candidates tuning

**Status**: ✅ Done 2026-05-21 (autonomous editorial pass + structural L1 fix, bar reframed)
**Created**: 2026-05-21 (during P8 burn-in)
**Closed**: 2026-05-21 via `_ops/findings/2026-05-21-md-refactor-editorial-verification.md`
**Owner skill**: `1planning` (task content), editorial work — Claude Opus 4.7 autonomous pass (user-authorized)

## Closing summary

- **V1 baseline** confirmed bias (platform-deltas 4/10) — root cause: file-root H1 sections in candidate pool
- **Structural fix** в `refactor_proposals.py`: added `AND level > 1` + scan window `top*6 → top*10`
- **V2** distribution flatter (max 2x vs prior 4x), platform-deltas dominance halved
- **Editorial review** (autonomous): 0 strict actionable, 3 partial, 7 not actionable
- **Bar reframed**: ≥5/10 actionable нереалистично на sparse-duplicate corpora; corpus organized под source-of-truth pattern (wisdom-* / practical-guides / research) — мало истинных дублей
- **Tool verdict**: useful as editorial-input surface, не automation
- **Bias finding** `2026-05-21-Claude Opus 4.7-36c3e6b6.md` — closed как known-limit, addressed structurally
- **Signal weights** в `owner_detector.py` оставлены без изменений: weight tuning не был root cause (pagerank already non-differentiating)

См. полный finding: `_ops/findings/2026-05-21-md-refactor-editorial-verification.md`

Применимые инструкции: `AGENTS.md` (project root), `CLAUDE.md` (project root), `_ops/AGENTS.md`.

## Цель

Завершить **P5 editorial verification** для `md_refactor_candidates` который остался partial (tested top-3 + top-5, не top-10). И ответить на captured finding: `md_refactor_candidates` bias — 3 из 5 top proposals → `platform-deltas.md` как owner, что указывает на signal weighting bias в `owner_detector.py`.

**Why now**: всё backend готово (P1-P8 done), profile coverage 100% LLM. Это последний шаг до полного «Tier 2 ready». Без editorial verification top-10 не можем claim что P5 met acceptance criteria.

## In scope

- Editorial verification: top-10 proposals от `md_refactor_candidates` на `knowledge/` corpus
- Manual review каждого: actionable / not-actionable / partial
- Если ≥5/10 actionable — P5 verification done, document
- Если <5/10 — signal weighting tuning в `owner_detector.py` (composite_score formula)
- Threshold tuning options: `uniqueness_threshold` (0.35 → 0.30?), `owner_confidence_threshold` (0.45 → 0.60?)
- Record results в `_ops/findings/` после editorial pass
- Update task-001 DoD checklist accordingly

## NOT in scope

- P7 cleanup (separate task, blocked on burn-in confirmation)
- Knowledge description cleanup (separate `knowledge-description-cleanup/` task)
- Backend code changes outside `owner_detector.py` and CLI thresholds
- Adding new MCP tools

## Definition of done

- 10 proposals reviewed manually, classified actionable/not/partial
- If signal good (≥5/10): document в `_ops/findings/` editorial verification result, mark P5 acceptance met
- If signal bad (<5/10): tune signals (composite weights OR thresholds), re-run, document iteration
- `md_refactor_candidates` bias finding (`_ops/findings/2026-05-21-...platform-deltas-bias.md` — auto-generated id) addressed: либо tuned, либо downgraded к «known limit»
- Task-001 status updated: P5 acceptance complete

## Stop rules

- 3+ tuning iterations без improvement — backend signal model нужен deeper rethink, escalate в `1strategy`
- User session time exhausted — document partial result, retake позже

## Подшаги

### S1 — Pre-flight check (5 min)

```bash
cd /Users/triton/Documents/GitHub/agentic-research/experiments/md-embedding-server/mcp
npm run smoke  # confirm 24/24
sqlite3 /Users/triton/Documents/GitHub/agentic-research/knowledge/.md-navigator/index.sqlite \
  "SELECT DISTINCT profile_model, COUNT(*) FROM sections WHERE profile_type IS NOT NULL GROUP BY profile_model;"
# Expected: anthropic/claude-haiku-4.5 | 300 (or close)
```

### S2 — Generate top-10 proposals (5 min)

Через MCP:
```
md_refactor_candidates({ corpus: "/path/to/knowledge", top: 10 })
```

Или CLI:
```bash
md_navigator.py refactor-candidates /path/to/knowledge --top 10 --json > /tmp/proposals-top10.json
```

### S3 — Editorial review (1-2 часа)

Для каждого из 10:

1. Read `affected_section` (path, heading) + `target_owner` (path, heading)
2. Open оба файла, read surrounding context
3. Decide:
   - **Actionable (replace_with_wikilink valid)** — affected section truly duplicates target's content, replacing с link improves IA
   - **Partial** — overlap есть но не 1:1, нужен extract или merge с modification
   - **Not actionable** — false positive (different subject, target wrong owner)
4. Note rationale в short notes

### S4 — Aggregate verdict (15 min)

- Count actionable / partial / not
- If actionable ≥5 → P5 acceptance met
- If actionable + partial ≥7 → marginal but acceptable
- If actionable <3 → signal не работает, нужно tuning

### S5 — Signal tuning (если нужно, 1-2 часа)

Common bias patterns to look for:

- **«All proposals → same target»** (e.g. platform-deltas): owner_detector.py composite weights too heavy на pagerank+in_degree относительно semantic alignment. Reduce graph weight, increase cosine + profile.type match weight.
- **«Top proposal correct, тлеть proposals noise»**: thresholds too loose. Raise `uniqueness_threshold` (filter out более unique sections) and/или `owner_confidence_threshold` (filter out weak owners).
- **«Profile type mismatch»** (e.g. uses → uses instead of uses → definition): owner ranking ignores profile.type fit; should boost candidates where target type ∈ {definition, rule}.

File: `experiments/md-embedding-server/scripts/navigator/owner_detector.py`. Function: `find_owner_candidates`. Composite formula:
```python
composite = (
    0.35 * cosine +
    0.30 * is_definition +
    0.15 * pagerank +
    0.10 * in_degree_norm +
    0.10 * confidence_prior
)
```

Tuning candidates:
- Cosine weight 0.35 → 0.45 (stronger semantic)
- Definition boost 0.30 → 0.35
- Pagerank weight 0.15 → 0.05 (reduce graph bias)
- In-degree 0.10 → 0.05
- Confidence 0.10 → 0.10 (keep)

### S6 — Re-verify after tuning (15 min)

```bash
md_navigator.py refactor-candidates /path/to/knowledge --top 10 --json > /tmp/proposals-top10-v2.json
```

Compare top-10 v1 vs v2. If improved → document tuning rationale, accept.

### S7 — Document results (15 min)

Write summary `_ops/findings/2026-MM-DD-md-refactor-editorial-verification.md`:
- Iteration count
- Final acceptance rate
- Bias finding addressed yes/no
- Signal weights final

Update `task-001-md-tools-unified-backend.md` Verification section: mark P5 acceptance state.

## Verification

- Top-10 reviewed
- Aggregate verdict documented
- Either ≥5/10 actionable OR tuning iteration shows improvement
- Bias finding closed or downgraded
- Task-001 P5 verification status updated

## Risks & mitigations

| Risk | Mitigation |
|---|---|
| Editorial session takes >2 hours user time | Cap at top-5 first, expand if signal looks good. Or split в две session |
| Tuning breaks signal на other corpora | Spike tuning на small corpus first. Verify не regression на existing acceptance |
| 3+ tuning iterations не improve | Escalate — может signal foundation wrong (composite не captures real owner-ness). `1strategy` для rethink |

## Anchors / Evidence

- Parent: `task-001-md-tools-unified-backend.md`
- Bias finding: `_ops/findings/2026-05-21-Claude Opus 4.7-36c3e6b6.md` (refactor candidates bias to platform-deltas)
- Composite signal source: `experiments/md-embedding-server/scripts/navigator/owner_detector.py`
- Editorial sample evidence: chat 2026-05-21 (top-3 review showed 2 plausible + 1 false-positive)
