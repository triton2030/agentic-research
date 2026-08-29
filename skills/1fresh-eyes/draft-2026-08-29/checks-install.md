# Install evidence — 2026-08-29

## Owner decisions

- `_ops/chat-recall/2026-08-29-163434-codex-01a04d4a.md:15`: сохранять
  функцию и слова владельца, но не вредить скилу буквальностью.
- Тот же holder, `:19-20`: завершить установкой; instructional body и
  references — по-русски, frontmatter descriptions — короткий English
  trigger-only текст.
- Тот же holder, `:21`: сначала решать через `Уникальный контекст` и `Цель`
  как commander's intent; procedural hard line оставлять только у
  невыводимой механики, safety boundary, критичного порядка или falsifying
  acceptance.
- Тот же holder, `:22`: содержательный reference тоже может владеть локальной
  `Целью`; перечислять остаётся только то, что чистый агент не выводит без
  потери механики, безопасности или проверяемого поведения.

## Bounded commander's-intent pass

В `Уникальный контекст` перенесены причина утечки рамки main, источник
свежести, владение методом роли и смысл расхождения. В `Цель пользователя`
перенесены neutral source-bound input, отдельные evidence paths, native
handback, non-voting controller и полноценный `unchanged`.

Удалены как выводимые дубли: отдельные admission-вопросы; reminder о владении
методом роли; повтор native form в `named`; повтор чтения зоны и terminal
barrier в `panel`; action labels, grouping и второй запрет голосования в
`synthesis`.

Сохранены hard lines:

- freeze packets before first report — критичный порядок против leakage;
- native non-fork launch и cross-family runtime-owner — точные интерфейсы;
- recursive parent guard и `panel_incomplete` — safety/terminal boundaries;
- retained native/cross-family correction — точная runtime-механика;
- source verification + different evidence paths — falsifying acceptance.

Последний bounded checker вернул одну находку: named stop стоял до correction.
Steering-edge возвращён прямо в named branch; после этого findings — none.

## Bounded reference-goal pass

Локальную `Цель` получили пять references с самостоятельной функцией:
`packet.md`, `panel.md`, `premortem.md`, `steering.md`, `synthesis.md`.
`premortem.md` дополнительно получил `Уникальный контекст` о другой модельной
семье и recursive-parent risk. Малый служебный `named.md` оставлен без
декоративной цели.

Из целей теперь выводятся neutral source-bound packet; отсутствие утечки
Premortem в native panel; обратная failure-chain с signal/state/guardrail;
коррекция без нового голоса и steering trace; non-voting synthesis с native
records и разными evidence paths.

Hard lines сохранены там, где абстрактная цель небезопасна:

- `packet.md`: точные panel/named поля, freeze-order и swap repair;
- `panel.md`: фиксированный roster, runtime launch, bounded waves и
  `panel_incomplete` terminal boundary;
- `premortem.md`: recursive guard, точный cross-family owner, запрет native
  reports, first-line schema и terminal blocker;
- `steering.md`: точные retained-session API, условия нового потока,
  authority boundary и falsifying stop;
- `synthesis.md`: source verification и точная handback schema;
- `named.md`: один точный runtime launch и blocker без подмены.

## Atomic counts

Независимый conservative recount exact installed generation после локальных
целей:

- Claude files: `SKILL 57 · named 11 · packet 22 · panel 24 · premortem 30 · steering 24 · synthesis 20`.
- Codex files: `SKILL 57 · openai.yaml 4 · named 11 · packet 22 · panel 23 · premortem 30 · steering 26 · synthesis 21`.
- Active phases Claude/Codex: admission `30/30`; panel packet `27/27`; named
  packet `23/23`; local Premortem bridge `29/29`; native panel `25/24`;
  synthesis `24/25`; named run/correction/handback `13/13`; native correction
  `22/24`; cross-family correction `24/24`.

Nested `$1codex` / `$1claude-mcp` bodies не входят в closed local totals.
Excess сохранён как attention risk; нового ceremonial split ради 20 нет.

## Trigger evidence

Exact description:

`Use when long work reaches a material trajectory fork, the user requests fresh eyes, or names one specialist profile such as auditor or Premortem.`

Первая укороченная версия без примеров ошибочно направила bare «Проведи один
Premortem» в framework near-miss. После локальной правки fresh
`claude-opus-5` probe (`warnings=[]`) дал expected result: B/C/D/H use; A/E
skip/local; F cross-model near-miss; G framework-method near-miss.

## Functional clean-run

Claims привязаны к runtime `SKILL.md` SHA-256
`901cda9c45450ca7a23bbc14f1b71ed4d3c5557b9bcf650d5b5632d2b2c5fef9`.

- Named: один `auditor`, `fork_turns:"none"`; panel roles не запускались;
  terminal native audit — pass; correction edge проверен latest hash.
- Frozen panel packets: `P-PRE-20260829-03`, `P-LAD-20260829-03`,
  `P-SOL-20260829-03`, `P-PRO-20260829-03`.
- Premortem: session `cd0ddc91-100d-44c6-be28-ff28ba70075f`,
  resolved `claude-opus-5`, fresh warnings `[]`; после hash steering verdict
  `signal_watchable / install now`.
- Native bounded waves: `ladder` + `solvent`, затем `prospector`; все
  `fork_turns:"none"`, без Premortem output; четыре terminal reports получены.
- Линзы различались: цель/направление · снимаемое допущение · внешние классы ·
  история провала. Synthesis вернул `next / nearest alternative / unchanged`
  без голосования и выбрал install.

Residual: Premortem локально насчитал synthesis `20`, независимый conservative
checker — Codex `21`. Число остаётся диагностикой, не acceptance gate;
функционального omission trial не показал. Claude named branch source-supported,
но отдельно end-to-end не запускалась.

После reference-goal pass один чистый agent построил из текущего `packet.md`
panel packet и named auditor packet. Оба сохранили decision anchor,
observed state, evidence addresses, material gaps, boundaries, отдельную panel
zone, `Main уже читал` + rounds и named evidence object; rationale и желаемый
verdict main не утекли. Это falsifying evidence относится к новым references;
старый полный clean-run по-прежнему относится к неизменному `SKILL.md` hash.

## Installation

- Claude tracked owner: `skills/claude/1fresh-eyes/`; product-frame pair
  сохранена только здесь и не установлена в runtime package.
- Codex tracked runtime owner создан: `skills/codex/1fresh-eyes/`.
- Installed projections: `~/.claude/skills/1fresh-eyes/` и
  `~/.codex/skills/1fresh-eyes/`.
- Старые `brief-templates.md`, `steering-and-dialogue.md`,
  `synthesis-and-evidence.md` и installed Claude `cut.md` удалены из runtime
  package; история осталась в repo/git.
- Tracked → installed byte manifests совпадают; общие `SKILL.md`, `packet.md`
  и логика runtime-пакетов сохранены по owner contract.
- Exact package fingerprints после последней синхронизации: Claude
  `1cd6171da6c68216475c19f3902ee589c5662681508589166364e4f41448a648`,
  Codex `c3165347acfa0555c80ad2fcb5c6b1057d193d605b101bfe15703fd7a9a12e5b`.

## Checks

- `qv-skill`: valid для обоих tracked owners и installed projections; прежний
  полный runtime trial покрывает неизменившийся `SKILL.md`.
- YAML: все frontmatters и `agents/openai.yaml` parse.
- Relative links: все существуют.
- Language audit: instructional body/references русские; Latin остаток —
  stable names, commands, schema keys, code и English frontmatter.
- `git diff --check`: clean.
- Exact installed `SKILL.md` hash в обеих средах: `901cda9c…fef9`.
- Последний clean packet probe: `9/9 pass`; tracked↔installed manifests:
  byte-equal в обеих runtime-формах.
