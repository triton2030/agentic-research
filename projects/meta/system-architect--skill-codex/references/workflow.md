# Workflow — Rigid Spine

Порядок rigid. Не переставляй.

## 1. Telos / Upstream Check

Сначала прочитай:

- `_ops/PROJECT-PLAN.md` — Goal, активный Stage, Approach & Why, Anti-goals.
- `_ops/INTERVIEW.md` — только предпочтения, которые реально ограничивают архитектурный выбор.
- `_ops/learnings.md` — если есть; это лучший источник реальных failure classes.
- корневые и локальные `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`.

Gate пройден только если:

- Goal описывает результат, а не процесс;
- есть активный Stage с понятным направлением;
- `INTERVIEW.md` не contaminated routing / owner-chain / folder policy;
- learnings либо пуст, либо конкретен.

Если Goal или Stage слабы — **блокируй audit** и возвращай к `main-strategy`. Не компенсируй слабую карту generic архитектурой.

## 2. As-is Map

Это first-order шаг, не поздняя линза.

Собери карту того, что реально есть **на этой машине и в этом репо**:

- evidence type: `direct trace` | `user-reported summary` | `structure-only`;
- installed skills, plugins, validators, hooks, permissions, approvals, tool constraints;
- доступные subagents или их отсутствие;
- какие owner surfaces живые, а какие только упомянуты в текстах;
- какие folder surfaces реально производят артефакты.

Разделяй:

- `реально существует`;
- `подразумевается текстом`;
- `отсутствует`.

Если capability inventory не сделан, prescriptions дальше невалидны.

Внешний поиск до local capability audit — anti-pattern.

## 3. Forces

До failure map назови 2-4 силы, которые уже влияют на дизайн или будут давить в горизонте 6-24 месяцев:

- рост или сжатие tool surface;
- смена основной модели;
- рост числа типов задач;
- рост числа owner layers;
- новый класс пользователей / новый режим работы;
- любая другая сила с конкретным ранним сигналом.

Для каждой силы нужен:

- что именно изменится;
- ранний сигнал;
- почему сила должна влиять на design choice уже сейчас.

Если Force Fields живут только в финальном epilogue, это ошибка дизайна.

## 4. Failure Classes

Не делай россыпь симптомов. Собирай failure **в классы**.

Источники:

1. `_ops/learnings.md`
2. текущий trace, если он есть
3. inversion/premortem по активному Stage

Для каждого класса:

- что конкретно ломается;
- где текущая система это позволяет;
- чем класс отличается от соседнего;
- какие силы из шага 3 делают его вероятнее.

Плохая форма:

- пять почти одинаковых failure items;
- generic `модель может ошибиться`;
- failure без места, где система его позволяет.

## 5. Leverage Analysis

Это центр архитектурного мышления.

Вопрос не такой: `какой фикс закрывает этот сбой?`

Вопрос такой:

> какая одна правка убивает класс из нескольких failure modes, а не лечит один симптом?

Для каждого leverage candidate покажи:

- какие failure classes он collapse'ит;
- почему это leverage, а не bundle из мелких patch'ей;
- его reversibility и blast radius;
- в каком owner layer он должен жить.

Если честного leverage нет, так и скажи. Не изобретай абстракцию ради красивой схемы.

## 6. Prescriptions

Prescriptions появляются только после leverage analysis.

Каждая prescription обязана содержать:

- **Fix-layer**: `runtime guardrail` | `local skill` | `instruction text` | `criteria-generator handoff` | `human checkpoint`
- **Leverage target**: какие failure classes она схлопывает
- **Почему это лучше мелких patch'ей**
- **Почему более сильный слой отклонён**, если prescription не runtime
- **Конкретный механизм**, если это runtime layer
- **Backlink**: `→ protects PROJECT-PLAN §Goal` / `§Stage <name>` / `→ addresses learnings entry <date>` / `→ honors INTERVIEW §<section>`
- **Observable signal**
- **Sunset signal**
- **Owner**

Для major prescriptions добавь proof path:

- `existing evidence`;
- `fresh-context probe` если платформа и диалог это позволяют;
- `не запускался` с честной причиной.

## 7. Minimize Pass

Перед финальным emit попытайся **убрать**, а не только добавить.

Обязательные вопросы:

- что можно удалить;
- что можно не создавать;
- что можно слить в один owner layer;
- какой новый skill / hook / doc оказался не нужен после leverage analysis.

Архитектор без minimize pass почти всегда переусложняет.

Если scope касается папок, здесь и появляются verdicts:

- `keep`
- `archive`
- `remove`
- `do not create`

Chesterton's fence всё ещё обязателен: не удаляй то, чью причину не понимаешь.

## 8. Handoff + Default Route

Финал должен замкнуть петлю:

- `Default route for fresh session`
- `Main-strategy handoff`, если вскрыт upstream drift
- `Criteria handoff`, если нужен task-level контракт

`system-architect` не переписывает `PROJECT-PLAN.md` или `INTERVIEW.md` сам, но обязан назвать следующий owner и следующий шаг.

## EVPI Questions

Вопрос допустим только если ответ materially меняет:

- fix-layer;
- owner;
- whether to add vs remove;
- whether the force is real or not.

Не задавай:

- `согласен с моим анализом?`
- открытые вопросы без 2-4 реальных вариантов;
- вопросы, которые меняют только wording.
