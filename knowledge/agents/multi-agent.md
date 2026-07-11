---
description: Multi-agent системы — supervisor bottleneck, forward_message и борьба с sycophantic consensus.
---

# Agents — Multi-agent Systems

Снимок на 20 мая 2026. Снято с `wisdom-agents.md` при function-split refactor.

Здесь принципы про координацию нескольких агентов: разделение ролей,
передачу сообщений, fan-out и консенсус. Runtime гарантии — `runtime-layer.md`.
Tool surface каждого worker — `tool-design.md`.

## Проверено

- Роли агентов лучше разделять, чем собирать в одного «супер-агента». Для сложной системы устойчивее несколько узких ролей с ясными границами.
- Multi-agent классическая ошибка — «сломанный телефон» через цепочку перепересказов. Решение — forward_message-паттерн (передача сообщения как есть, а не пересказ) и лимит 3-5 worker-агентов на одного supervisor; шире — supervisor становится bottleneck по контексту.
- Sycophantic consensus: при голосовании или iterative discussion несколько LLM-агентов сходятся к согласию даже при ошибочной позиции одного. Если нужна реальная проверка — встраивать adversarial роль с мандатом «искать дыры», не консенсус.
- Parallel agents включать только когда есть независимые файлы, evidence streams или leaf implementation. Model-specific fan-out policy — `knowledge/wisdom-gpt-5.6.md`, `knowledge/wisdom-claude-opus-4.7.md`.

## Опоры

- `/knowledge/wisdom-claude-code.md`
  Платформенные наблюдения про Claude Code Agent tool, parallel agents, `isolation: "worktree"`.
