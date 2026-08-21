---
kind: module-return
wave: 5
state: fail
grader: file_matched_grader
packets: wave-5-blind-reader-packets.json
---

# Return — Wave 5 matched grader

## Verdict

Representative G0 behavior: **FAIL**. Usefulness: **not proven**.

## Что прошло

- Оба arms не выдали `latest` за current и не придумали unsupported fact.
- Wiki arm ответил на stable knowledge и abstain/route для currentness,
  conflict, history и no-gold.
- Holder arm восстановил prior/later для history и abstain-ил там, где frozen
  records не содержали policy.
- Поверхности не смешались: Wiki читал только generated Wiki, holder arm —
  только два frozen holders.

## Blockers

- Один reader ответил на пять cases после общего чтения всей поверхности;
  locked budgets и must-report fields принадлежат отдельному case.
- Wiki Q1 не сообщил applicability/lifecycle; Wiki Q4 превысил лимит одной
  projection read; source routes нескольких cases неполны.
- Holder Q1 не дал stable record path, Q2 превысил context budget; reporting
  schema не содержит все case-specific fields.
- Semantic gold не разделяет ожидания Wiki arm и holder arm: history-arm Wiki
  должен abstain/route, а holder arm — читать prior/later evidence.
- Wiki сообщил около 650 context tokens против 2500 у holders, но task wall
  latency 478170 ms против 231127 ms и reads 5 против 2. Экономия tokens сама
  по себе не закрывает usefulness threshold.

## Следствие

Semantic criteria и forbidden claims остаются frozen. Нужна отдельная
operations amendment: per-case isolation, arm-specific expectations,
must-report schema и сопоставимые измерения. Её нельзя настраивать по ответам
candidate; входы — locked v1 и измеренная физика source surfaces.
