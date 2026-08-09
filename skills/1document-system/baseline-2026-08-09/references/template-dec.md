# DEC — Decision Record

**Purpose:** сохранить одну material развилку, почему выбран вариант, его
последствия и границу пересмотра. **Default authority:** `decision`.
Aliases: ADR, BDR. Near-miss: evidence → RPT; product scope → PRD; change design
→ EDD. DEC владеет выбором и rationale, не фактами или реализацией.

## Core Sections

| Heading | Mode | Contract |
| --- | --- | --- |
| Decision Identity and Status | OWNER | ID, title, date, workflow-state, decision owner |
| Context | REFERENCE | Минимальная ситуация и owner identities/pointers по действующему profile |
| Decision Question | OWNER | Одна точная развилка |
| Decision Drivers | OWNER | Ranked constraints и success conditions |
| Options Considered | OWNER | Реальные alternatives, включая status quo когда применим |
| Decision | OWNER | Выбранный вариант без operational ambiguity |
| Rationale | OWNER | Почему выбор выигрывает; evidence отдельно от judgment |
| Consequences | OWNER | Positive, negative, neutral, accepted debt |
| Required Follow-through | LOCAL | Affected owner identities/pointers → exact decision-induced action/delta, без копии specs |
| Reversibility and Rollback | OWNER | One/two-way door, rollback boundary |
| Revisit Conditions | OWNER | Observable triggers, не calendar reminder |
| Related Owners | REFERENCE | Evidence, requirements, architecture, rules identities/pointers |
| Supersession | OWNER | Predecessor/successor и что остаётся valid |

## Conditional Modules

Architecture/business/legal/vendor impact; approval/dissent log; rollout gate;
options matrix.

## Business Decision Record Profile

BDR — самодостаточная append-only историческая запись material business choice,
а не current truth owner. После acceptance она не редактируется; новое решение
создаёт новый BDR, а нормативные последствия тем же ходом обновляют live owners.

В BDR не вставляй Markdown links, wikilinks, URLs, filesystem paths, anchors или
graph relations (`depends-on`, `derived-from`) ни в body, ни во frontmatter.
Predecessor, successor, affected owner и provenance называй plain stable IDs без
link syntax. Local contract может выбрать поля для этих IDs, но не превращать
историческую запись в dependency hub.

## Completion Check

Одна decision question; alternatives реальны; drivers, trade-offs, negative
consequences и revisit triggers явны; downstream owner updates адресованы по
действующему profile, а не спрятаны внутри DEC. Для BDR все identifiers plain,
Markdown/wikilinks и graph dependencies отсутствуют.

