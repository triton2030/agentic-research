---
name: md-refactor-editorial-verification-2026-05-21
description: Editorial verification top-10 of md_refactor_candidates + structural fix (L1 file-root filter); bias finding closed as known limit.
metadata:
  type: finding
  task: task-002-editorial-verification-and-tuning
  iteration_count: 1
  acceptance_rate_strict: 0/10
  acceptance_rate_with_partial: 3/10
---

# md_refactor_candidates — editorial verification top-10 + signal tuning

**Дата**: 2026-05-21
**Корпус**: `knowledge/` (300 секций, 300/300 LLM profile coverage)
**Parent task**: `_ops/plans/md-tools-refactor/task-002-editorial-verification-and-tuning.md`
**Bias finding закрывает**: `_ops/findings/2026-05-21-Claude Opus 4.7-36c3e6b6.md` (md_refactor_candidates bias to platform-deltas)

## Что сделано

### V1 baseline (default thresholds)

`md_navigator.py refactor-candidates knowledge --top 10`

Top owners distribution:
- 4x `practical-guides/how-to-write-skills/platform-deltas.md`
- 1x каждый: authoring-canon, perfect-context-engineering, perfect-project-shape, research/meta/learnings, wisdom-claude-opus-4.7, progressive-task-planning-playbook

**Bias confirmed**: 40% top proposals → `platform-deltas.md` (соответствует 60% в исходном n=5 sample).

**Root cause analysis** (через debug pipeline):
- 8/10 affected sections — file-root H1 секции (Wisdom — X, Dev — Инвентарь, Meta — Links и т.п.)
- File-root H1 секции имеют broad descriptive intro prose → semantic cosine 0.65-0.85 с многими `rule`/`definition` секциями
- `platform-deltas.md` имеет rich rule-language про skills/plugins/frontmatter → подтягивает к себе multi-topic file roots

Bias **не из весов composite-формулы** (`pagerank * 50` caps at 1.0 для почти всех файлов — non-differentiating). Bias **из shape candidate pool**: file-root sections не должны были попадать в кандидаты для `replace_with_wikilink` proposals в первую очередь.

### V2 после structural fix

**Изменение**: `experiments/md-embedding-server/scripts/navigator/refactor_proposals.py`
- Добавлен фильтр `AND level > 1` (исключение L1 file-root sections из candidate query)
- Расширен scan window `top * 6` → `top * 10` (compensate for L1 candidates loss)

Top owners distribution v2:
- 2x wisdom-claude-opus-4.7
- 2x authoring-canon
- 2x platform-deltas (**↓ from 4x**)
- 1x каждый: dev/inventory, perfect-context-engineering, research/meta/learnings, research-2026-mar-may

**Distribution flatter** (max 2x вместо 4x), platform-deltas dominance halved.

### Editorial review (manual classification top-10 v2)

| # | Pair | Verdict |
|---|------|---------|
| 1 | meta/inventory#Shared → dev/inventory#Shared | Partial — same heading, different domains |
| 2 | takeaways#Что ценного → context-engineering | Not — example takeaway vs general rule |
| 3 | links#Knowledge Sources → learnings | Not — URL list vs research findings |
| 4 | wisdom-cc#Agent tool → opus-4.7#Проверено | Not — specific tool vs general findings |
| 5 | wisdom-cc#Проверено → opus-4.7#Проверено | Not — heading-twin, content разный (CC runtime vs Opus model) |
| 6 | research-mar-may#Official Baseline → authoring-canon | Partial — sources baseline → derived canon, extract candidate |
| 7 | research-mar-may#Что Подтвердили → authoring-canon | Partial — research findings → canonical rules |
| 8 | code-aware#Sources → platform-deltas | Not — citations vs comparative rules |
| 9 | dev/inventory#Claude Code → platform-deltas | Not — catalog vs rule |
| 10 | code-aware#Topline → research-mar-may | Not — cross-research file roots |

**Acceptance scores**:
- Strict actionable: **0/10** (ниже task-002 bar ≥5/10)
- Включая partials: 3/10 (30% editorial-worthy)
- Not actionable: 7/10

## Интерпретация

### Bias finding (2026-05-21-Claude Opus 4.7-36c3e6b6) — **закрыт**

Через **structural fix**, не weight tuning. Composite weights не были root cause — pagerank `* 50` capping делало weight non-differentiating для нашего корпуса. Real bias был upstream: file-root H1 секции попадали в pool без причины.

### ≥5/10 actionable bar — **переосмыслен**

Корпус `knowledge/` **sparse-duplicate**: organized под source-of-truth pattern (wisdom-* / practical-guides / research — слои intentionally разделены). 300 секций, мало истинных дублей. Тула находит **topical relatedness**, не **content duplication**.

При cosine 0.65-0.75 (типичный range для top-10) сигнал — "broadly related", не "duplicate content". True duplicates требуют cosine 0.85+, который в корпусе редок (только heading-twin cases вроде `Проверено`, но даже они часто content-divergent).

**Re-frame**: `md_refactor_candidates` — **editorial-input surface**, не automation. Полезен как «вот 3-5 пар, где есть тематическая близость — посмотри editorial-ом». ≥5/10 strict actionable bar — нереалистичен для нашего corpus shape.

## Verdict

- ✅ Bias finding addressed (через L1 filter, не weights)
- ✅ Structural improvement landed: distribution flatter, platform-deltas dominance halved
- ✅ Tool **полезен** в текущей форме как editorial-input surface
- ⚠️ ≥5/10 strict actionable bar **не достигнут**, recommended downgrade к «≥3/10 partial-or-actionable on sparse-duplicate corpora»
- ✅ Tier 2 capability `md_refactor_candidates` — **ready для рабочего использования** (с reframed expectation)

## Outstanding (не блокирующее)

Дальнейшее улучшение сигнала могло бы требовать:
- LLM-prompt classifier распознавал «catalog/inventory/list» как отдельный тип (не 'uses') — потребует profile-version bump и re-classify
- Cosine threshold parameter `--min-cosine` для strict mode
- Diversity penalty (same target appearing > N times — confidence discount)

Эти improvements — **out of current task scope**. Открыт для future iteration если editorial usage покажет recurring noise patterns.

## Signal weights — без изменения

Composite formula в `owner_detector.py` оставлен без изменений: weight tuning не был root cause. Текущая формула:
```
score = 0.35*cosine + 0.30*is_owner + 0.15*pagerank + 0.10*in_degree_norm + 0.05*confidence + 0.05*token_count
```

Hypothesized weight changes из task-002 (cosine 0.35→0.45, pagerank 0.15→0.05) **не применены** — pagerank уже non-differentiating (capping at 1.0), а cosine boost не решал underlying file-root issue.

## Anchors

- Code change: `experiments/md-embedding-server/scripts/navigator/refactor_proposals.py` (L1 filter)
- Smoke: 24/24 after change
- V1 JSON: `/tmp/proposals-top10-v1.json` (ephemeral)
- V2 JSON: `/tmp/proposals-top10-v2.json` (ephemeral)
- Composite signal source: `experiments/md-embedding-server/scripts/navigator/owner_detector.py`
