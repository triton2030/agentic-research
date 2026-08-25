# Evidence — 1planning

## 2026-08-25 — planning-вопросы переданы `1interview-tool`

### Support envelope

- Target models: `GPT-5.6`, `Claude Opus 5`, `Claude Fable 5`.
- Harness: Codex desktop; shared portable owners с tracked и installed
  проекциями Codex/Claude.
- Инструменты: `sync_simple_projections.py`, системный `quick_validate.py`,
  `rumdl 0.2.57`, `md-tools 0.7.0`, read-only independent agents.
- Длина работы: planning-вопрос должен пережить смену сессии и вернуть ответ
  в настоящий owner результата.

### Claims и falsifiers

- **Одиночный planning-вопрос не умирает в чате.** Fresh-window probe получил
  один невыводимый вопрос, меняющий первый route, и выбрал
  `_ops/interviews/YYYY-MM-DD-topic.md` через `1interview-tool`; остановил
  только зависимую ветку. Тот же probe для одного ad hoc вопроса вне planning
  оставил ответ в чате и не создал форму.
- **Второй owner формы снят.** `portable/references/questions.md` удалён;
  поиск `questions.md`, `<questions folder>`, «Открытые вопросы» и «Вопросы ко
  мне» по live shared/tracked/installed пакетам вернул ноль. Все относительные
  Markdown-ссылки двух portable packages разрешились в существующие файлы.
- **Смысловой шов связен.** Прочитаны все прежние holders удалённого owner-а:
  `SKILL.md`, `map.md`, `modes.md`, `contract.md`, `decompose.md`,
  `delegation.md`. После коррекции владельца body держит один routing/branch
  gate; contract и map — только свои схемы, форма и lifecycle —
  `1interview-tool`. Architecture critic: `architecture_ok`; developer critic
  после recheck: `satisfied`.
- **Semantic compression.** До коррекции один routing-смысл имел носители в
  шести planning-файлах; после — только body, contract и map, причём общий
  гейт живёт лишь в body. Повторный fresh-window audit подтвердил оба исхода:
  planning-вопрос → interview-form и только затронутая ветка ждёт; ad hoc вне
  planning → чат.
- **Structure и distribution.** `quick_validate.py` прошёл для Codex и Claude
  пакетов; `rumdl` прошёл по 11 изменённым Markdown-файлам;
  `sync_simple_projections.py 1planning 1interview-tool --check` подтвердил
  byte-parity shared owner-а, tracked и installed проекций; `git diff --check`
  не нашёл whitespace defects.

### Ограничение evidence

`md impact` был вызван уже после удаления source-path и честно вернул
`path_not_found`; поэтому denominator удаления взят из pre-cut `rg`-поиска и
полного чтения шести live holders. `_workspace` snapshots и `skills/1planning/`
исключены как производные/архивные поверхности, а не live owners.
