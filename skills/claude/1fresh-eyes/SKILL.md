---
name: 1fresh-eyes
description: >
  Use when the user asks for fresh eyes, a named native Claude
  critic/auditor/scout, independent review, or parallel evaluative agents;
  also when one concrete cross-domain result could reverse a material
  decision. Prevents a self-confirming review from masquerading as evidence.
---

# Свежие Глаза

## Product Job

До material commitment преврати запрос пользователя либо strongest untested
defeater в правильно изолированный stream нужного native agent. Продукт — не
число агентов и не суровость ответа, а decision-ready input:

- critic возвращает собственный judgment и alternative;
- `auditor` проверяет acceptance как `pass/fail/unknown`;
- `md-scout` возвращает адресуемый evidence packet без semantic verdict.

Main context владеет исходным решением, проверкой source claims, синтезом и
правками. Native role владеет своим методом и формой ответа; gateway их не
унифицирует.

Мера успеха: после проверки owner может назвать следующий action — изменить
решение, продолжить, собрать missing evidence или остановиться. Agent count,
consensus и само слово `independent` этой меры не закрывают.

## Почему Обычный Review Подтверждает Себя

Main уже self-conditioned собственным решением. Естественный shortcut —
выбрать профиль по типу артефакта, передать ему свою гипотезу и принять
совпавший verdict за независимость. Даже новая Claude `Agent`-инвокация не
поможет, если brief заранее задаёт вывод; а fork либо resumed stream переносит
ещё и frame main/предыдущего review.

Разрыв causal chain:

```text
owner decision
→ заранее названный result, который изменит next action
→ native role, владеющая именно этим information job
→ fresh Agent context + self-contained non-leading brief
→ native product без нормализации
→ source verification
→ owner action
```

## Challenge Anchor

До spawn зафиксируй в working context, не превращая это в пользовательскую
анкету:

```text
decision: что сейчас выбирает owner
current route: что main собирается сделать и почему
reversal result: какой наблюдаемый результат изменит next action
output job: judgment | acceptance | evidence
role: named profile и почему она владеет output job
```

Explicit named-agent request фиксирует `role`; не переигрывай выбор
пользователя через chooser. Для implicit critic run отсутствие честного
`reversal result` означает, что main ищет reassurance: не spawn-и review по
одной materiality.

## Named Role Catalog

| Output job | `Agent` subagent_type | Выбирай, когда решение может опровергнуть |
|---|---|---|
| business judgment | `business-critic` | viability, adoption, economics, trust |
| implementation judgment | `developer-critic` | feasibility, dependencies, tests, DX |
| structural judgment | `architecture-critic` | boundaries, ownership, conceptual integrity |
| trajectory judgment | `smith` | direction, sequence, opportunity cost, future cost |
| acceptance evidence | `auditor` | stated conditions and claimed completion |
| corpus evidence | `md-scout` | broad Markdown retrieval, coverage and gaps |

Для implicit material challenge выбирай одну из четырёх critic roles по
strongest neighboring-domain defeater, а не по artifact type. `auditor` и
`md-scout` выбираются по требуемому native product, не как critic substitutes.

Callable `subagent_type` schema — runtime truth. Если выбранный профиль не
selectable, остановись: создание ad hoc critic contract через
`general-purpose` не принадлежит этому gateway. Exact named profile
пользователя не подменяй без его согласия.

## Independence Boundary

Fresh first pass требует одновременно двух условий:

1. Первый проход стартует только новой обычной non-fork `Agent`-инвокацией с
   exact `subagent_type`. `context: fork` и `/subtask` наследуют parent frame;
   `SendMessage` и resumed ID легитимны только после первого прохода как
   retained dialogue. Ни один из этих путей не создаёт fresh first pass.
2. Self-contained brief с decision/current route, raw artifact paths,
   source-bound facts, unknowns, scope и forbidden side effects. Перед spawn
   прочитай [`references/brief-templates.md`](references/brief-templates.md).

Не передавай conclusion main agent, preferred alternative, suspected hotspot,
investigative sequence, native role recap или desired verdict. Текущий route
нужно назвать фактически — critic должен видеть предмет атаки, но не его защиту.

Fresh named agent не видит parent conversation, но это не blank slate: Claude
Code передаёт definition профиля, активную `CLAUDE.md` hierarchy и git status
snapshot. Если спорный claim уже встроен в active instruction stack, назови
ограничение; такой pass conversation-isolated, но не instruction-isolated.

Если нужный input нельзя передать self-contained в новую non-fork invocation,
честно назови результат `peer review` или `retained consultation`; явный запрос
на independence им не закрывается.

## Split И Dialogue

Parallel fan-out оправдан только отдельными output jobs, reversal results либо
disjoint artifacts. Один и тот же critic на одном артефакте создаёт duplicate
votes, не дополнительную независимость. Если smallest split неочевиден,
прочитай [`references/split-patterns.md`](references/split-patterns.md).

Decision-required streams образуют completion barrier. Пока они работают,
main может продолжать только disjoint work, но не commit/ship, claim done,
finalize decision или отдавать final response до возврата и синтеза всех
обязательных products. Недоступный либо failed stream остаётся missing input,
а не молчаливым разрешением продолжить.

Первый ответ остаётся native fresh pass. После main intervention тот же stream
становится `steered pass`, `repaired pass` или `retained consultation`.
Исправляй только факты, source, scope и permissions; не desired conclusion или
native method. Exact operations и reopen boundary —
[`references/steering-and-dialogue.md`](references/steering-and-dialogue.md).

## Verify И Act

Не своди разные roles к общей schema и не голосуй:

- critic finding принимается только после проверки supporting source; без
  alternative он не decision-ready;
- `auditor` сохраняет native acceptance matrix и typed evidence;
- `md-scout` сохраняет addresses, actual scope/coverage и gaps, но не получает
  critic status;
- disagreement остаётся видимым и может означать ambiguous brief, rubric или
  owner boundary.

Вернись к Challenge Anchor: какой verified input изменил `decision` или
`current route`? Classification critic findings и handling invalid tests живут
в [`references/synthesis-and-evidence.md`](references/synthesis-and-evidence.md).
Edits и final validation выполняет main owner.

## Thought Demonstrations

**Default → transition.** При rewrite skill тип артефакта подталкивает к
`developer-critic` или `md-scout`. Но если next action изменится при
обнаружении ownership leak, output job — structural judgment, а role —
`architecture-critic`. Artifact не выбрал lens; reversal result выбрал.

**Антипример.** Три critics запускаются через `context: fork`, получают
hypothesis main и сходятся в verdict. Формально это разные agents, но их
frame общий; consensus умножил один и тот же prior, а не evidence.

**Перенос.** Пользователь прямо просит `md-scout` проверить Markdown corpus.
Gateway запускает новую named Agent с corpus/scope/question. Scout возвращает
coverage и gaps; main может изменить решение по packet, но не пересказывает
его как `architecture_ok` или critic vote.

## Граница И Stop

`1fresh-eyes` владеет named-role routing, isolation boundary и возвратом native
product к owner decision. Он не владеет методами roles, truth в артефактах,
semantic retrieval, final acceptance или mutation. Generic/cross-model review
принадлежит `1codex`, а не этому gateway.

Готово, когда runtime mode честно назван, fresh pass начат новой non-fork
`Agent`-инвокацией, native product сохранён, decision-changing claims проверены
и owner action явен. Остановись, если `Agent` недоступен; exact requested role
не selectable и замена не разрешена; два follow-up не сужают evidence,
alternative или decision; либо outputs уже синтезированы.

Behavioral hypothesis датирована `Claude Code 2.1.220`, 2026-08-04. Смена
runtime semantics, callable schema или повтор tells `forked context`,
`artifact-picked lens`, `consensus as proof` reopen-ят контракт.
