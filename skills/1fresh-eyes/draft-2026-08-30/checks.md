# Checks — 1fresh-eyes candidate — 2026-08-30

## Exact identity

- Immutable `1skill-creation` baseline:
  `9bf11f64b436d313d979cba822b684f502e8e40e5f15a12f78cbd914ca29a518`.
- Current candidate:
  `822c05f430116642ccf203b391a5e80875497b53106d720bc204b5eb839d3daf`.
- Contract: SHA-256 of sorted SHA-256 manifest for `claude/**`, `codex/**` and
  `product-frame.md`.

```text
46736b1a3d123a92a24471ecf872871e3487b309a63745c5c99b730b02245782  claude/SKILL.md
fb5af443815e16d3cf71388b91f0d88ea975bd40978fdac81b20cf3998193e37  claude/references/packet.md
65adc8616093830a79097ed965447ce18d630d4cc9add907e624adcecee8e6a6  claude/references/panel.md
44f4733731f6b504307efb7d971927ce1cb1fd3328309dc67c963bc9119dbee0  claude/references/premortem.md
0f9ea297d0a5d48fb9b041c0a23c33438f8e403d52651d2bc5956ef0ada33d7e  claude/references/steering.md
63f88c6cc60376fe5f1562facb1c9542f6e2dc398503d7d482f68452ca49bc55  claude/references/synthesis.md
51f825870ce2be217fea186f40d459573b94208738d3f01cd209289ac24c50b7  codex/SKILL.md
3ac87a7356886c8fe8645948a9b8be07939fbe9a9e7b89a4601905954ae57b5b  codex/agents/openai.yaml
fb5af443815e16d3cf71388b91f0d88ea975bd40978fdac81b20cf3998193e37  codex/references/packet.md
fb227c646f148fdf6925bdda93cd874c3a5c95cb8ca9d3df459a2e68d8a739a1  codex/references/panel.md
dc075968502c9f770b87e2c742d615b79389d9a7571bbc30d6bcd1d40f340ead  codex/references/premortem.md
ce3c528d41c0c5bd66636325f327e7ea984b0fa884a920af7fa783239e7d4864  codex/references/steering.md
63f88c6cc60376fe5f1562facb1c9542f6e2dc398503d7d482f68452ca49bc55  codex/references/synthesis.md
78404cedace5b26e31802296033e22c8b9956fbad665d975e8bc513ca2cec31f  product-frame.md
```

## Structural checks

- Pre-repeat `qv-skill` and system `quick_validate.py`: pass, Claude/Codex.
- YAML: 13/13; relative links: 12/12; `git diff --check`: pass.
- Russian instructional prose; English trigger-only descriptions.
- Runtime topology: five substantive references in each form; no `named.md`.
- Tracked owners and installed projections remain outside candidate writes.

## Active sets — independently confirmed

| Mode/stage | Claude | Codex |
|---|---:|---:|
| Admission | 19 | 19 |
| Neutralize panel | 19 | 19 |
| Neutralize named | 16 | 16 |
| Named run | 10 | 10 |
| Cross-family | 20 | 20 |
| Native panel | 15 | 14 |
| Correction native | 15 | 17 |
| Correction cross-family | 15 | 15 |
| Handback | 17 | 18 |

No new stage/reference was added to reach 20. Reduction came from removing
common context duplication and the duplicated named/panel correction route.

## Behavioral evidence

- Exact precursor `19def…`: complete four-report panel with Opus 5 receipt,
  three clean native agents, one same-stream correction and non-voting handback
  in `panel-run-19def.md`.
- First review of compressed `65628…`: trajectory findings none; instruction
  findings resolved into `c66d6…`, except rejected quote duplication.
- Instruction repeat `c66d6…` found three scope clarifications, resolved into
  exact `822c0…` without new active units.
- Exact `822c0…`: trajectory checker и instruction checker завершились без
  находок; оба независимо проверяли точную финальную версию.
- Installation: not performed.

Текущая owner-последовательность — completed real panel → semantic reduction →
two exact independent checks — завершена. Дополнительный exact panel run был
остановлен как третье, не требуемое доказательство.
