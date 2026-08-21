---
kind: module-card
волна: 4
роль: read-only-runtime-analyst
модель: gpt-5.6-luna
thinking: max
---

# Модуль — LLM generation route

## Outcome

Найти минимальный уже доступный локальный route, который исполняет semantic
prompt пакетно без OpenViking runtime и поддерживает reproducibility, retry,
resume, bounded concurrency и безопасные receipts.

## Оркестрация

- Сначала вызвать `$1orchestration`.
- Внутренние субагенты раздельно проверяют local dependencies/config surfaces
  и provider/API contracts. Не выводить значения секретов.

## Ownership

- Read-only; никаких правок, коммитов и платного full-corpus запуска.
- Разрешены безопасные discovery/health checks без corpus payload, если они не
  создают billable workload.
- Не предлагать новую платформу, если существующий route удовлетворяет contract.

## Ответить

1. Какой provider/model route реально доступен из experiment без OpenViking?
2. Как фиксируются model, prompt digest, inputs, outputs, errors и retry state?
3. Как ограничить расход, параллелизм и blast radius; как resume избегает
   повторной оплаты?
4. Как тестировать generator через fake/fixture до реального sample call?

## Return

`THREAD_DONE` с проверенными entrypoints, dependency/config evidence, exact
secret-safe CLI/API contract, cost/retry/resume policy и falsifying smoke plan.
