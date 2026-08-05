---
description: "Self-contained non-leading briefs for fresh named Claude roles."
---

# Brief Templates

Read immediately before the first fresh `Agent` invocation.

## Brief Contract

Isolation and anti-priming invariants are owned by
[`Independence Boundary`](../SKILL.md#independence-boundary). Per-role zone,
falsifier and stake are derived in
[`Экспертная Юрисдикция`](../SKILL.md#экспертная-юрисдикция). This reference only
packages the resulting fields; it cannot relax either contract.

## Named Critic

```text
Решение: {owner decision this judgment may change}.
Текущий route: {what main intends to do and why; one factual sentence}.
Что проверить: {neutral question only this profession would ask in this form}.
Почему сейчас: {what changes downstream, stated in this role's own currency}.
Где смотреть: {this role's zone: exact raw paths where its falsifier would surface}.
Факты: {source-bound facts or none}. Неизвестно: {material gap}.
Границы: in — {scope}; out — {scope}; side effects — {none/read-only/etc.}.
Доступный local tool: {one relevant tool and its information job, or omit}.
```

Two briefs filled from this template must not be interchangeable between their
roles; if they are, the zones were never derived and the run buys one input
twice.

Select the profile through the native `Agent` tool's exact `subagent_type`. Do
not restate its native contract in the brief: a compressed recap of the
profession sits nearer than the role definition and the agent will answer the
recap instead of its own method.

## `auditor`

```text
Что заявлено готовым: {artifact/work/result}.
Условия приёмки: {exact user/task/owner conditions}.
Где проверять: {raw artifacts, diff, commands or evidence paths}.
Известное evidence: {outputs or none}. Неизвестно: {gaps}.
Границы: in — {scope}; out — {scope}; только чтение.
```

Do not suggest pass/fail statuses. The auditor owns its native acceptance
matrix and evidence kinds.

## `md-scout`

```text
Corpus: {root}. Только source-read-only.
Вопрос: {one retrieval question}.
Scope: {paths/includes/exclusions}.
Решение, которое зависит от packet: {owner decision}.
Факты: {source-bound facts or none}. Неизвестно: {gap}.
Вне scope: {boundary}. Relevant local route: {optional one-line hint}.
```

Scout returns addresses, actual coverage and gaps. It does not return a critic
verdict, and its packet does not by itself close the owner decision.
