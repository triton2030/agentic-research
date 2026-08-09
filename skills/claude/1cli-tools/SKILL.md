---
name: 1cli-tools
description: >
  Use before building a helper, installing software, or doing repetitive manual
  work with Markdown, code, checks, UI/design, media/docs, data, security, or
  delivery: this Mac may already have a useful local tool. Inspect only the
  relevant capability and reuse it when it shortens the task. Skip when the
  project already fixes the tool and no choice remains.
---

# Local Tool Router

## Цель

До собственной реализации или ручной обработки проверить и переиспользовать
минимальную локальную возможность, которая заметно упрощает задачу пользователя.

## Критерии успеха

Считать успехом active tool и названную отменённую работу либо targeted
`no fit`, после которого основная задача продолжена без нового inventory.

## Инварианты

- Предпочитать project-local command и config глобальной копии.
- Не выводить из discovery разрешение на install, update, network или mutation.
- Не отдавать инструменту решение о смысле и приёмке результата.

## Дельта

- Markdown: `md`, `mdq`, `rg`, `fd`, `rumdl`, `markdownlint-cli2`, `lychee`.
- Код и зависимости: `ast-grep`, `graphify`, `depcruise`, `knip`.
- Проверки: JS/TS, Python, shell и CI toolchains уже установлены.
- UI и браузер: `impeccable`, `agent-browser`, `playwright`.
- Дизайн, медиа и документы: visual apps, Blender, FFmpeg, WebP, Poppler,
  LibreOffice.
- Данные и delivery: `jq`, `gron`, SQLite, `just`, `gh`, Vercel, Supabase.
- Security: secret, SAST, dependency и filesystem scanners уже доступны.

## Известные сбои

- неизвестна локальная возможность → пишется дубль или ставится package →
  лишняя работа → [tool-map](references/tool-map.md)
- имя или receipt принято за working tool → выбран неактивный binary →
  ложный старт → [runtime ownership](references/runtime-ownership.md)
- scanner выбран по названию → network, exposure или ложная remediation →
  [security scans](references/security-scans.md)

## Механика

1. Сопоставить задачу с одной строкой Дельты и открыть только нужную reference.
2. Проверить кандидатов через `command -v`, bundled `probe-tools.sh` и live help.
3. Выбрать минимальный подходящий инструмент и вернуться к основной задаче.

## Завершение

Вернуть `selected TOOL @ PATH → avoided work` либо `no fit`; не продолжать
поиск, если следующий probe уже не способен изменить выбор.
