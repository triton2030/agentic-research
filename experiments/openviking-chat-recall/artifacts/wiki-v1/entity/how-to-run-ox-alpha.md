---
type: entity
title: Как запускать Ox Alpha через Hermes?
description: Провайдер Nous, provider-specific zero-pricing gate без fallback, strict resume identity и лимиты подписки не сдерживают вызовы
topic: hermes
---
# Как запускать Ox Alpha через Hermes?

`1hermes` развивается для запуска `Ox Alpha` через Hermes harness; отдельный скил для этого не создаётся. `Nous` — основной провайдер `Ox Alpha`: ошибочный OpenRouter-only gate удалён, а допуск определяется по subscription/free semantics в Nous Portal. Применяется provider-specific zero-pricing gate без fallback и со strict resume identity в контракте `Ox Alpha`. Лимиты подписки Nous Portal не должны сдерживать вызовы Hermes: агент сам вызывает Hermes при необходимости.

## Решения

- Владелец решил развивать `1hermes` для запуска `Ox Alpha` через Hermes harness и не создавать отдельный скил. [решение о развитии 1hermes](../../../../../_ops/chat-recall/2026-08-22-063718-codex-01a0271b.md#L21) [вторая опора решения о развитии 1hermes](../../../../../_ops/chat-recall/2026-08-22-063718-codex-01a0271b.md#L22)
- Владелец решил сделать `Nous` основным провайдером `Ox Alpha`, удалить ошибочный OpenRouter-only gate и определять допуск по subscription/free semantics в Nous Portal. [решение о провайдере Nous](../../../../../_ops/chat-recall/2026-08-22-063718-codex-01a0271b.md#L26) [решение об удалении OpenRouter-only gate](../../../../../_ops/chat-recall/2026-08-22-063718-codex-01a0271b.md#L27) [решение о допуске через Nous Portal](../../../../../_ops/chat-recall/2026-08-22-063718-codex-01a0271b.md#L28)
- Владелец решил применять provider-specific zero-pricing gate, не использовать fallback и сохранять strict resume identity в контракте `Ox Alpha`. [решение о zero-pricing gate](../../../../../_ops/chat-recall/2026-08-22-063718-codex-01a0271b.md#L28)
- Владелец решил, что лимиты подписки Nous Portal не должны сдерживать вызовы Hermes: агент сам вызывает Hermes при необходимости. [решение о лимитах подписки](../../../../../_ops/chat-recall/2026-08-06-113200-claude-712763b3.md#L24)

## Источники
- [решение о развитии 1hermes](../../../../../_ops/chat-recall/2026-08-22-063718-codex-01a0271b.md#L21)
- [вторая опора решения о развитии 1hermes](../../../../../_ops/chat-recall/2026-08-22-063718-codex-01a0271b.md#L22)
- [решение о провайдере Nous](../../../../../_ops/chat-recall/2026-08-22-063718-codex-01a0271b.md#L26)
- [решение об удалении OpenRouter-only gate](../../../../../_ops/chat-recall/2026-08-22-063718-codex-01a0271b.md#L27)
- [решение о допуске через Nous Portal](../../../../../_ops/chat-recall/2026-08-22-063718-codex-01a0271b.md#L28)
- [решение о zero-pricing gate](../../../../../_ops/chat-recall/2026-08-22-063718-codex-01a0271b.md#L28)
- [решение о лимитах подписки](../../../../../_ops/chat-recall/2026-08-06-113200-claude-712763b3.md#L24)
