---
description: Agent jobs and moments that md-tools-v2 must support.
depends-on:
- '[[current-skill-usage-map.md]]'
- '[[minimum-document-set.md]]'
---
# Jobs And Moments

Этот документ переводит список функций в рабочие моменты агента.

Функция нужна не потому, что она существует в текущем backend. Она нужна,
если закрывает конкретный момент работы скила.

## Минимальные Моменты

| Момент | Что нужно агенту | Примеры текущих tools |
|---|---|---|
| Cold start по Markdown-папке | Понять карту файлов, описания, важные узлы | `md_orient`, `md_ls`, `md_importance` |
| Найти смысл | Найти секции по естественному запросу | `md_search`, `md_extract` |
| Прочитать соседний контекст | Увидеть linked / related context без лишнего корпуса | `md_read_related` |
| Подготовить правку `.md` | Понять обязательства и риск каскада | `md_edit_context`, `md_preflight` |
| Rename / delete / section rewrite | Понять hard и soft blast radius | `md_impact`, `md_deps`, `md_section_blast_radius` |
| Проверить корпус | Найти дубли, расползание смысла, discovery gaps | `md_audit`, `md_overlaps`, `md_repeated_concepts`, `md_cluster` |
| Проверить graph health | Найти broken links, cycles, schema drift | `md_health`, `md_check`, `md_cycles`, `md_scan` |
| Закрыть работу | Проверить явно выбранные `.md` и свежесть индекса | `md_preflight`, `md_check`, `md_status` |
| Управлять состоянием | Создать / обновить index, init/strip frontmatter | `md_index`, `md_init`, `md_strip` |

## Что Дальше

Для каждого момента нужно описать:

- вызывающие скилы;
- required input;
- expected output;
- read-only / write / cost mode;
- failure mode;
- проверку совместимости.
