---
description: 'ADR-0002: md extract до-читывает headings с диска, развязывая его от
  формы ls/orient карты.'
depends-on:
- '[[0001-agent-view-output-projection.md]]'
---
# ADR-0002 — `md extract` до-читывает headings с диска

- **Статус:** Accepted
- **Дата:** 2026-05-31

## Контекст

`md extract` потребляет вывод `md ls` / `md orient` как `map_data` и требовал
поле `headings` в каждом файле карты (`navigator.pick`). Это **блокировало**
bounded-дефолт `md ls` из ADR-0001: при удалении heading-деревьев из карты ради
компактности `md extract --files X` падал с `KeyError: 'headings'`, ломая
selftest и smoke-пайплайн `ls → extract`.

## Решение

`navigator.pick._ensure_headings` до-читывает per-file headings с диска по `path`,
когда карта их не несёт, присваивая ID по схеме `build_map` (`<file_id>.<idx>`).
Доступы к `headings` в `pick` стали толерантными (`.get("headings", [])`). Так
`md extract` работает на **любой** карте — lean или полной — и больше не зависит
от того, несёт ли карта heading-деревья.

2026-06-18 уточнение границы: `pick` остаётся adapter-ом выбора file/heading ids
и token budget, а чтение heading-bounded section body (`extract_section_by_line`)
принадлежит `navigator.markdown_io`. Это сохраняет решение ADR-0002, но переносит
семантику границ секций в тот же deep module, который владеет Markdown parsing.

## Последствия

- `md ls` non-expanded дефолт теперь сбрасывает heading-деревья (ADR-0001);
  полные headings — через `--expanded` / `md toc`.
- `MAP_SCHEMA` file-item: `headings` стало optional (не required).
- `extract` развязан от формы карты: единственный источник headings — диск, а не
  дублирование в каждой карте. Архитектурно чище и устойчивее к будущим
  изменениям формы `ls`/`orient`.
- Границы извлекаемого тела секции теперь едины для `extract`, `read-related`
  anchor-aware, `walk` и `coherence-audit`: все идут через `markdown_io`.
- `semantic-neighbors` не становится новым `map_data` owner-ом для `extract`:
  его candidate rows раскрываются собственным payload-level `read_next`.
