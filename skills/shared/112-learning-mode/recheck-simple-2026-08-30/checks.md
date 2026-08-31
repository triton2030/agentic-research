# Checks — простая candidate 112-learning-mode

## Candidate

- Path: `candidate/SKILL.md`.
- SHA-256:
  `5084d6b2458b528623d4d56e057e1dc2e5d050cf21890c78b160a52a8789e252`.
- Composition: один `SKILL.md`, references и agents отсутствуют.
- Active set: 20 по независимому literal recount.
- Exact English trigger-only description: PASS.
- Hard manual flag: PASS.
- Всё instructional body после frontmatter на русском: PASS.
- YAML parse, placeholders и `git diff --check`: PASS.
- Final trajectory и behavioral probe exact SHA: PASS.

## Validator boundary

Cross-runtime YAML/content check проходит. System `quick_validate.py` по-прежнему
отвергает `disable-model-invocation`: тот же Codex-only schema conflict
возникает на unchanged official baseline. Удаление Claude-native manual flag
изменило бы утверждённое поведение; platform split не добавлялся без отдельного
owner-решения.

## Official surfaces unchanged

Shared owner, tracked Claude/Codex и live Claude/Codex сохраняют byte parity:

- `SKILL.md`:
  `94606c3083f96262e7865b97e607060677028a2d2d15db5feb220cb9840b7793`;
- `references/activation.md`:
  `108032ccff06bb52a0dbf15dcca4a41df1be5458238848c2950d47773b3d8327`.

Candidate не записан ни на одну official или live поверхность.
