# Clean-room reimplementation — 1fresh-eyes — 2026-08-30

Статус: clean-room input завершён; полный candidate собран отдельно и не
переписывает этот нулевой черновик задним числом.

Исполнитель: отдельный `gpt-5.6-luna` / `max`, `fork_turns: none`. Он получил
только `intent.md` без старого пакета, истории, Product Frames и receipts.

## Clean-room reimplementation

```text
material fork
  → neutral packet
  → isolated lane runs
  → source verification of decision-changing claims
  → no-vote owner packet
```

Широкая развилка запускает ровно четыре независимых потока: `ladder`,
`solvent`, `prospector` и Premortem другой модельной семьи. Явно названная
доступная роль получает ровно один свежий native run без панели и panel
synthesis; недоступная роль не заменяется имитацией.

Нейтральный пакет сохраняет вопрос, варианты, ставки, ограничения, временной
горизонт, существенные сырые факты и наблюдаемое конечное состояние. Он не
передаёт rationale, желаемый verdict, confidence, прежние отчёты,
интерпретированный корпус или вывод главного агента.

Каждый поток сохраняет native output и адресуемую опору для утверждений,
которые меняют решение. Сборщик не считает голоса и возвращает `next`,
`nearest alternative`, `unchanged`; подтверждённый `unchanged` полноценен.
Отсутствующая роль или непроверенное material claim дают честный `incomplete`,
а не додуманный вывод.

## Zero-based design

Минимальный дизайн — один контракт с двумя режимами и тремя примитивами:

1. `neutralize(decision_object, terminal_result)`.
2. `run_isolated(lane, packet)`.
3. `assemble_without_vote(reports)`.

`panel` запускает четыре isolated lanes; `named` — один. Семантика свежести,
`unchanged`, `incomplete` и запрета голосования не зависит от runtime.

## Предложенная поверхность

Clean-room исполнитель предложил держать в `SKILL.md` trigger, два режима,
neutral packet, independence, fixed roster, native output, source verification,
decision handback, failure semantics и runtime adapter boundary.

Единственный возможный самостоятельный reference — lane contracts, только
если методы и evidence zones не принадлежат другому owner-у. Старый пакет
после этого показал, что методами уже владеют definitions ролей; отдельный
lane reference поэтому не принимается без нового доказательства.

## Выводимое и невыводимое

Из intent выводятся изоляция, отсутствие голосования, полноценный `unchanged`,
честный incomplete и запрет имитации роли. Отдельных строк требуют только
точный fresh-context runtime, cross-family bridge, сохранение native result,
порядок заморозки до отчётов, терминальные blockers и falsifying acceptance.

Clean-room исполнитель намеренно не выдумывал значения ролей, CLI/API,
провайдеров, scoring, thresholds, majority rules, автоматическую приёмку,
замену отсутствующей роли или скрытый классификатор материальности.

## Открытые вопросы для авторского прохода

- Какие runtime seams различаются у Claude и Codex.
- Какие старые hard lines доказаны наблюдаемым failure trace.
- Нужны ли отдельные references после сведения поведения к трём примитивам.
