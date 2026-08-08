---
description: "Evidence routing beyond direct instruction reads; не второй md/graph runbook."
read-when: "Repair требует exact, semantic или graph evidence вне уже прочитанных instruction files."
---

# Evidence Routing For Instruction-Layer Work

Открывай, когда instruction repair требует доказательств за пределами
прочитанного instruction file. Это router, а не второй runbook `md`.

## Маршруты

- Известны малые targets → direct Read; literal duplicate, exact citation, file
  count или stale wording → `1cli-tools`.
- Неизвестно, где живёт правило, или нужен broad duplicate/owner search →
  `1md-search`. Передай ему короткий тезис одного правила на
  query, languages вероятного source и нужные path constraints. Он владеет
  corpus/index/recovery и вернёт адресуемые bodies с gaps.
- Holders, `depends-on`, anchors, cycles, blast radius и graph closeout →
  `1md-graph`. Не дублируй его commands и verdict rules здесь.
- Если неизвестна точная `md` signature/schema, передай lookup в
  `1cli-tools`: live truth — `md tools <command> --json` и
  `md <command> --help`.

## Instruction-Layer Delta

Из чужого evidence packet верни только то, что нужно для repair:

- **question** — какое instruction rule/wording проверялось;
- **scope/filters** — какие instruction surfaces и exclusions реально покрыты;
- **evidence** — direct bodies/exact refs и непокрытые gaps;
- **verdict** — duplicate, drift, distinct delta или candidate-only;
- **consumer** — exact repair в instruction layer или handoff соседнему
  owner-у.

В audit mode остановись на evidence-backed proposed repair. В change mode
после edit всегда достаточен direct diff/read; другой closeout запускает
только owner задетого semantic/graph/exact-CLI риска.
