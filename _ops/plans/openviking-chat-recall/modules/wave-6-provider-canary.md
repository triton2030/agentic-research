---
kind: module-card
wave: 6
stage: F4
state: planned
role: synthetic-provider-canary
model: gpt-5.6-luna
thinking: max
---

# Модуль — F4 synthetic provider canary

[parent: task.md](../task.md) · gate: before any real holder egress

## Contribution

Выбрать и проверить один semantic execution envelope для Wave 6b: auth,
synthetic-only egress, timeout/retry, logging, secret redaction и cost/usage
accounting. F4 не читает F2 private records или holders и не генерирует Wiki.

## Dependency

Pinned OpenViking prompt/IA/model tuple и accepted Wave 4b execution seam.
F1–F3 могут быть приняты независимо, но Wave 6 получает PASS только после F4.

## Ownership

Один visible Luna Max writer с nested read-only checker владеет только:

- `experiments/openviking-chat-recall/scripts/run_provider_canary.py`;
- `experiments/openviking-chat-recall/tests/test_provider_canary.py`;
- `experiments/openviking-chat-recall/artifacts/full-build/provider-canary/**`.

Plan/status, holders, F1–F3, prompts, Wiki и semantic artifacts read-only.

## Execution contract

1. Fixture/fake adapter deterministically доказывает timeout, один transient
   retry, terminal failure, request counting, usage aggregation, log schema и
   redaction до любой записи receipt.
2. Один real synthetic call использует `gpt-5.6-luna` / `max` через выбранный
   `codex exec` public envelope и output schema. Он получает только публичный
   nonce и уже redacted payload; raw secret canary не входит в provider input.
3. Receipt фиксирует CLI/provider/model/thinking, command/config digests,
   attempts, status, elapsed, usage/token accounting, retry policy и output
   digest. Полный prompt/transcript, env, credentials и raw secret запрещены.
4. Тот же accepted envelope становится обязательным input Wave 6b. Route или
   model drift инвалидирует receipt.

## PASS

PASS возможен только если одновременно:

- real call доказывает auth и exact structured nonce round-trip;
- public logs/receipt содержат redacted marker и не содержат raw canary;
- fake tests доказывают timeout/retry/failure и deterministic accounting;
- реальный route выдаёт адресуемый usage/cost receipt. Если provider surface
  не раскрывает нужный usage signal, verdict — `UNKNOWN`, не ноль;
- два receipt builds с frozen captured provider result byte-identical;
- ни один holder/F2 path не был открыт или передан provider-у.

## Falsifiers

- реальный holder/quote попал в prompt, log или receipt;
- raw canary, credential name/value, env dump или transcript сохранён;
- auth доказан только config inspection, а не completed call;
- retry/timeout/cost заявлены без fake или real receipt;
- model/thinking/CLI version нельзя адресовать;
- live network response используется как deterministic test fixture без
  captured digest;
- UNKNOWN превращён в PASS или нулевую стоимость.

## Return

Full commit SHA, exact paths, selected envelope, synthetic task/run address,
auth/egress/retry/timeout/redaction/usage matrix, tests, public receipt digest,
nested receipt и terminal `PASS | FAIL | UNKNOWN`. Только PASS открывает 6b.
