# Checks — 112-learning-mode recheck — 2026-08-30

## Protocol identity

- Effective THREAD_CARD fingerprint:
  `9bf11f64b436d313d979cba822b684f502e8e40e5f15a12f78cbd914ca29a518`.
- Фактически установленный и полностью прочитанный
  `/Users/triton/.codex/skills/1skill-creation/SKILL.md`:
  `6e6b93e97eef2a31c8922ba8462a28a086c82ec80c6566c39ed63fc6bdc9f6a3`.
- Первый digest используется как внешний baseline-id поручения; совпадающих
  bytes в доступных projections/history не найдено. Смысловой live-протокол
  содержит требуемые FAST, clean-room, preservation, checker и probe стадии.

## Exact candidate

- `candidate/SKILL.md`:
  `9908cba1175e7d03c4dedaa9051cbd87fad389da3e2f2e7ce9a7d31d9d2adc0a`.
- `candidate/references/activation.md`:
  `7f9f42bd890d118655cbbadf729fa57eac6462a33a1735676c706cfcf34949a4`.
- Composition: ровно два ожидаемых файла.
- Cross-runtime YAML parse: PASS; exact English trigger-only description и
  `disable-model-invocation: true`: PASS.
- Русский instructional body/reference, локальная `## Цель`, link existence,
  отсутствие placeholders и `git diff --check`: PASS.
- Literal active-set acceptance: PASS, максимум 20.
- Trajectory acceptance: FAIL, один terminal residual в no-method ветке.

## Validator boundary

System `quick_validate.py` и `qv-skill` отвергают
`disable-model-invocation` как неизвестный ключ. Они так же отвергают unchanged
official baseline. Это известная несовместимость Codex-only schema с
Claude-native manual-only contract, уже зафиксированная в `../evidence.md`;
удаление ключа изменило бы утверждённое cross-runtime поведение. Локальный
cross-runtime YAML/content validator прошёл. Полный validator PASS поэтому не
заявляется.

## Official surfaces unchanged

Во всех пяти official owner/tracked/live packages сохранены одинаковые SHA:

- `SKILL.md`:
  `94606c3083f96262e7865b97e607060677028a2d2d15db5feb220cb9840b7793`;
- `references/activation.md`:
  `108032ccff06bb52a0dbf15dcca4a41df1be5458238848c2950d47773b3d8327`.

Проверены shared owner, tracked Claude, tracked Codex, live Claude и live
Codex. Candidate hash ни на одной official поверхности не установлен.
