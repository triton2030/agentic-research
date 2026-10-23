# Вход проверки — правки после логической проверки 2026-10-23

## Граница

Три правки, одобренные владельцем по итогам логической проверки
([logic-map.md](logic-map.md), разрыв Р1 и раздел «Итог сверки и атаки»):

1. Скил `1chat-recall`: исключение из порядка «сначала найти старую цитату»
   для реплики, которой владелец меняет инструкцию агентам, и справка
   `--supersedes-unresolved`, допускающая «не искали по правилу».
   Файлы: `skills/{claude,codex}/1chat-recall/references/capture.md`
   (раздел «Отношение к прежним словам») и `scripts/chat_capture.py`
   (`SUPERSESSION_GUIDANCE`, справка флага) — `git diff`.
2. Глобальная инструкция Codex: возвращены абзац «Пиши меньше…» (решение
   владельца `_ops/chat-recall/2026-09-26-231139-claude-fe013ec1.md:31`)
   и суженная строка о `$1findings` (решение
   `_ops/chat-recall/2026-09-27-143633-claude-a3f57bdb.md:75`, текст —
   `skills/1instruction-authoring/work/codex-global-2026-09-27/after.md:57-58`).
3. Обе глобальные инструкции: последняя фраза абзаца о записи сведена в одну,
   соединяющую прежние формулировки Claude и Codex.

Глобальные правки 2–3: `skills/1instruction-authoring/work/claude-global-2026-10-23-v3/`
и `codex-global-2026-10-23-v3/` — `original.md` против `after.md`.

## Основания

- Глобальное правило: `skills/1instruction-authoring/work/claude-global-2026-10-23-v3/original.md:16-23`
  («Читай их через `1chat-recall` перед правкой, которая может отменить моё
  прежнее решение…», «Инструкции агентам цитаты не защищают: их меняет моё
  текущее слово, без поиска прежних цитат и без развилки»).
- Порядок скила: `skills/claude/1chat-recall/references/capture.md:110`.
- Helper требует ответ о связи у позиции; `--supersedes-unresolved` раньше
  значил только «не найдено после поиска».

## Контракт

`~/.claude/skills/1skill-creation/SKILL.md`,
`~/.claude/skills/1agent-steering/references/steering-science.md`.
Тесты `tests.test_chat_capture`: 59 OK в обоих рантаймах после правки.
