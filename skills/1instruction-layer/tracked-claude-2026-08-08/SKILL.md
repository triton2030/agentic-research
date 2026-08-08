---
name: 1instruction-layer
description: >
  Use when writing or auditing durable `AGENTS.md`, `CLAUDE.md`, path rules or
  repo-local instruction files; a plausible rule can otherwise load from the
  wrong owner or be obeyed in form while leaving the same agent decision
  unchanged. Recover the effective chain and design the smallest
  trajectory-changing delta; prose is not enforcement.
---

# Слой Инструкций

Этот controller владеет методом мышления; references владеют только условной
глубиной. До Gate 0 прочитай [`product-jobs.md`](references/product-jobs.md)
(продукт, мера, режимы `audit`/`change`, границы) и
[`controller.md`](references/controller.md) (три failure-а иерархии, re-anchor,
decision traces).

Держи компактное рабочее состояние
`admission → chain map → owner → steering cell → control → exact delta → proof`.
Каждый gate должен породить свой наблюдаемый результат до следующего. Пропустить
gate можно только когда его результат уже прямо подтверждён текущим evidence;
гладкий финальный текст не заменяет промежуточное различение.

Шаги controller-а — по файлу на gate; открывай файл в момент этого gate, до его
решения:

- Gate 0 допуск durable работы — [`gate0-admission.md`](references/gate0-admission.md)
- Gate 1 effective chain map — [`gate1-chain.md`](references/gate1-chain.md)
- Gate 2 owner и класс delta — [`gate2-owner.md`](references/gate2-owner.md)
- Gate 3 steering cell — [`gate3-steering.md`](references/gate3-steering.md)
- Gate 4 control и один repair — [`gate4-control.md`](references/gate4-control.md)
- Gate 5 exact delta — [`gate5-wording.md`](references/gate5-wording.md)
- Gate 6 bypass и доказательство — [`gate6-bypass.md`](references/gate6-bypass.md),
  затем [`gate6-proof.md`](references/gate6-proof.md)

Перед финальным ответом открой [`output-stop.md`](references/output-stop.md):
формат вывода, условия готовности и стоп.
