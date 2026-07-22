---
description: "Body-evidence admission test and verdicts for declared, missing or invalid depends-on edges."
---

# Semantic Edge Audit

Contents: Boundary · Evidence Packet · Admission Test · Verdicts ·
Owner-Conflict Slots · Flow Check · Closeout.

Открывай, когда mechanical graph уже известен, но надо решить: верен ли
declared `depends-on`, отсутствует ли обязательный edge, или связь вообще не
должна быть edge.

## Граница

- Container, split/merge/move/rename, block placement и owner-shape сначала
  решает `1ia-audit`.
- `1md-graph` решает только source/downstream direction и propagation.
- `1md-navigator` даёт semantic candidates; similarity не создаёт edge.

## Evidence Packet

Собери target, его direct `must_read`, direct `must_update`, важные body links
и выбранные semantic candidates. Reuse текущий `preflight`; повтори его только
если evidence отсутствует или target/state изменился. Затем:

```bash
md read-related --paths TARGET --scan GRAPH_ROOT --json
```

Из map выбери и прочитай нужные bodies напрямую до verdict. Packet-level
`_envelope.next_step` раскрывает весь neighborhood, не selected item; запускай его
только для малого packet или с явным `--token-budget N`. Recorded graph
кажется неполным — bounded candidates через `1md-navigator`; second hop не
расширяй автоматически.

## Admission Test

Перед `keep` или `add-missing` заполни одну проверяемую конструкцию:

> Если в `SOURCE#section` изменится **X**, то в `HOLDER#section` станет ложным
> или misleading **Y**.

Требования:

- **X** — адресуемый контракт: правило, роль, формула, enum, обещание,
  ограничение, право, evidence;
- **Y** — конкретная проекция этого контракта в теле holder-а;
- для X и Y названы `path#heading` и краткое body evidence;
- «важно», «связано», «полезно прочитать», общая тема и сходный словарь
  admission test НЕ проходят.

Direction test: **source владеет X; holder применяет, ограничивает или
пересказывает X.** Оба файла заявляют владение X, либо source отсылает к
holder-у как к канону → `owner-conflict`, не `keep` и не reciprocal edge.

Отказы теста:

- есть X, но нет конкретного Y → `downgrade` до navigation;
- есть Y, но source не владеет X → `reverse`, `remove` или `owner-conflict`;
- holder останется верным при материальном изменении X → edge не hard;
- изменение нерелевантной части source не доказывает связь.

Стоп-правило: нельзя создать или сохранить hard edge на основании одних
frontmatter, description, similarity score или тезиса «документы связаны».

## Verdicts

- `keep` — X/Y и direction подтверждены body evidence;
- `reverse` — edge записан в обратную сторону;
- `downgrade` — useful navigation, не obligation;
- `remove` — stale, decorative или misleading edge;
- `add-missing` — обязательный source meaning не объявлен (X/Y названы);
- `owner-conflict` — владение инвариантом спорно; edge-edit стоп, решение у
  `1ia-audit`;
- `deferred` — owner/scope/evidence недостаточны для verdict.

Для каждого verdict — X/Y и body addresses. Большой cascade или similarity
score сами по себе не ошибка.

## Owner-Conflict Slots

Для спорной пары заполни:

```text
A owns:
A says B owns:
B owns:
B says A owns:
shared invariant:
```

Один invariant заявлен обоими, либо каждый делегирует его другому →
`owner-conflict`. `md cycles == 0` этого не опровергает: он видит только
frontmatter-циклы, петля живёт в тексте.

## Flow Check

Проверь только то, что меняет edge verdict:

- base claim приходит до downstream detail;
- child применяет/уточняет source, а не становится вторым canon;
- anchor ведёт к нужной секции;
- sibling summaries не конкурируют как owner truth.

Если flow требует менять container или переносить truth, останови edge edit и
передай решение `1ia-audit`.

## Closeout

После авторизованной edge-правки прогони `preflight`, scoped `check` и
`cycles`. Стоп, когда у каждой audited пары есть verdict с X/Y evidence и
findings сообщены; при разрешённых edits ошибки исправлены или blocked, иначе
получили action/handoff.
