# Контекст — 1html visual explainer

## Проблема

Owner evidence —
`../../chat-recall/2026-08-19-212344-codex-01a01ad4.md:22-41`.

## Ожидаемый эффект

Новая сессия быстрее доводит сложный материал до наглядного автономного
объяснения: одна folder-level stance задаёт отношение к работе, shared zone
снимает повторное копирование libraries/components, а mandatory QA-loop
отсутствует.

## Отпавшие ходы

- Общий editorial template/preset: отменён owner-correction о design freedom.
- Source-lint красоты: не различает намеренный дизайн и визуальную ошибку.
- React Flow, который стилизует каждую node как одну большую card: отменён
  owner-correction о полной свободе содержимого nodes.
- React Flow с dev server/CDN: запрещён offline/file contract.
- Data charts без реальных чисел: создают ложную измеримость.
- Per-artifact bundle с собственной копией `lib/assets`: отменён прямой
  owner-correction об одной общей папке для множества HTML.
- Общая инструкция в каждом artifact: неверное прочтение; owner просил одну
  instruction на shared HTML_artifacts zone.

## Живой Потребитель

`/Users/triton/Documents/My_projects/mavo-short2/_workspace/HTML_artifacts/`
до миграции хранил отдельные копии runtime у каталога и WhatsApp artifact.
Теперь это одна flat/shared zone; CSS страницы и её тёплый visual language не
изменены, а старый directory URL сохранён compatibility redirect-ом.
