# Intent-only clean-room trace

Статус: `accepted semantic input`, не candidate и не approval.

## Изоляция

- Исполнитель: `/root/intent_only_clean_room`, новое окно с `fork_turns=none`.
- Ему запрещено читать filesystem, прежний пакет, history, CLI, schemas и
  reviews.
- Единственный содержательный вход — `intent.md:38-59`: «Уникальный контекст» и
  три «Цели пользователя». Момент вызова, не-успех, FAST и hard-lines не
  передавались.

## Zero-based результат

Исполнитель начал с пустого пакета и независимо вернул минимальную topology:

```text
SKILL.md
references/
  capture.md
  recall.md
  integrity.md
```

- Capture объединяет новую и восстановленную речь одним контрактом; без него
  backfill теряет одинаковую provenance-границу.
- Recall отделяет historical evidence от применимой текущей позиции; без него
  старая цитата становится текущей правдой или скрывает неполный coverage.
- Integrity объединяет validation, Repair/backfill и границу existing owner;
  без него repair может переписать слова или обойти Capture.

Точный storage, CLI, source locator, transaction и live-owner resolver
исполнитель оставил runtime gaps, а не выдумал. Candidate сохранил три
reference-файла; самостоятельный Restoration после Fresh Eyes снят, потому что
его authority уже принадлежит исходной работе, а граница evidence/current truth
осталась в body и Retrieval.

## Active set clean-room

Router держит только `SKILL.md`; Capture и Retrieval — body плюс один reference;
Repair/backfill — body плюс Integrity, затем terminal `capture-needed` освобождает
Integrity и возвращает body плюс Capture. Ни один runtime-момент не требует все
references одновременно.
