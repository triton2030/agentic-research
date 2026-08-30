# Source basis повторной проверки

## Состояние до нового намерения

До формирования `intent-2026-08-30-v4.md` были полностью прочитаны старый
package, история, live projections и новый authoring contract. Наблюдаемое
состояние после чтения: `нужен новый commander's intent`; старый текст является
только evidence и не задаёт форму следующего candidate.

## Старый package и live baseline

- Official owner: `skills/claude/1local-rules/SKILL.md` — SHA-256
  `16e3b0e3c8017cbbb875842f0c5640200c7d810106f7a2103df0eb0911de3f01`.
- Claude live: `/Users/triton/.claude/skills/1local-rules/SKILL.md` — тот же
  SHA-256.
- Codex live: `/Users/triton/.codex/skills/1local-rules/SKILL.md` — тот же
  SHA-256.
- Codex runtime metadata:
  `/Users/triton/.codex/skills/1local-rules/agents/openai.yaml` — SHA-256
  `9455f25c3d8293c455e2915c8632d5db872f92e1d5092451d4e6eab3ee698c68`.
- Composite baseline fingerprint из `THREAD_CARD`:
  `9bf11f64b436d313d979cba822b684f502e8e40e5f15a12f78cbd914ca29a518`;
  способ композиции в карточке не задан, поэтому сохранность дополнительно
  проверяется адресными file hashes и отсутствием target diff.

## История, прочитанная полностью

- `skills/1local-rules/origin.md`, `cut.md`, `evidence.md`;
- `draft-2026-08-30/SKILL.md` и его `references/admission.md`,
  `behavior-proof.md`, `candidate-checks.md`, `form.md`, `install.md`,
  `retire.md`;
- `draft-2026-08-30-v2/SKILL.md` и его `references/conflict.md`,
  `references/sync.md`;
- `draft-2026-08-30-v3/SKILL.md`.

## Новый управляющий контракт

Полностью прочитаны `$1skill-creation`, `references/refactor.md`,
`goal-context.md`, `skill-short-description.md`, `behavior-protocol.md`,
`reference-files.md`, `agent-defaults.md`, `check-approve.md`,
`install-approved.md`, а также оба checker-role файла. Product Frame проекта,
Product Principles, `knowledge/wisdom-skills-plugins.md` и входной guide
написания skills прочитаны до продуктового суждения.

После этого состояния создан новый intent, переданный clean-room исполнителю
без старого package и history.
