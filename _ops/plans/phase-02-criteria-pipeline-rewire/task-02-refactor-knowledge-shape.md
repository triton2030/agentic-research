# Task 02 — Рефактор knowledge-shape

Статус: выполнено.

Применимые критерии:
- [`knowledge-maintenance`](../../criteria/knowledge-maintenance.md) — смысловая раскладка `knowledge/`, дубли, model-specific файлы.
- [`repo-shape`](../../criteria/repo-shape.md) — папки, owner surfaces, безопасные удаления и переносы.
- [`instruction-layer`](../../criteria/instruction-layer.md) — ссылки на knowledge/criteria из инструкций без копирования тел.
- [`work-review`](../../criteria/work-review.md) — проверка результата по observable evidence.

## Цель

Сделать `knowledge/` рабочей картой знаний: файлы названы под реальные случаи
жизни и задачи, папки отражают функцию знания, дубли схлопнуты в owner-файлы, а
модельные различия вынесены в отдельные файлы для `GPT-5.5` и актуальной
Claude Opus-версии.

## Подшаги

- [x] Снять инвентарь knowledge-файлов.
  EN: Build a file-by-file inventory with current role, proposed owner role, duplicate cluster, and action: keep, merge, move, delete, or defer.

- [x] Выбрать итоговую форму папок.
  EN: Define the minimal folder/file taxonomy for task-ready knowledge access without adding new surfaces that duplicate existing owners.

- [x] Схлопнуть дубли.
  EN: Merge duplicate meanings into one owner file per concept and preserve only missing useful substance from secondary files.

- [x] Разделить модельные знания.
  EN: Move real model-delta guidance into separate model-specific wisdom files for `GPT-5.5` and the confirmed Claude Opus version; keep shared advice only where behavior does not diverge.

- [x] Обновить маршруты чтения.
  EN: Update README/AGENTS/CLAUDE only where their reading routes must point to the new knowledge shape, without copying criteria or skill bodies.

- [x] Проверить свежую сессию.
  EN: Verify with file lists and targeted searches that a new agent can find the right knowledge file by task, model, and artifact type.

## Критерии приёмки

- `knowledge/` имеет понятную задачно-смысловую форму, а не историческую свалку.
- Каждый новый или сохранённый файл имеет одну функцию: wisdom, guide, practical guide, research, example или idea.
- Для каждого найденного дубля выбран один owner-файл; вторичные файлы удалены, объединены или явно отложены.
- Модельные различия не смешаны с общими правилами; версия Claude Opus не меняет canon без явного подтверждения.
- Root-инструкции и README дают только маршрут чтения, а не дублируют содержимое knowledge-файлов.
- Проверка включает `rg --files knowledge`, поиск дублей по ключевым темам и `git diff --stat`.

## Evidence

- User signal: нужны чёткие файлы под разные случаи жизни и задачи, логичные папки, уборка дублей, отдельные model-specific файлы.
- External check: official Anthropic release notes show `Claude Opus 4.5` on 2025-11-24 and `Claude Opus 4.7` on 2026-04-16 as the newer launch; the cleanup therefore keeps the Claude canon on `Claude Opus 4.7`.
- `rg --files knowledge _ops | sort` confirms the target tree: removed project archive, removed `_ignore-wip`, removed old phase-01 task folder, removed empty business/design/dev links files.
- Targeted `rg` checks were used for stale model strings, removed files, old surfaces, and empty-marker language.
- `git diff --stat` confirms this is mostly cleanup and deletion, with model and routing files updated instead of a new parallel system.
