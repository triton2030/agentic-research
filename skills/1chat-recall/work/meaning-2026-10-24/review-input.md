# Вход проверки — смена смысла 1chat-recall, 2026-10-24

## Граница заказа

По решению владельца 2026-10-24:

1. Корпус — контекст того, как владелец думал, а не канон и не поиск его прежних
   решений; действующее живёт в документах проекта, инструкциях и текущем
   разговоре. Поиск старой цитаты перед записью и обязательный ответ «что
   отменяет» сняты; связь ставится, только если адрес уже известен.
2. Текст скила переведён на английский, построен по условиям «когда делаешь X —
   делай Y», очевидное для сильной модели убрано. Примеры реплик владельца
   остаются по-русски.
3. В корневых (глобальных) инструкциях сказано, что цитаты владельца — не канон.

Сохраняются: отбор по мерилу будущего выбора, `selection` вместо «окей»,
перезапись записи текущего разговора, дословность.

## Что читать

- Черновик скила: `skills/1chat-recall/work/meaning-2026-10-24/draft/claude/`
  (`SKILL.md`, `references/capture.md`, `retrieval.md`, `integrity.md`,
  `search-mechanics.md`); `draft/codex/` отличается рантайм-строками.
- Прежняя редакция (русская): `skills/claude/1chat-recall/` — тексты там ещё
  прежние; helper `scripts/chat_capture.py` уже без обязательного ответа о связи
  (`git diff`), тест в `tests/test_chat_capture.py` переписан.
- Продуктовая рамка: `skills/shared/1chat-recall/product-frame.md` (`git diff`).
- Папочные инструкции корпуса: `_ops/AGENTS.md`, `_ops/chat-recall/AGENTS.md`
  (`git diff`).
- Глобальные инструкции: `skills/1instruction-authoring/work/claude-global-2026-10-24/`
  и `codex-global-2026-10-24/` — `original.md` против `after.md`.
- Слова владельца: `_ops/chat-recall/2026-10-22-195852-claude-code-83f01dd5.md`,
  записи `#recall-3533827af6044f6bb85688933e44823a`,
  `#recall-06676b2f90904567bab2bca560a4d636`,
  `#recall-7cf15098882e41ef9062f4ee89929e43`,
  `#recall-c4f250ec16554aeeb80d6da69d386555`.
- Контракт: `~/.claude/skills/1skill-creation/SKILL.md`,
  `~/.claude/skills/1agent-steering/references/steering-science.md`.

## Evidence

Тесты всех `tests/test_*.py` на пакетах с черновыми текстами: Claude 183 OK,
Codex 186 OK. Пробы — `probe-result.md` рядом, когда появится.
