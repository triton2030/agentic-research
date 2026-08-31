---
name: 1codex-bg-threads
description: >-
  Use when the user asks to offload work to, create, continue, fork, or retain
  visible background Codex threads.
---

# Фоновые треды Codex

## Уникальный контекст

Вызов превращает root из исполнителя в технического директора: делимую работу
и мышление он переносит в видимые Codex threads, а внимание оставляет
бизнес-пользе и целостности. Luna/max даёт дешёвую мощность; retained context
ускоряет повторные темы, но не становится истиной. Mutable writing требует
независимой проверки.

## Цели пользователя

- Root делегирует делимую работу и мышление, сохраняя бизнес- и архитектурное
  решение.
- Каждый thread получает посильный outcome и достаточный текущий контекст.
- Mutable результаты и terminal lifecycle доказаны внешне.

## Роль

- `THREAD_CARD`, заполненная по всем полям
  [thread-brief](references/thread-brief.md), назначает receiver; любая
  отсутствующая часть оставляет controller.
- Receiver выполняет только карточку. Он может использовать собственных
  same-thread subagents, но не управляет top-level visible threads.
- Retained receiver сначала закрывает
  [retained-thread](references/retained-thread.md) source-basis артефактом.
- Перед единственным `THREAD_DONE` receiver открывает
  [thread-result](references/thread-result.md).
- Без `THREAD_CARD` ты controller и технический директор: управляй top-level
  visible threads и не отдавай им бизнес-приоритет, topology, сквозную
  архитектурную траекторию, synthesis, integration или acceptance.

## Протокол поведения

> «Моя цель, это чтобы агент сам не работал, а чтобы он через фоновые тряды был
> оркестратором верхнего уровня».

> «...я хочу, чтобы мы вызывали именно дешевых Луна МАКС. Это именно в
> протоколе скилла должно быть. Но по дефолту».

> «...если я вызываю луну или фоновых агентов для того, чтобы они по факту
> писали», тогда «обязателен протокол проверки агентов».

Следующие стадии выполняет только controller; receiver следует разделу «Роль».

1. Отдельной стадией заверши `1orchestration` до принятых slots. Делегируй
   каждый делимый исполнительский и аналитический вклад; `no-delegation`
   оставь только для неустранимых решений технического директора.
2. По умолчанию назначай exact `gpt-5.6-luna` + `max`. Для действительно
   сложного мышления разрешены `gpt-5.6-sol` + `medium` либо `xhigh`; effort
   выбирается по сложности, неопределённости и риску.
3. Закрой [runtime](references/runtime.md) одним capability snapshot.
4. До карточки закрой [environment](references/environment.md) одним
   environment verdict.
5. Перед новым запросом к существующему retained specialist закрой
   [retained-thread](references/retained-thread.md) current-source артефактом.
6. Для launch, fork или follow-up открой
   [thread-brief](references/thread-brief.md).
7. При terminal, failed или needs-input состоянии открой
   [thread-result](references/thread-result.md).
8. После acceptance bounded результата либо завершения зонтичной
   retained-service открой
   [lifecycle](references/lifecycle.md).
