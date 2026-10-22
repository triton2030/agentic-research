---
description: "История снятого Codex-скила recraft-images: генерация и правка изображений через Recraft в Codex."
---

# recraft-images — снят

Codex-скил снят 2026-10-22 при уборке скилов: в сессиях Codex ни одного
чтения `SKILL.md`, а каждый лишний скил в каталоге Codex укорачивает описания
остальных. Решение владельца — «ок удаляй».[^removal]

Был: Codex-вход в Recraft по прямой просьбе владельца. В Claude Code эту работу ведёт `1recraft`; папка `_workspace/design/recraft-images/`, куда он сохраняет картинки, со скилом не связана. До снятия tracked owner лежал в `skills/codex/recraft-images/`, вместе с `origin.md`, `cut.md` и `evidence.md` он перенесён в снимок.

- [`versions/retired-codex-2026-10-22/`](versions/retired-codex-2026-10-22/) —
  последний пакет; живого владельца и установленной копии нет.

Снимок хранит историю и не предназначен для запуска. Вернуть — скопировать
снимок в `~/.codex/skills/recraft-images/`.

[^removal]: [Слова владельца, 2026-10-22](../../_ops/chat-recall/2026-10-22-235727-claude-code-4acb96f5.md#recall-3dda27c2a5f24cc59d6753f758945166).
