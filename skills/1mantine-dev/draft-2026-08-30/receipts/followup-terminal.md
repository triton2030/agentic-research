# Terminal receipt — simplicity follow-up, 2026-08-30

## Статус

`TERMINAL_BLOCKER`: candidate semantic surface проходит, но exact approval и
установка остановлены по результатам одного полного exact-version цикла. После
этого цикла runtime-файлы не переписывались.

## Версия candidate

Предыдущий пакет до follow-up: `19e4a1e9e1fbc8be02e3d342eff9f094c70d81fb3e4c7539525a1388e8f46284`.

Текущий пакет (только `SKILL.md` и два runtime references):
`bbb8a2c3399cae25cc4c37086beb160bea67e5fc19d8c738cb294653e8b00842`.

| Файл | SHA-256 |
| --- | --- |
| `SKILL.md` | `3a4855f14e114258f8333a219465b5c12b25c2e3e1f0e9e75d442cc4cb1ec909` |
| `references/audit.md` | `3c819f8b27f6c0a0b90b6802001bfea62f104337b860bfb0a48150a837995d14` |
| `references/last-year.md` | `6f6f1fa1948eb2b1b88d8b5c3486e80a674b36cee16bd2aa53f63b9779671d43` |

Изменены runtime-артефакты: `SKILL.md`, `references/audit.md`,
`references/last-year.md`. Карта и receipts дополнены для evidence; official
owners, projections, live packages и `1skill-creation` не изменялись.

## Пройденные стадии и проверки

- `$1chat-recall`: поздние owner-слова подтвердили official-first, conditional audit/version, commander intent и запрет procedural overload.
- `$1fresh-eyes` trajectory-critic: прежний stage split — method-as-goal; следующий ход — core + два условных gate.
- Clean-room / Zero-based: независимое предложение из трёх runtime-файлов; authoring/check ceremony исключена.
- Независимый literal checker: выполнен на полном входе `1skill-creation` и history; вернул три findings ниже.
- Независимый trajectory checker: semantic pass, closure blocked.
- Clean probe: четыре cases; ordinary local path остаётся лёгким, version/audit handoffs распознаются.
- `qv-skill skills/1mantine-dev/draft-2026-08-30`: pass.
- `md check --paths skills/1mantine-dev --json`: 18 targets, 0 issues.
- `git diff --check`: pass.
- Codex/Claude live hash parity: обе live projections остались
  `91354c6f5ad37ce14b5459e12cbf27d653c01e7b1bea681ab024931ceec8da54`.
- `python3 skills/shared/sync_simple_projections.py 1skill-creation --check`:
  pass; effective baseline fingerprint остаётся
  `9bf11f64b436d313d979cba822b684f502e8e40e5f15a12f78cbd914ca29a518`.

Два исходных handoff-gap закрыты в runtime: `last-year.md:21-23` буквально
сохраняет task packet и resolved/confirmed cohort; `audit.md:12-14` буквально
передаёт required behaviors, cohort, named scope и current solution.

## Terminal findings

1. `map.md:11-27` занижает semantic counts. Literal checker насчитал
   `SKILL.md` — 36, `audit.md` — 34, `last-year.md` — 28; active sets —
   `core` 21, `version gate` 43, `audit gate` 54, тогда как карта заявляет
   12/10/9 и 12/19/20. Это нарушает запрет укрупнять независимо нарушимые
   предикаты и лимит 20; необходимы пересчёт и дальнейшее смысловое сжатие без
   новых микростадий.
2. `SKILL.md:23` и `last-year.md:11-12` не задают, что делать при отсутствии
   lockfile, installed metadata или public types. `resolved cohort` можно
   ошибочно принять за диапазон manifest/registry; нужен явный `cohort:
   unknown` и запрет подтверждённого version-specific результата до
   разрешения когорты.
3. `reviews-terminal.md:1-39` всё ещё называет старые hashes exact candidate и
   closure. Этот historical receipt не покрывает текущий пакет; его нужно
   пометить superseded либо заменить отдельной closure-квитанцией.
4. Clean probe обнаружил material routing residue для hybrid
   mismatch+review: current route может открыть `audit.md` до version gate;
   также обычные два поведения (`Button` + `useForm`) попадают в полный audit,
   что создаёт избыточный overhead относительно simplicity criterion.

## Needs

Не утверждать и не устанавливать текущий пакет. Для следующего захода нужен
один новый bounded repair: точный semantic-count map без механического дробления,
явный unknown/blocker для неразрешённой cohort, однозначный version-before-audit
маршрут и новая closure-квитанция; затем достаточно одного exact check cycle.
