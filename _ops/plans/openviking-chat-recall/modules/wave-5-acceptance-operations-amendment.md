---
kind: module-card
wave: 5
state: superseded-before-write
role: acceptance-operations-writer
model: gpt-5.6-luna
thinking: max
---

# Модуль — case-isolated acceptance operations amendment

[parent: task.md](../task.md) · superseded by post-ingestion utility gate

## Contribution

Эта карточка сохраняет диагностированный operations defect первого blind run,
но больше не является исполнимым gate перед Wave 6. Case-isolation и typed
measurements переносятся в Wave 6b, где reader проверяет настоящий
representative L2/L1/L0 route. Frozen questions, expected semantic criteria,
forbidden claims и hard semantic failures v1 не меняются.

## Inputs

- `artifacts/distilled-acceptance.json` как immutable semantic gold;
- exact line/word/byte measurements двух frozen holders;
- topology первого запуска и независимый verdict только как список protocol
  defects, не как источник правильных candidate answers.

Не читать generated Wiki, raw reader packets, probe manifest/receipt или source
answers при выборе thresholds.

## Ownership

Отменённый writer должен был менять только:

- `experiments/openviking-chat-recall/artifacts/distilled-acceptance-operations-v2.json`.

Read-only critic не пишет файлов. Ни один operations-v2 artifact этой карточки
не интегрируется; новый contract принадлежит Wave 6b.

## Required contract

- Десять независимых runs: пять cases × Wiki/holder arm; fresh context на run.
- Один question/model/answer schema на matched pair; поверхности различаются
  только заранее объявленным arm route.
- V1 semantic criteria остаются byte-addressable и не копируются с изменениями.
- Для каждого case/arm: allowed files/records, max typed reads, context/answer
  budget, required report fields, abstain/route expectation и hard failures.
- Holder budget выводится из frozen source measurements и не требует невозможной
  полной read при лимите меньше самого holder-а.
- Reader elapsed, top-level orchestration wall time, tokens, bytes и typed reads
  считаются отдельно; одно измерение не подменяет другое.
- Grader имеет доступ к frozen semantic gold и source evidence; reader — нет.

## Falsifying checks

- amendment меняет вопрос или semantic expected/forbidden text — fail;
- два cases делят reader context — fail;
- Wiki arm должен дать full history вместо abstain/holder route — fail;
- holder arm оценивается по projection-read limit или наоборот — fail;
- обязательное поле нельзя получить из разрешённой поверхности — fail;
- threshold зависит от candidate packet/answer — fail;
- aggregated elapsed скрывает orchestration latency — fail.

## Return

Исторический writer обязан вернуть отсутствие принятого commit либо exact
disposable worktree paths. Матрица critic остаётся evidence того, почему первый
run нельзя считать utility proof. Следующий case-isolated rerun принадлежит
Wave 6b и не наследует candidate-derived thresholds этой карточки.

## Prohibitions

Не менять v1 gold, candidate Wiki/probe, holders, plan/status или full-build
cards; не ослаблять semantic acceptance ради зелёного результата.
