---
kind: module-card
волна: 4
роль: read-only-researcher
модель: gpt-5.6-luna
thinking: max
---

# Модуль — corpus map и partition contract

## Outcome

Дать root проверяемую карту полного `_ops/chat-recall/`: объём, record schema,
аномалии, тематическое распределение и безопасный способ заморозить и разделить
corpus между будущими workers без пропусков и дублей.

## Оркестрация

- Сначала вызвать `$1orchestration`.
- Запустить минимум двух внутренних субагентов на непересекающихся диапазонах
  holders; агрегатор проверяет границы и расхождения.
- Все внутренние задачи read-only.

## Ownership

- Репозиторий read-only; никаких правок, коммитов и plan edits.
- Не один в кодовой базе: игнорировать чужие незакоммиченные изменения и не
  считать их своим output.
- Читает `_ops/chat-recall/**`, текущий inventory builder и его receipts.

## Ответить

1. Какой exact snapshot contract замораживает tracked и task-relevant untracked
   holders без зависимости от текущего dirty tree?
2. Сколько files/records реально парсится; какие schema/metadata anomalies и
   дубли есть?
3. Какая partition key даёт file-disjoint, примерно равные semantic workers и
   сохраняет chronology одного кластера?
4. Какие machine-readable manifests нужны для coverage и resume?

## Return

`THREAD_DONE` с командами, counts, адресами anomalies, рекомендуемыми manifest
schemas и partition plan. Self-report без команд/выборки не является evidence.
