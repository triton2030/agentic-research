# Независимая проверка v4 · финальный раунд

## Literal checker

Candidate сохраняет один смысловой дефект: самостоятельно нарушимые инструкции
внутри составных абзацев не разделены по строкам. Окончательный active set равен
80 body + 1 routing, 61/55 по веткам. Counts и exact final probe сохранены, но
line-per-instruction defect остался после исчерпания двух повторных review-loop.

## Trajectory checker

Candidate-дефектов не найдено. Единственная находка относилась к тому, что
round-2 probe была привязана к прежнему SHA. Финальная factual trajectory exact
SHA `eb262405…` сохранена в `probe-2026-08-30-v4-round3.md`.

## Verdict

`blocked-before-approval`: смысловой candidate адресуем и прошёл clean-room,
loss-map, routing, trajectory и structural checks, но не выполняет текущий
line-per-independent-instruction contract и существенно превышает мягкий active
budget. Official owner/projections/live не изменяются. Новый approval-запрос не
разрешён, пока отдельный следующий цикл не решит структуру либо owner явно не
примет названное исключение.
