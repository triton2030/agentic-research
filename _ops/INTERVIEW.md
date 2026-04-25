# INTERVIEW

## Тон И Выход

- 2026-04-22 · Писать как можно короче.
- 2026-04-22 · По умолчанию писать только запрошенное, без лишних разделов и пояснений.
- 2026-04-22 · Не выдумывать факты; отделять факты от гипотез.
- 2026-04-22 · Для бизнесовых и стратегических текстов говорить человеческим деловым языком, не языком разработки.
- 2026-04-22 · В конце анализа owner-chain скилла — короткое резюме простым русским языком: что из `_ops/` помнить дальше по работе.

## Repo Shape И Routing

- 2026-04-22 · Живые `SKILL.md` считать load-bearing truth layer для skill-owned поведения.
- 2026-04-22 · `AGENTS.md` и корневые инструкции должны задавать routing и placement rules, а не дублировать skill bodies.
- 2026-04-22 · Перед нетривиальной работой сначала читать релевантный `knowledge/wisdom-*.md`; если неясно, начинать с `knowledge/wisdom-agents.md`.
- 2026-04-22 · Общие выводы класть в `knowledge/`, project artifacts - в `projects/{category}/{name}--{type}-{platform}/`.
- 2026-04-22 · Для новых control surfaces по умолчанию предпочитать `skill`, а не отдельный `agent`, если agent-shaped artifact не запрошен явно.

## Минимальный След

- 2026-04-22 · Новые файлы не создавать по умолчанию; сначала обновлять существующий правильный файл.
- 2026-04-22 · Side-docs, summaries, handoff notes и дополнительные explainers без явного запроса не создавать.
- 2026-04-22 · `_ops/` не использовать как общий склад заметок, backlog и случайных планов.
- 2026-04-22 · Имена обычных файлов и проектных папок держать в `kebab-case`.

## Рабочий Режим

- 2026-04-22 · Skills использовать как routing, не как preload.
- 2026-04-22 · Для существенной repo-level работы owner-chain по умолчанию: `before-work` -> нужный owner-skill -> execution -> `work-review`.
- 2026-04-24 · `step-back` использовать только для dialog-time framing, а не как постоянный repo owner; прежнее слово `ops` в этом смысле считать устаревшим алиасом.
- 2026-04-24 · `INTERVIEW.md` должен быть живым input/output loop: `preference-sync` захватывает предпочтения, а downstream skills применяют релевантные строки в scope, routing, Must-not или verification depth.
- 2026-04-25 · Moment-skills должны освежать контекст в момент действия: `before-work` на старт работы, `before-write` перед substantive Edit/Write, `work-review` перед финальным «готово».
- 2026-04-25 · `task-contract` должен быть узким owner-skill: создавать, обновлять и закрывать task-файлы, но не забирать preflight, write-check, review или стратегию.
- 2026-04-24 · `project-strategy` должен сверять PROJECT-PLAN с реальностью: использовать историю чата, git diff/history и фактически закрытые task-файлы как evidence для синхронизации статусов фаз и плана.
- 2026-04-24 · `brooks` нужен не как code-only reviewer, а как structural critic целой системы: документы, картинки, бизнес-планы, instructions, repo-shape и их связность; downstream-скиллы должны только роутить к нему, не переписывать его роль.
- 2026-04-22 · Task criteria работают как primer + check, не как hard gate; нарушения Must эскалируются обратно вверх по owner-chain, но ход не останавливается на входе.
- 2026-04-22 · `instruction-layer` должен управлять agent instruction layer так, чтобы он защищал горячий `_ops`-контур `project-strategy`; `_ops/PROJECT-PLAN.md`, `_ops/INTERVIEW.md` и `_ops/learnings.md` надо пересинхронизировать почти после каждого значимого изменения.
