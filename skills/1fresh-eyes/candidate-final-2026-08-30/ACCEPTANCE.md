# Acceptance — exact final candidate

## Identity

Package fingerprint — SHA-256 exact manifest bytes:

- Claude: `012fb65c07e40cd12302a7fe1475dbd4ae9293f1d67aed2de662cfc8ecc22a00`.
- Codex: `9f69a1c113d5b765564f2862256b53de54269ad264417b4d06a8fe7b92f32351`.
- Repaired `references/packet.md`: `59e0711ab502cda49fd0f08349f06fb52d7615170c6f523d438833913bb432b3` в обоих пакетах.

Manifests: [`manifest-claude.sha256`](manifest-claude.sha256) · [`manifest-codex.sha256`](manifest-codex.sha256).

## Terminal evidence

- Instruction checker: `pass`, findings `[]` — [`receipts/instruction-check.raw.md`](receipts/instruction-check.raw.md).
- Trajectory checker: `pass`, findings `[]` — [`receipts/trajectory-check.raw.md`](receipts/trajectory-check.raw.md).
- Realistic packet probe: `packet_probe_pass` — [`receipts/packet-probe.raw.md`](receipts/packet-probe.raw.md).

## Active sets

`anchor 8 · packet 15 · named 16 · named-correction 20 · premortem 20 · panel 19 · panel-correction 20 · synthesis 15`.

## Scope

Candidate отличается от текущих tracked/live packages только одной одинаковой строкой в `claude/references/packet.md` и `codex/references/packet.md`.

Tracked owners и live projections не изменены. Установка закрыта до нового безусловного approval этих exact bytes.
