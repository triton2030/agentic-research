# Строгий clean-room trace

Статус: `superseded process trace`, не candidate и не approval.

## Изоляция

- Исполнитель: `/root/strict_clean_room`, новое окно с `fork_turns=none`.
- Ему запрещено читать любые файлы и менять filesystem.
- В prompt не было путей, старого пакета, history, tests, CLI, schemas,
  reviews, source basis, FAST-tree, hard-lines или active-set hints.
- Содержательный вход состоял из «Уникального контекста», трёх целей, момента
  вызова и не-успеха. Это всё ещё шире буквального контракта «только уникальный
  контекст и цели»; исправляющий проход записан в
  [intent-only-clean-room.md](intent-only-clean-room.md).

## Методы и независимый результат

Исполнитель буквально применил `Clean-room reimplementation` и `Zero-based
design`, начал с пустого пакета и независимо вернул:

```text
1chat-recall/
├── SKILL.md
└── references/
    ├── capture.md
    ├── retrieval.md
    └── repair.md
```

Его semantic draft без runtime knowledge вывел:

- same-turn literal Capture;
- полную карту тем до classification;
- keyword-like context вместо повествовательного summary;
- атомарную evidence-единицу с адресом;
- decision-scoped Retrieval, chronology, coverage, live semantic owner и
  нормальное воздержание;
- запрет profile/general summary/permission;
- immutable evidence и Repair/Backfill/Validation/Restoration;
- полный Capture для каждой восстановленной материальной цитаты;
- restoration только в existing semantic owner.

Точные runtime roots, schema, transaction, search, address, source locator,
validator и owner-update contracts исполнитель оставил gaps, а не выдумал.

## Loss-check и принятая дельта

Старый пакет после полного clean draft доказал две самостоятельные runtime
стадии: Restoration и structural Validation. Recovery не имел отдельного
результата и после simplicity-фальсификатора поглощён условным блоком Retrieval.
Прямую
Repair→Capture reference-chain clean draft заменил packet→body-router→Capture,
чтобы в один момент оставался активен один reference.

Первоначальный вердикт `accepted` отозван буквальным checker-ом. Слот остаётся
полезным evidence, но не закрывает обязательный clean-room критерий.
