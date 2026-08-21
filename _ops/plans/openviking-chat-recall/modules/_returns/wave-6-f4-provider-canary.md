---
kind: module-return
wave: 6
stage: F4-provider-canary
state: accepted-unknown
date: 2026-08-22
---

# Wave 6 F4 — synthetic provider canary

## Результат

Visible Luna Max task `01a02657-d943-7013-b1a6-36be71b59b68` построил
synthetic-only provider canary. Candidate `48798f2b2b022c5613d3468db36d80433e8a2024`
интегрирован в `main` как `c7ceed0`.

Terminal verdict — `UNKNOWN`. Одна real synthetic попытка была запущена;
автоматического или скрытого retry не было. Public receipt оставляет usage,
стоимость, nonce, route address и model event как `null`/unavailable, а не
выводит их из config или успешных fake tests.

## Причина UNKNOWN

Командный журнал task `01a02657-d943-7013-b1a6-36be71b59b68`, ordinals
369–422, фиксирует `CanaryError` после real-call path и пустой artifact root.
Pre-fix containment helper сравнивал absolute root с relative child и падал
до записи captured result/receipt. In-memory provider result не сохранился,
поэтому auth, exact nonce round-trip, actual model и usage не принимаются.

Текущий candidate исправляет сравнение через `root.absolute()` и
`child.absolute()`. Исходный UNKNOWN receipt остаётся неизменяемым evidence;
исправление не превращает первый вызов в PASS задним числом.

## Evidence

- exact ownership: `run_provider_canary.py`, его test и
  `artifacts/full-build/provider-canary/provider-canary-receipt.json`;
- envelope: `codex-cli 0.149.0-alpha.4.1`, `gpt-5.6-luna`, `max`, ephemeral,
  isolated temporary cwd, explicit output schema, JSON events, read-only
  sandbox, timeout 90 s;
- fake probes: success, one transient retry then success, terminal failure,
  timeout, request/usage accounting и redaction before provider boundary;
- receipt SHA-256
  `63b4f47dc0382cef49c5eae4efc11052f775b4bac7713e58b5fa7bca4cb57636`;
- public receipt validator и privacy/path scan — PASS;
- root full experiment suite — 59/59;
- root non-billable full-pipeline preflight с подменённым RealRun создал
  captured result, два renders и receipt для absolute и relative roots; оба
  verdict `PASS`.

Nested checker `01a02662-e49f-7523-a979-c664a2b38802/F4-nested-read-only`
атаковал pre-fix snapshot и вернул FAIL: zero-exit без addressable model event
мог выглядеть как PASS. Candidate теперь требует
`event_model == gpt-5.6-luna`; missing model event даёт `UNKNOWN`.

Independent Luna Max auditor `/root/f2_fast_audit` принял candidate только как
F4 UNKNOWN evidence. Разрешение на retry отклонено до трёх code repairs:

- все observed model events обязаны быть непротиворечивы; последовательность
  wrong model → expected model сейчас может дать ложный PASS;
- PASS требует addressable run/thread ID, а не `run_address=null`;
- public receipt и validator должны адресовать provider и real/fake retry
  policy отдельными полями.

## Frontier

F4 принят только как честное terminal UNKNOWN evidence. Wave 6 не получила
PASS, реальные holders provider-у не разрешены, Wave 6b закрыта. Следующий
разрешённый ход — отдельный F4-R1 после полного non-billable persistence
preflight и устранения трёх false-PASS seams; исходный F4 artifact root не
перезаписывается.
