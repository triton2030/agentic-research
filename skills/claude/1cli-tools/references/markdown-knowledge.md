---
description: "Локальный md-tools для больших Markdown-корпусов и связанного знания."
---

# Markdown И Project Knowledge

Момент: выбирается операция над большим Markdown corpus. Сверено 2026-08-19 с
`md-tools 0.7.0`; быстрее всего меняются catalog/signatures. Это локальный
продукт, его контракт нельзя восстановить из имени `md`.

## Сначала Спроси Сам Инструмент

```bash
md --version
md tools --json
md tools TOOL_NAME --json
```

`md tools TOOL_NAME --json` — владелец назначения, canonical signature и output
contract. Не угадывай аргументы и не разбирай JSON по памяти.

## Маршруты, Которых Нет В Обычном Markdown Toolchain

| Решение | Команда |
|---|---|
| войти в незнакомый corpus без чтения всех файлов | `md orient CORPUS --json` |
| найти claim по смыслу | `md search CORPUS --query QUERY --json` |
| выбрать heading, затем получить только нужное тело | `md toc FILE --json` → `md extract ... --json` |
| собрать owner context до правки | `md edit-context FILE --json` |
| оценить удаление/перемещение файла | `md impact PATH --scan CORPUS --json` |
| оценить переписывание heading/section | `md section-blast-radius ... --json` |
| проверить нормативный claim против canon | `md canon-check ... --json` |
| проверить поток мысли с раскрытием anchored wikilinks | `md coherence-audit ... --json` |
| проверить freshness semantic index | `md status CORPUS --json` |

`md search --rerank` обращается к внешнему reranker и сообщает примерную цену.
`orient --expanded` возвращает явную полную filesystem map вместо обычного
ограниченного view.

Решения о многом чтении, semantic search и dependency impact принадлежат
`1md-read`, `1md-search` и `1md-graph`; здесь хранится только карта неизвестного
локального CLI.
