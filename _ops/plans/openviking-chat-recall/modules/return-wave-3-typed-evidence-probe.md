---
kind: module-return
волна: 3
дата: 2026-08-21
---

# Return — typed-evidence probe

## Candidate и integration

- Writer task: `01a02465-8638-7d41-b1a5-8c91a9becd72`.
- Writer commit: `c3e5452`; integrated main commit: `9319f71`.
- Граница: 11 новых файлов только в
  `experiments/openviking-chat-recall/**`; source/plan/global skills не менялись.

## Independent deterministic evidence

Root после integration выполнил:

```bash
uv run --locked --project experiments/openviking-chat-recall \
  python -m unittest discover -s experiments/openviking-chat-recall/tests -v
uv run --locked --project experiments/openviking-chat-recall \
  python experiments/openviking-chat-recall/scripts/build_typed_probe.py \
  --manifest \
  experiments/openviking-chat-recall/artifacts/typed-gold-manifest.json \
  --output-dir "$(mktemp -d)"
```

Result: `Ran 5 tests ... OK`; cluster A — exact 4 records,
`2026-08-14T07:45:46.732000+00:00` → `2026-08-17T17:46:29+05:00`;
cluster B — exact 5 records, both frozen SHA confirmed. Separate temp rebuild was
byte-identical to committed typed input. `md check` returned `issues: []` for
all three typed-input and three offline-Wiki targets.

## Blind semantic evidence

Projectless task `01a0247f-3ee8-7480-87a2-4c0f963c9fae` видел только
snapshot из `index.md` и двух concept pages; repository, plan, gold,
holders, typed input, receipt, internet и git history были запрещены.

| Question | Blind answer | Verdict |
| --- | --- | --- |
| Recurrence | 4; exact first/latest; hit → full holder + later holders | PASS |
| Current outcome | Все 5 obligations с evidence records `:18`–`:22` | PASS |
| Stock/full corpus | Нет; offline projection, Compile blocked, evidence нет | PASS |

Reader confidence: `100%` по всем трём ответам. Final: semantic `PASS`.

## Split verdict

1. Deterministic evidence seam — **PASS**.
2. Official LLM Wiki prompt/IA на offline diagnostic — **semantic PASS** на
   двух кластерах; это не runtime export.
3. Stock OpenViking runtime/package route — **BLOCKED**: health/resource import
   работают, но Compile возвращает HTTP 400
   `include_integrity` SDK/VikingBot mismatch.

Общий full-corpus verdict: **не запускать**.

## Next decision

Рекомендован свой batch compiler: deterministic evidence layer + verified official
OpenViking LLM Wiki prompt/IA + rebuildable parallel folder. Это материально
отказывается от OpenViking runtime как готовой библиотеки, поэтому требует
отдельного approval владельца.
