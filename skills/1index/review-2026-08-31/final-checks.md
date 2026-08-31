# Финальная проверка exact candidate

## Exact input

- `SKILL.md` — `72356b3f8889224418d60e02a5e967acda8e3195e32eaf467171cdc7416f4b1d`;
- Codex metadata — `4f4f7c3f8159ba19f2249680a0ec5296f0123db073d15553d803981c648116e7`;
- package manifest — `038b1bc85d54a2fe2d7e6d8348c0c75363d6e9678383fe7e5b415095c2128af4`.

Manifest воспроизводится как SHA-256 вывода `shasum -a 256` для двух exact
package files в порядке `SKILL.md`, `platforms/codex/agents/openai.yaml`.

## Механика

- System `quick_validate.py`: PASS.
- Codex YAML parse: PASS.
- Frontmatter description и Codex `short_description`: exact parity, 95
  символов, одна English trigger-only фраза.
- `default_prompt` явно вызывает `$1index`; metadata SHA не изменился.
- Внутренних Markdown links в runtime нет; недоступных references нет.
- Official owner, tracked Codex/Claude и обе live projections не менялись и
  по-прежнему совпадают между собой.

## Независимые проверки

- Wave 1 trajectory: PASS на multi-source holdout; obvious near-miss отклонён,
  missing INDEX дал proposal.
- Wave 1 literal: приняты line separation и точный missing-INDEX object;
  конфликт generic description-template отклонён по прямому owner-решению.
- Wave 2 trajectory: PASS после смыслового сжатия и authority repair.
- Wave 2 literal: semantic defects отсутствуют; приняты только разнесение
  independently violable predicates и исправление source address.

После wave 2 изменилось только представление уже проверенных predicates:
route schema отображена строками 26–28, one-hop — 29–30, placement — 31–32,
missing-INDEX authority — 33–35. Нового решения, порядка или выхода не
появилось, поэтому trajectory evidence причинно сохраняется. Основной агент
проверил точные финальные байты и эту one-to-one карту.

## Complexity

Честный literal active set остаётся `33` для body и `38` на Codex path.
Ориентир `20` превышен, но checker признал его мягким residual, а дальнейшее
удаление затронет одну из трёх owner-целей, два admission-входа, per-source
границу, exact route, one-hop либо authority. References и стадии не созданы.

Terminal verdict: **PASS / exact candidate ready for owner approval**.
