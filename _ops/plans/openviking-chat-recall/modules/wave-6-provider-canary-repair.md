---
kind: module-card
wave: 6
stage: F4-R1
state: rejected-unknown
role: synthetic-provider-canary-repair
model: gpt-5.6-luna
thinking: max
---

# Модуль — F4-R1 provider canary repair

[parent: task.md](../task.md) · dependency: accepted F4 UNKNOWN return

## Contribution

Исправить persistence boundary и три найденных false-PASS seam, затем выполнить
один новый synthetic-only Luna Max call и получить долговечный terminal
receipt. F4-R1 не исправляет и не заменяет исходный F4 UNKNOWN; он создаёт
отдельное evidence в новом artifact root.

## Execution result

Visible Luna Max task `01a02681-32dd-7de1-8d4c-014972769587` выполнил один
synthetic-only call. Он завершился `provider_error/nonzero_exit` до parseable
JSON events: model, run address и usage не наблюдались, automatic retry не
было. Terminal evidence поэтому остаётся `UNKNOWN`, а не `FAIL` или `PASS`.

Трёхкоммитный repair candidate `84cda7f → 5bfbffb → 9b1cdaf` не интегрирован.
Независимый acceptance-аудит нашёл два оставшихся false-PASS: validator
принимал `usage_status=addressable` при `usage=null` и
`real_call.request_count=2`. Исходный F4 receipt и accepted `UNKNOWN` на
`c7ceed0` остаются единственным live evidence этой ветки.

После Fresh Eyes дальнейший CLI/provider repair снят с текущей траектории:
он не доказывает semantic utility Wiki. Любая будущая provider-попытка требует
новой root-card, отдельного falsifier-а для этих двух seam и не может
перезаписывать F4/F4-R1 receipts.

## Ownership

Один visible Luna Max writer с nested read-only checker владеет только:

- `experiments/openviking-chat-recall/scripts/run_provider_canary.py`;
- `experiments/openviking-chat-recall/tests/test_provider_canary.py`;
- `experiments/openviking-chat-recall/artifacts/full-build/provider-canary-r1/**`.

`provider-canary/**`, holders, F1–F3, plan/status, prompts и semantic artifacts
read-only. Nested checker не запускает provider и не пишет в owned paths.

## Required code repair

До полного preflight writer обязан закрыть три independent-audit blocker-а:

1. Parser сохраняет все observed model signals. PASS разрешён только если
   непустой набор равен `{gpt-5.6-luna}`; любой другой model signal даёт FAIL,
   даже если последний event снова называет Luna. Missing model остаётся
   UNKNOWN.
2. PASS требует безопасный addressable run/thread ID из реального event stream.
   Completed nonce/model/usage с `run_address=null` не является PASS.
3. Public receipt и validator получают отдельные addressable поля `provider`
   и `retry_policy`: fake transient maximum — один retry, real canary — zero
   retry и ровно один request.

Обязательные negative tests: wrong → expected model, expected → wrong model,
missing run/thread ID, missing/wrong provider и missing/wrong retry policy.

## Mandatory non-billable preflight

До real call writer обязан:

1. Добавить end-to-end test через public canary boundary с fake Codex binary:
   version probe, one JSON event stream, exact nonce, addressable model/usage,
   relative artifact root и полный captured-result → two renders → receipt
   pipeline.
2. Повторить pipeline с absolute artifact root и из другой cwd. Оба build
   обязаны пройти validator и дать четыре expected owned files без unrelated
   cleanup.
3. Сохранять sanitized captured result сразу после возврата provider и до
   derived receipt. Запись owned JSON должна быть atomic внутри того же root;
   symlink/path escape остаётся fail closed.
4. Доказать executable call-count: fake full pipeline — один provider
   subprocess; real path не имеет automatic retry.
5. Пройти targeted tests, полный experiment suite, privacy/path scan и
   независимый nested review, включая все Required code repair falsifiers.
   Любой preflight FAIL/UNKNOWN запрещает real call.

## One-call execution

После полного preflight разрешён ровно один новый `codex exec` call через тот
же pinned envelope: `gpt-5.6-luna` / `max`, ephemeral, isolated temp cwd,
explicit output schema, JSON events, read-only sandbox, timeout 90 s. Provider
получает только public nonce и redacted synthetic payload. Результат пишется в
`provider-canary-r1/**`; исходный F4 receipt не открывается для записи.

## Terminal verdict

- `PASS`: completed auth, exact nonce, actual model event
  `gpt-5.6-luna`, addressable token usage, saved sanitized capture, two
  byte-identical renders и clean privacy scan.
- `FAIL`: wrong model, secret/path leak, non-exact output, schema drift или
  нарушенный single-call contract.
- `UNKNOWN`: timeout, missing model/usage, provider ambiguity или новый
  persistence gap. UNKNOWN не равен нулевой стоимости и не разрешает retry.

После одного вызова дальнейшие automatic repairs запрещены. Любой следующий
provider call требует новой root-карточки и сохраняет все прежние receipts.

## Return

Full SHA, exact paths, preflight commands/results, one-call address/status,
auth/egress/model/usage/redaction matrix, artifact digests, nested receipt и
terminal `PASS | FAIL | UNKNOWN`. Только independently accepted PASS закрывает
Wave 6 и открывает representative Wave 6b.

## Principles trace

P-004/P-005 требуют наблюдаемой цепочки вместо вывода из тестов; поэтому
потерянный result остаётся UNKNOWN. P-007 дополняет существующий F4 owner:
новый root хранит repair evidence, а исходный receipt не перезаписывается.
