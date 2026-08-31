---
description: "Exact-first поиск live task contract и handoff semantic discovery владельцу 1md-search."
---

# Discovery Map

Открывай перед созданием или переходом contract, чтобы не продублировать live
work, не спутать backlog с active execution и не принять archive за current.

## Наборы

- **Active:** `_ops/plans/**/task-*.md` и staged-run
  `_ops/plans/<stage>/<task>/task.md`, исключая любой `/_archive/`.
- **Deferred:** `_ops/backlog/**/task-*.md`, исключая любой `/_archive/`.
- **Archived evidence:** task-файлы под `/_archive/` в plans или backlog.
- `_ops/GOAL.md`, `README.md`, applicable `AGENTS.md` — read-only owner context.

## Exact-First

Используй доступный runtime exact lookup по принятому title/outcome, path, named
owner или устойчивому термину; отдельно проверь live plans, optional live
backlog и только при необходимости archive evidence. Нужны адресуемые
files/lines и фактический scope поиска, не semantic verdict.

Несуществующую optional surface пропусти; не создавай backlog только ради
поиска. Найденный body прочитай напрямую и классифицируй здесь.

Для известной staged-run Stage exact-first заменяется одним bounded inventory.
Предпочтительный route: `md orient _ops/plans/<stage> --frontmatter-field kind
--frontmatter-field after --json`. Если project/runtime не предоставляет `md`,
используй эквивалентный exact filesystem inventory Stage без preload bodies. По
нему выбери один Task; archive не считай active.

Этот route post-binding является Stage-local. Bound root не возвращается к
глобальному plans/backlog search, чтобы выбрать другую Stage или доказать
cross-stage uniqueness. Неясную коллизию, dependency или потребность другого
planning namespace верни user/caller-у как handoff. Глобальный duplicate search
принадлежит flat task либо caller-side allocation; incidental path metadata не
делает sibling Stage current execution owner-ом.

## Semantic Handoff

Если exact search не разрешил duplicate/related-contract question, передай
`1md-search`:

- **project root**, владеющий единственным semantic index; `_ops` — bounded
  search zone, не отдельный corpus;
- временные includes/excludes для live plans/backlog и, только если нужен
  historical evidence, archive;
- короткий вероятный task title/outcome thesis — один аспект на query;
- query pack, если отдельно ищутся active work, deferred intent и прежний
  superseded outcome.

Navigator владеет status, effective filters, warmup/recovery, normal map и
bounded body reads. Не копируй сюда index states или transaction procedure и не
создавай `.md-navigator` внутри `_ops`. Semantic rank означает related
candidate, не planning state и не permission resurrect archived work.

## Классификация Результата

Для каждого прочитанного candidate классифицируй path:

- live plans → update/reconcile active contract;
- live backlog → update/review/promote deferred contract;
- archive → evidence only до нового решения об active/deferred state;
- другой owner surface → не превращай его в task contract.

## Stop

Если похожий live contract найден, обновляй или перемещай его, не создавай
второй. Если `1md-search` вернул coverage gap, назови его; отсутствие hit не
доказывает отсутствие contract вне фактического scope.
