---
type: entity
title: Как владелец запускает Ox Alpha через Hermes?
description: "Позиция: Ox Alpha живёт в 1hermes через Hermes harness без отдельного скила, провайдер — Nous, гейт zero-pricing без fallback, использование только пока модель бесплатна."
topic: hermes
---
# Как владелец запускает Ox Alpha через Hermes?

Ox Alpha запускается через Hermes harness силами `1hermes`; отдельный скил для неё владелец создавать не стал. Основной провайдер — `Nous`: ошибочный OpenRouter-only gate решено удалить, допуск определять по subscription/free semantics в Nous Portal, а контракт `Ox Alpha` держит provider-specific zero-pricing gate без fallback и со strict resume identity. Саму модель используют только пока она бесплатна.

## Harness и отдельный скил

- Владелец решил развивать `1hermes` для запуска `Ox Alpha` через Hermes harness и не создавать отдельный скил. [решил: Ox Alpha через Hermes harness, без отдельного скила](../../../../../_ops/chat-recall/2026-08-22-063718-codex-01a0271b.md#L21), [решил: Ox Alpha через Hermes harness, без отдельного скила](../../../../../_ops/chat-recall/2026-08-22-063718-codex-01a0271b.md#L22)

## Провайдер и допуск

- Владелец решил сделать `Nous` основным провайдером `Ox Alpha`, удалить ошибочный OpenRouter-only gate и определять допуск по subscription/free semantics в Nous Portal. [решил: Nous — основной провайдер, допуск по семантике Nous Portal](../../../../../_ops/chat-recall/2026-08-22-063718-codex-01a0271b.md#L27), [решил: Nous — основной провайдер, допуск по семантике Nous Portal](../../../../../_ops/chat-recall/2026-08-22-063718-codex-01a0271b.md#L27), [решил: Nous — основной провайдер, допуск по семантике Nous Portal](../../../../../_ops/chat-recall/2026-08-22-063718-codex-01a0271b.md#L24)

## Гейт и resume identity

- Владелец решил применять provider-specific zero-pricing gate, не использовать fallback и сохранять strict resume identity в контракте `Ox Alpha`. [решил: provider-specific zero-pricing gate и strict resume identity](../../../../../_ops/chat-recall/2026-08-22-063718-codex-01a0271b.md#L24)

## Лимиты подписки

- Владелец решил, что лимиты подписки Nous Portal не должны сдерживать вызовы Hermes: агент сам вызывает Hermes при необходимости. [решил: лимиты подписки не сдерживают вызовы Hermes](../../../../../_ops/chat-recall/2026-08-06-113200-claude-712763b3.md#L24)

## Бесплатность

- Владелец поправил, что `Ox Alpha` используется только пока она бесплатна, а при переходе на платный режим её нужно сразу отключать. [поправил: Ox Alpha только пока бесплатна](../../../../../_ops/chat-recall/2026-08-22-063718-codex-01a0271b.md#L24), [поправил: Ox Alpha только пока бесплатна](../../../../../_ops/chat-recall/2026-08-22-063718-codex-01a0271b.md#L24)

## Маршрут к документации

- Владелец поправил маршрут к Hermes: в его документации есть более подходящий для Claude путь. [поправил: маршрут к Hermes по пути для Claude](../../../../../_ops/chat-recall/2026-08-06-113200-claude-712763b3.md#L21)

## Источники

- [решил: Ox Alpha через Hermes harness, без отдельного скила](../../../../../_ops/chat-recall/2026-08-22-063718-codex-01a0271b.md#L21)
- [решил: Ox Alpha через Hermes harness, без отдельного скила](../../../../../_ops/chat-recall/2026-08-22-063718-codex-01a0271b.md#L22)
- [решил: Nous — основной провайдер, допуск по семантике Nous Portal](../../../../../_ops/chat-recall/2026-08-22-063718-codex-01a0271b.md#L27)
- [решил: Nous — основной провайдер, допуск по семантике Nous Portal](../../../../../_ops/chat-recall/2026-08-22-063718-codex-01a0271b.md#L27)
- [решил: Nous — основной провайдер, допуск по семантике Nous Portal](../../../../../_ops/chat-recall/2026-08-22-063718-codex-01a0271b.md#L24)
- [решил: provider-specific zero-pricing gate и strict resume identity](../../../../../_ops/chat-recall/2026-08-22-063718-codex-01a0271b.md#L24)
- [решил: лимиты подписки не сдерживают вызовы Hermes](../../../../../_ops/chat-recall/2026-08-06-113200-claude-712763b3.md#L24)
- [поправил: Ox Alpha только пока бесплатна](../../../../../_ops/chat-recall/2026-08-22-063718-codex-01a0271b.md#L24)
- [поправил: Ox Alpha только пока бесплатна](../../../../../_ops/chat-recall/2026-08-22-063718-codex-01a0271b.md#L24)
- [поправил: маршрут к Hermes по пути для Claude](../../../../../_ops/chat-recall/2026-08-06-113200-claude-712763b3.md#L21)
