---
name: 1cli-tools
description: >
  Use when repo/tooling decisions need terminal evidence: active binary owner,
  exact text/path/symbol refs, JSON shape, update or security scan. Markdown
  meaning → 1md-navigator; graph → 1md-graph; not browser/visual QA.
---

# CLI Evidence

## Результат

Верни проверяемый evidence packet:

- claim: на какой вопрос отвечает probe;
- scope: cwd, paths, exclusions и выбранный runtime;
- command + active owner: что именно запущено и откуда;
- evidence class и наблюдаемый результат;
- gaps, side effects и следующий owner.

Команда доказывает только свой слой. Manager receipt не доказывает active
binary; text match не доказывает semantic owner; analyzer finding не даёт
permission на delete/rename.

## Границы

- Markdown meaning, canon, owner, corpus discovery и index lifecycle →
  `1md-navigator`.
- `depends-on`, holders, anchors, cycles, wikilinks и graph impact →
  `1md-graph`.
- Browser interaction, screenshot и visual assertions → профильный browser /
  frontend skill.
- Install/update, network probe, codemod, delete/move/rename, cache download и
  mutating LSP action требуют явного покрытия запросом.

Название команды не гарантирует read-only. `outdated`, `doctor`, `dry-run`,
`cache verify` и даже некоторые `list/root` могут обновить metadata, repair
cache или создать directories.

## Default Path

1. Сформулируй один claim и минимальный scope. До команды назови, какой output
   подтвердит или опровергнет claim.
2. Выбери минимальные handles. Targeted presence/owner probe:

   ```bash
   bash ~/.claude/skills/1cli-tools/scripts/probe-tools.sh rg sg tsc
   ```

   Для package CLI сначала подтверди local owner (`node_modules/.bin`) и
   запускай `pnpm exec` из package root, затем рассматривай global binary.
   `npm exec`/`npx`/`uvx` могут скачать package/cache и не являются harmless
   fallback без подтверждённого local receipt.
3. Загрузи только нужную ветку:
   - exact strings/paths/counts/JSON, symbol/refactor, syntax и analyzer
     candidates →
     [`references/exact-and-code-evidence.md`](references/exact-and-code-evidence.md);
   - PATH owner, versions, update или explicit machine-wide audit →
     [`references/runtime-ownership.md`](references/runtime-ownership.md);
   - secrets, vulnerabilities, SAST или native supply chain →
     [`references/security-scans.md`](references/security-scans.md).
4. Перед редким flag проверь `<tool> --help`; перед schema-dependent parsing —
   live JSON keys/schema. Для `md`: `md tools <command> --json` для machine
   contract, `md <command> --help` для human flags. Live surface сильнее
   reference.
5. Запусти узкий probe. Для delete/rename/codemod нужны два независимых
   сигнала либо runtime/test confirmation.
6. Сообщи фактические side effects, в том числе automatic cache/index repair.

## Evidence Classes

- `derived`: exact CLI fact (`rg`, `fd`, `sg`, parsed JSON field);
- `inferred`: analyzer/scanner candidate (`knip`, `depcruise`, SAST);
- `semantic`: ranked search candidate или navigator packet;
- `runtime`: реально выполненная command/test/health check.

`inferred` и `semantic` требуют cross-check перед необратимым действием.
Secret-scanner finding остаётся candidate даже если verifier принял credential:
owner/scope и rotate/revoke — отдельные решения.

## Стоп

Стоп, когда claim получил адресуемый результат; scope, active owner, command и
evidence class названы; side effects и residual risk не скрыты. Не расширяй
probe до inventory всей машины, если исходный вопрос уже закрыт.
