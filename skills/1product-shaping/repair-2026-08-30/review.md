# Exact-version review — functional repair — 2026-08-31

Candidate package:
`skills/1product-shaping/candidate-repair-2026-08-31/`.

Package hash:
`c34fdcf3a27226144de81acc5784458b5297834d3173fce02f5f3eded4bbac7f`.

## Exact files

- `SKILL.md`:
  `f1867a192c68200ab72e63a2f05c41ba0306928b7da1337707d4b7070a4fa896`.
- `references/pair-contract.md`:
  `10607e24f90958903036956db49b8c08a398427b99a1624dae80a86ec8d896e3`.
- `platforms/codex/agents/openai.yaml`:
  `76a092a743e2ff0c0b470bd8ee3449eaf1c651d6de19a3c0b1236ac08a016370`.

Package hash algorithm from repo root:

```bash
d='skills/1product-shaping/candidate-repair-2026-08-31'
find "$d" -type f -print0 | sort -z | xargs -0 shasum -a 256 \
  | sed "s#  $d/##" | shasum -a 256
```

## Основание

- Current `1skill-creation` SKILL SHA-256:
  `6e6b93e97eef2a31c8922ba8462a28a086c82ec80c6566c39ed63fc6bdc9f6a3`.
- Owner evidence и observed loss перечислены в `intent.md` и `loss-map.md`.
- Текущий orchestration follow-up не использован как owner speech.

## Проверки exact версии

- Literal checker, final round: `Находок-правок: нет`; package hash совпал;
  ссылка существует; YAML разбирается; `description` 133 символа,
  `short_description` 117 символов.
- Raw semantic counts: `SKILL.md` 42, `pair-contract.md` 63, `openai.yaml` 5.
  Checker не признал превышение отдельной находкой: ориентир 20 мягкий, а
  схема сохраняет измеренно потерянную функцию.
- Trajectory checker, final round: `Находки: []`; путь остаётся
  commander-intent + одна output/authority schema без interview, examples или
  новых стадий.
- Clean probe, final round: выданы все три поверхности и все пять обязательных
  разделов Frame; неподтверждённые P-003…P-005 отклонены; terminal state
  `AWAITING_EXACT_FULL_PAIR_APPROVAL`; канон и журнал не записаны.
- Mechanical: `Skill is valid!`, `yaml-ok`, `link-target-ok`,
  `git diff --check` без вывода.

## Изоляция

`1use-principles` не менялся. Tracked owner, Codex/Claude projections и live
`1product-shaping` не менялись этим ремонтом; их попарные file SHA совпадают.
Установка не выполнялась.
