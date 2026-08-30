# 1local-rules v5: карта owner и установки

Статус: топология подготовлена; owner, tracked projections и installed
projections в этой работе не изменялись.

## Решение

Единственный source owner пакета должен стать shared-owner:
`skills/shared/1local-rules/`. Общий контракт Claude и Codex живёт в
`portable/SKILL.md`; существующая Codex UI metadata — единственная runtime-
дельта и живёт в `platforms/codex/agents/openai.yaml`.

Два независимых runtime owner-а отвергнуты: утверждённый `SKILL.md` побайтово
общий, а дублирование создаст две редактируемые истины без различия поведения.
Новый sync, package README, manifest, reference-файлы и symlink-слой не нужны:
generic `skills/shared/sync_simple_projections.py` уже собирает эту форму и
останавливается на неожиданных файлах.

## Точная будущая топология

| Роль | Путь | SHA-256 после cutover |
| --- | --- | --- |
| source owner, общий контракт | `skills/shared/1local-rules/portable/SKILL.md` | `c4982fe302d9e2e3ae3d64dd13fe90be6b02a937132bd5b7c2a8efeb90bf61b0` |
| source owner, Codex UI delta | `skills/shared/1local-rules/platforms/codex/agents/openai.yaml` | `9455f25c3d8293c455e2915c8632d5db872f92e1d5092451d4e6eab3ee698c68` |
| tracked Claude projection | `skills/claude/1local-rules/SKILL.md` | `c4982fe302d9e2e3ae3d64dd13fe90be6b02a937132bd5b7c2a8efeb90bf61b0` |
| tracked Codex projection | `skills/codex/1local-rules/SKILL.md` | `c4982fe302d9e2e3ae3d64dd13fe90be6b02a937132bd5b7c2a8efeb90bf61b0` |
| tracked Codex UI projection | `skills/codex/1local-rules/agents/openai.yaml` | `9455f25c3d8293c455e2915c8632d5db872f92e1d5092451d4e6eab3ee698c68` |
| installed Claude projection | `~/.claude/skills/1local-rules/SKILL.md` | `c4982fe302d9e2e3ae3d64dd13fe90be6b02a937132bd5b7c2a8efeb90bf61b0` |
| installed Codex projection | `~/.codex/skills/1local-rules/SKILL.md` | `c4982fe302d9e2e3ae3d64dd13fe90be6b02a937132bd5b7c2a8efeb90bf61b0` |
| installed Codex UI projection | `~/.codex/skills/1local-rules/agents/openai.yaml` | `9455f25c3d8293c455e2915c8632d5db872f92e1d5092451d4e6eab3ee698c68` |

Источники байтов для cutover лежат в history-candidate, а не в live:
`skills/1local-rules/draft-2026-08-30-v5/SKILL.md` и
`skills/1local-rules/draft-2026-08-30-v5/agents/openai.yaml`. Metadata побайтово
равна текущей Codex projection, но live-файл остаётся только
evidence и не становится owner-ом.

Claude projection намеренно не содержит `agents/openai.yaml`: это Codex-only
UI metadata, а не переносимое поведение.

## Атомарный cutover

1. Одним изменением создать оба source-файла shared-owner и добавить
   `1local-rules/portable/` в реестр `skills/shared/README.md`.
2. Запустить:

   ```bash
   python3 skills/shared/sync_simple_projections.py 1local-rules --write --install
   python3 skills/shared/sync_simple_projections.py 1local-rules --check
   ```

3. Отдельно подтвердить наличие обеих tracked и обеих installed целей и
   сверить их с хэшами таблицы.

До cutover текущий check не является parity-доказательством: он проверяет
Claude runtime-owner и печатает `skipped codex/1local-rules: owner отсутствует`.
После появления shared-owner такое пропускание недопустимо.

## Стоп-условия

- Не продолжать при отклонении утверждённого SHA `SKILL.md`.
- Не продолжать при изменении SHA Codex metadata без отдельной проверки.
- Не продолжать, если owner и запись реестра не входят в одно изменение.
- Не удалять неожиданные projection-файлы; generic sync обязан остановиться.
- Не считать установку завершённой, пока финальный `--check` не охватил Claude
  и Codex без `skipped` и все восемь путей не совпали с таблицей.

Оставшаяся сложность — только shared-owner и одна Codex UI delta. Удаление
shared-owner вернёт две редактируемые истины; удаление runtime-дельты потеряет
Codex UI/invocation metadata. Остальные стадии и файлы поглощены существующим
generic sync-контрактом.
