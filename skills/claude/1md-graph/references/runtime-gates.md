---
description: "Live md composite-error, side-effect and graph-frontmatter mutation gates."
---

# Runtime Gates и Schema Mutation

Механика составных команд и мутаций графового frontmatter. Смысловые решения
живут в `SKILL.md` и соседних references; здесь — как не споткнуться о
runtime. При расхождении команды, поля или cost с памятью используй targeted
`md tools <cmd> --json` / `md <cmd> --help`; live payload сильнее этого файла.

## Composite Runtime Gates

- `edit-context` preview может вернуть packet-level continuation в
  `_envelope.next_step`; это не per-item selector, и generated command может
  быть unbounded без явного budget. Сначала проверь top-level `.error`, затем
  named errors внутри `.preflight`, `.related` и, в full/query mode,
  `.search`. Success branches не обязаны иметь `_exit_code`; process status и
  named error сильнее предположения о вложенном коде.
- Такой packet-level `next_step` раскрывает весь neighborhood: следуй ему
  только для малого packet или добавь явный `--token-budget N`. Не повторяй
  `preflight` без изменения target/state.
- `section-blast-radius` проверь в обеих вложенных ветках: `.graph.error` и
  `.semantic.error`. Process может остаться 0 при failed graph layer; пустой
  top-level `next_step` тоже не доказывает успех.
- Live catalog помечает `section-blast-radius` как `readOnlyHint:false` и
  `cost_bearing:true`: команда может heal/index corpus, записать cache и
  вызвать embedding provider. Если эти side effects не покрыты задачей,
  закрой hard layer через `preflight`, а semantic lifecycle передай
  `1md-navigator` вместо запуска composite.
- При named `index_busy` дождись текущего writer-а и повтори исходную
  команду; не запускай второй index writer. Для warmup/rebuild следуй live
  payload и dry-run/confirm route.
- Graph scope берётся из `[graph]` policy и graph `--path-*` flags;
  `md status` показывает index scope и НЕ доказывает тот же радиус.
- Для broad hygiene из `GRAPH_ROOT` запускай `scan`, `check` и `cycles` на
  нужном scope; `health` — optional summary, не замена этим checks.

## Schema Mutation

Portable **graph** core: непустой string `description` для discovery и
`depends-on` только для реального source meaning (admission test —
[`semantic-edge-audit.md`](semantic-edge-audit.md)). Это minimum common
denominator графа, а не полный metadata contract и не запрет на поля других
owners. Planning, artifact identity, lifecycle, provenance и другие metadata
следуют local document contract и отдельному path/zone profile; не подменяй их
поле на `depends-on` ради прохождения graph schema.

Frontmatter открыт для arbitrary custom metadata. `scan` проверяет обязательный
`description`, тип `zone`, присутствующие graph fields и три deprecated graph
key; unknown-field gate отсутствует. По умолчанию `strip` удаляет только
`depends_on`, `read-before-edit` и `edit-after-edit`, сохраняя local metadata;
explicit `--also-related-section` дополнительно меняет body.

Prose/wikilink остаётся navigation, не edge. Отсутствующий `depends-on` означает,
что graph participation не объявлен; `depends-on: []` явно объявляет отсутствие
исходящих hard edges. Ни одно состояние не доказывает отсутствие downstream
holders — держатели объявляют edge у себя, обратный запрос обязателен.

Для cleanup сначала `md scan`, затем `md init` / `md strip` с `--dry-run`;
confirm выполняй только из фактического `_envelope.next_step` с тем же
`transaction_id` или `fingerprint`.
