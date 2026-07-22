---
description: Multi-agent системы — независимые потоки, context hygiene, worker contract, synthesis и борьба с ложным consensus.
---

# Agents — Multi-agent Systems

Снимок обновлён 13 июля 2026. Исходный слой снят с `wisdom-agents.md` при
function-split refactor.

Здесь принципы про координацию нескольких агентов: разделение ролей,
передачу сообщений, fan-out и консенсус. Runtime гарантии — `runtime-layer.md`.
Tool surface каждого worker — `tool-design.md`.

## Проверено

- Роли агентов лучше разделять, чем собирать в одного «супер-агента». Для сложной системы устойчивее несколько узких ролей с ясными границами.
- Главная польза subagents — не только parallel speed, но и context hygiene:
  exploration notes, логи и большие промежуточные результаты остаются в worker
  threads; root хранит requirements, решения и integration, получая сжатый
  evidence packet вместо raw output.
- Безопасный default — независимые read-heavy потоки: exploration, tests,
  triage, review и summarization. Parallel writes требуют непересекающегося
  file/ownership scope или последовательного handoff; иначе coordination cost и
  конфликты съедают выигрыш.
- Multi-agent классическая ошибка — «сломанный телефон» через цепочку
  перепересказов. Исходные user inputs и critical evidence передавать без
  смыслового пересказа, а worker output возвращать по заранее заданному
  контракту. Fan-out держать минимальным: шире — supervisor становится
  bottleneck по контексту и синтезу.
- Sycophantic consensus: при голосовании или iterative discussion несколько LLM-агентов сходятся к согласию даже при ошибочной позиции одного. Если нужна реальная проверка — встраивать adversarial роль с мандатом «искать дыры», не консенсус.
- Parallel agents включать только когда есть независимые файлы, evidence streams
  или leaf implementation. Model-specific routing —
  `knowledge/wisdom-gpt-5.6.md`, `knowledge/wisdom-claude-opus-4.8.md` и
  `knowledge/wisdom-claude-fable-5.md`.

## Контракт Делегирования

До запуска worker-ов root или вызывающий skill должен назвать:

1. По какому критерию работа делится и какие потоки действительно независимы.
2. Какие результаты обязательны и нужно ли ждать все потоки перед продолжением.
3. Что возвращает каждый worker: summary, адресуемый evidence, gaps и blockers;
   не необработанный лог работы.
4. Кто имеет право писать и как исключено пересечение ownership.
5. Что остаётся у root: разрешение конфликтов, synthesis, integration и final
   validation.

Если чистого разделения нет или следующий ход зависит от результата предыдущего,
оставлять работу последовательной у одного агента.

## Surface Delta

- В текущем Codex subagents доступны как thread workflow. Их запускает прямой
  запрос пользователя либо применимая project/skill instruction; не полагаться
  на неявный fan-out, если он обязателен для результата.
- Responses API Multi-agent — отдельная beta surface со своими injected
  instructions, compaction и concurrency limits. Не переносить её runtime
  defaults в Codex или локальные agent configs как универсальный канон.
- Для GPT-5.6 demanding root/synthesis начинать с `Sol`, а лёгкие read-heavy
  workers проверять на `Terra`; качество, latency и cost подтверждать на
  representative tasks.

## Опоры

- https://learn.chatgpt.com/docs/agent-configuration/subagents
  Codex subagent workflows: context isolation, read-heavy default, worker
  prompting, model choice и thread controls.

- https://developers.openai.com/api/docs/guides/responses-multi-agent
  Отдельная Responses API beta surface и её runtime ограничения.

- `/knowledge/wisdom-claude-code.md`
  Платформенные наблюдения про Claude Code Agent tool, parallel agents, `isolation: "worktree"`.
