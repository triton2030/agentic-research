---
type: entity
title: Из каких источников 1mantine-dev берёт знания о Mantine?
description: Внутри — карта «симптом → help.mantine.dev» и лестница размещения; снаружи — llms.txt и help.mantine.dev по URL, официальные носители пока не ставятся.
topic: mantine
---
# Из каких источников 1mantine-dev берёт знания о Mantine?

Ядро источников — две оставленные reference: карта «симптом → help.mantine.dev» и специфичная для Mantine лестница размещения; остальные пять reference сняты. Официальные носители Mantine для агентов — MCP-сервер @mantine/mcp-server и скилы mantinedev/skills — решено пока не устанавливать: 1mantine-dev обращается к llms.txt и help.mantine.dev по URL.

## Состав reference после рефактора

- Владелец решил оставить в рефакторе 1mantine-dev две reference: карту симптом→help.mantine.dev и специфичную для Mantine лестницу размещения, а остальные пять снять.

## Официальные носители

- Владелец решил пока не устанавливать официальные носители Mantine для агентов — MCP-сервер @mantine/mcp-server и скилы mantinedev/skills; 1mantine-dev обращается к llms.txt и help.mantine.dev по URL.

## Источники

- [решил оставить две reference в 1mantine-dev](../../../../../../../_ops/chat-recall/2026-08-11-000000-claude-e8af9475.md#L18)
- [решил пока не устанавливать официальные носители Mantine](../../../../../../../_ops/chat-recall/2026-08-11-000000-claude-e8af9475.md#L19)
