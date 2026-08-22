---
kind: module-return
wave: 6
stage: F4-R1-provider-canary
state: rejected-unknown
date: 2026-08-22
---

# Wave 6 F4-R1 — provider canary repair

## Verdict

Visible Luna Max task `01a02681-32dd-7de1-8d4c-014972769587` выполнил один
synthetic-only `codex exec`; automatic retry не было. Process завершился
`provider_error/nonzero_exit` до parseable JSON events. Model signals, run
address и usage отсутствуют, поэтому terminal runtime evidence — `UNKNOWN`.

Repair candidate `84cda7fa3e8a160cc435dc7f566f545bed49738f` →
`5bfbffbeb01fa8ed480bceb9d1ab30827fd86781` →
`9b1cdafe27837e31b24ab79b32a26d995be98aea` отклонён и не интегрирован.
Accepted original F4 receipt на `c7ceed0` остаётся неизменяемым owner evidence.

## Direct evidence

- candidate write-set: только `run_provider_canary.py`,
  `test_provider_canary.py` и
  `provider-canary-r1/provider-canary-receipt.json`;
- original F4 receipt SHA-256:
  `63b4f47dc0382cef49c5eae4efc11052f775b4bac7713e58b5fa7bca4cb57636`;
- candidate R1 receipt SHA-256:
  `ca0c7bedd4b6f94e8382b8deebc973486eea11891e051177f6681d1a3cadd775`;
- оба artifact validator-а — PASS; targeted tests — 32/32; full experiment
  suite — 75/75;
- R1 runtime facts: one attempt/request, no automatic retry,
  `event_line_count=0`, `model_signals=[]`, `run_address=null`, `usage=null`;
- follow-up repairs не выполняли новый provider/Codex call.

## Rejection evidence

Independent auditor `/root/f4r1_final_acceptance` вернул `FAIL` по двум
исполняемым false-PASS probes:

- v2 validator принимал `usage_status=addressable` при
  `real_call.usage=null`;
- v2 validator принимал `real_call.request_count=2`, хотя contract разрешает
  ровно один request без retry.

Следовательно, green tests и validator не доказывают fail-closed PASS gate.
Candidate не становится live code, а observed provider outcome не
переклассифицируется задним числом.

## Trajectory decision

Fresh Eyes показал, что дальнейший zero-network/provider repair не измеряет
пользу Wiki. Следующий разрешённый ход — детерминированный representative
input-lock из F1–F3. Semantic provider не получает реальные holders; любая
будущая provider-попытка требует новой root-card и обязана начать с двух
false-PASS probes выше.
