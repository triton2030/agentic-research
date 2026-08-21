---
kind: module-return
волна: 4
статус: root-verified-partial
verified: 2026-08-21
---

# Return — verified contracts Wave 4

## Root-verified evidence

- Baseline `47e7179` содержит `180` holder Markdown без `README.md` и `1072`
  records. Проверено `git ls-tree` и `git grep '^\* '`.
- Committed `artifacts/source-inventory.json` stale: `count=182`, а
  `source_dir` указывает на worktree `b156`; current snapshot owner им быть не
  может.
- Typed-evidence tests проходят `5/5`: frozen Git refs, exact membership,
  reproducible output и fail-closed SHA/record drift.
- OpenViking LLM Wiki Skill на current `2af48624…` и pinned `499995f3…`
  одинаково владеет L2 typed pages и `index.md`, запрещает source-by-source
  pages и запрещает Wiki-agent создавать `.abstract.md`/`.overview.md`.
- OpenViking core `docs/en/concepts/03-context-layers.md` отдельно владеет
  L0/L1/L2, directory sidecars, token budgets и bottom-up generation.
- Host `codex-cli 0.149.0-alpha.4` имеет `exec --ephemeral --json
  --output-schema --sandbox -o`; standalone semantic call, auth, cost и logging
  не проверены.

## Принятые seams

1. Canonical input — content-addressed snapshot. Absolute/live path только
   diagnostic; record identity включает canonical relative `path:line` и
   content digest.
2. Deterministic layer единолично владеет membership, count, first/latest,
   chronology и provenance; semantic output не может их исправлять.
3. Upstream provenance разделён: `wiki_l2` и `context_layers_l0_l1` имеют
   отдельные refs/digests/prompts/validators.
4. Pipeline: snapshot → records → cluster proposal → deterministic facts → L2
   generation/validation → bottom-up L0/L1 → mechanical validation → publish;
   resume/receipts окружают каждый stage.
5. Snapshot и egress policy — fail-closed gates до semantic generation. Derived
   Wiki остаётся удаляемой projection.
6. CLI, schemas/contracts, dependency lock, README и published manifest — hot
   files одного writer. Stage modules и tests могут быть file-disjoint только
   после freeze contracts.
7. Acceptance расширяет locked Wave 1: 11 immutable questions, same budgets,
   no-gold abstention, chronology/currentness и matched Wiki-vs-holders run.

## Не принято как evidence

- Self-report внутренних субагентов без terminal packet.
- Exact anomaly counts, semantic clusters и retrieval benefit полного corpus.
- `codex exec` как рабочий provider route до fixture smoke и privacy/auth gate.
- Stock OpenViking runtime как implementation dependency.

## Gaps → Wave 4b

- Exact L0/L1 prompt templates, schemas, pinned/current drift и reuse boundary.
- One non-duplicating output topology для L2 Wiki + directory L0/L1.
- Разделение current Luna worktree production и future reusable CLI adapter.

## Terminal source tasks

- Corpus: `01a0248f-9a1b-71d0-ac76-9c9247e0d23d`.
- Compiler seam: `01a0248f-9a14-7a53-877a-56a4f0acb12a`.
- Wiki prompt/IA: `01a02490-90e6-7a71-8120-8451f7ad4016`.
- LLM route: `01a0248f-9a1b-71d0-ac76-9c52161efcf2`.
- Acceptance: `01a0248f-9a14-7a53-877a-568219d57716`.
- Privacy/recovery: `01a0248f-9a1b-71d0-ac76-9c7d8ac02686`.
