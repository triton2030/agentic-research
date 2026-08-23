---
type: index
title: Оркестрация волн субагентов
description: Где оркестрация живёт в Workspace, как 1orchestration распределяет задачи между субагентами, как устроена папка волны и что такое durable manifest восстановления
topic: orchestration-waves
---
# Оркестрация волн субагентов

Где оркестрация живёт в Workspace, как 1orchestration распределяет задачи между субагентами, как устроена папка волны и что такое durable manifest восстановления

- [Где оркестрация живёт в Workspace?](../method/workspace-layout-for-orchestration-sessions.md) — Специальная папка 1orchestration в Workspace, внутри — отдельная папка на каждую сессию оркестрации.
- [За что оркестратор отвечает перед траекторией и пользой проекта?](../concept/orchestrator-trajectory-keeper.md) — Позиция технического директора, экономия контекста, волевые решения при проблемах и автономность против неполезных или невыполнимых просьб.
- [Как 1orchestration распределяет задачи и инструкции между субагентами?](../method/distributing-tasks-to-subagents.md) — Что кладёт оркестратор в задание субагенту — свод инструкций всех слоёв, посильная задача, учёт нагрузки моделей, фокус внимания вместо запретов.
- [Как 1orchestration связана с 1instruction-shaping?](../method/orchestration-instruction-shaping-link.md) — Оркестратор пользуется знаниями 1instruction-shaping при написании инструкций субагентам, точечно ссылаясь на его reference-файлы вместо вызова всего скилла.
- [Как устроена папка волны в 1orchestration v4.2?](../entity/orchestration-wave-folder.md) — Схема папки волны вынесена в references/wave-folder.md, а шаблон context.md получил блок Закрытие; деление скилла отложено до первой боевой волны.
- [Какие root-источники читает оркестратор?](../entity/root-sources-direct-read.md) — Прямое чтение root-источников самим оркестратором — критичная правка общего 1orchestration наряду с durable manifest восстановления.
- [Куда записываются самостоятельные решения оркестратора?](../method/orchestrator-decisions-registry.md) — В папке оркестрации ведётся отдельный реестр самостоятельных решений с их обоснованиями, чтобы они не терялись.
- [Можно ли переписывать общий 1orchestration?](../concept/rewriting-general-orchestration.md) — Общий скилл не переписывать и не раздувать словами — владельцу важна компактность.
- [Что оркестратор показывает как доказательство работы?](../method/orchestration-report-as-proof.md) — Отчёт 1orchestration выводится прямо в чат как доказательство работы агента.
- [Что такое durable manifest восстановления?](../method/durable-manifest-recovery.md) — Критичная правка общего 1orchestration — durable manifest восстановления вместе с прямым чтением root-источников.
