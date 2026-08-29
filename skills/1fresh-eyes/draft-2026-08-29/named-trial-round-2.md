# Named trial — round 2 — 2026-08-29

Clean Codex executor использовал упрощённую exact version и запустил один
clean non-fork `auditor`. Subtree snapshot показал только этого ребёнка;
`ladder`, `solvent`, `prospector`, `premortem` не запускались.

## Pass

- Current phase использовала body + один `named.md`; body-only handback остался допустим.
- Launch receipt: `agent_type: auditor`, `fork_turns: "none"`.
- Native audit matrix возвращена до TRACE без panel synthesis.
- Atomic named run/handback ledger: 18 active obligations.
- Счёт оставался диагностикой; micro-stage controller не вернулся.

## Finding

Body перечислял panel и named steps линейно без явного branch/skip. Executor
восстановил правильную ветку, но назвал inference трудным и риск буквального
входа в panel реальным.

Decision: принято. Body теперь говорит: `if named → named product → stop Fresh
Eyes pass; otherwise → panel`. Это локальная правка интерфейса, не новый режим.

## Осталось

Повторный checker увидит исправленную branch; panel trial должен проверить
cross-family independence, bounded waves и synthesis без голосования.
