# Origin

## Владелец

- Исходная проблема, переход от hook к self-invoked skill, требование видимого
  когнитивного следа и выбор независимой модели сохранены в
  `_ops/chat-recall/2026-08-22-060958-codex-01a02701.md`.
- Порог изменён владельцем с трёх на каждые пять ещё не разобранных собственных
  `⚡ UNEXPECTED`, чтобы не вызывать skill лишний раз.
- Полный runtime-кандидат и Product Frame утверждены владельцем командой
  `делай` 2026-08-22 после предъявления точных замен для порога 5.
- 2026-08-31 владелец отменил self-invocation: `1model-check` вызывается только
  вручную и должен быть доступен в Claude и Codex. Источник —
  `_ops/chat-recall/2026-08-31-155258-codex-01a0576e.md#L16`.

## Механизм

`явный вызов → до пяти prediction errors → адресуемые ожидание/наблюдение → компактная рабочая
модель или честный gap → различающий probe → evidence-bound следующее действие`.

Skill-specific product truth и runtime-contract живут в этой папке.
`skills/claude/1model-check/` — paired runtime owner;
`~/.{codex,claude}/skills/1model-check/` — установленные projections.

## Исследовательские границы

- [Role relabeling](https://arxiv.org/abs/2606.05976) повышает explicit
  addressability собственных ошибок, но не доказало улучшение итоговой
  точности.
- [Targeted environment probing](https://arxiv.org/abs/2606.31422) может
  улучшать world-state accuracy; словесная uncertainty ненадёжна.
- [Compact causal repair](https://arxiv.org/abs/2607.01767) проверен в planning
  graphs и перенесён сюда только как эвристика компактного объяснения.
- [Metacognitive monitoring](https://arxiv.org/abs/2607.11881) ценно вместе с
  control action.
- [Training/reward evidence](https://arxiv.org/abs/2605.23384) не доказывает
  prompt-only effect.
