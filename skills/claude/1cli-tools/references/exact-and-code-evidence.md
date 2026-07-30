---
description: "Exact text, path, count and JSON evidence plus code-aware symbol, syntax and analyzer candidates."
---

# Exact And Code Evidence

Открывай, когда scope уже задан и нужны exact strings/paths/counts, stable IDs,
table rows, raw blocks или JSON inspection, code symbol/refactor evidence,
syntax inventory либо analyzer candidates. Heading-bounded Markdown prose
принадлежит `1md-read`, unknown semantic owner/discovery — `1md-search`;
frontmatter graph, anchors, wikilinks и impact — `1md-graph`.

## Exact Text, Paths И Counts

Сначала разведи единицы измерения: files, matching lines и occurrences.

```bash
fd -e md -e ts -e tsx -e py . SCOPE
rg -l 'OldName|old/path' SCOPE
rg -n 'OldName|old/path' SCOPE
rg -o --no-filename 'OldName|old/path' SCOPE | wc -l
```

Scope и exclusions бери из task/owner packet. Broad raw/archive/vendor count
подписывай как broad evidence, не как project truth. В raw/interview формах
извлекай answer blocks, не считай вопросы user claims.

## Exact Markdown IDs И Blocks

Stable ID, registry row или bold-labelled rule может быть мельче ближайшего
heading. Тогда exact route выгоднее: он не заставляет извлекать многотысячную
секцию ради одной addressable записи.

Сначала найди locator:

```bash
rg -n 'STABLE-ID' FILE.md
```

Если запись многострочная и не имеет собственного heading, извлекай её до
следующего delimiter **того же семейства**, а не до угаданного следующего
номера:

```bash
awk -v start='SYS-R-075' -v family='SYS-R-' '
index($0, "**" start " ") == 1 { on=1; print; next }
on && index($0, "**" family) == 1 { exit }
on
' FILE.md
```

`rg -A/-B` допустим как locator/context preview, но не как доказательство
heading boundary или полного raw block. Если target имеет heading, верни body в
`1md-read` через `toc → extract`.

## Raw Blocks, JSON И Links

```bash
awk '/^### Ответ пользователя/{flag=1; next} /^##/{flag=0} flag' RAW.md
jq 'keys' OUTPUT.json
jq '{envelope:._envelope, count:(.results // [] | length)}' OUTPUT.json
```

Незнакомый JSON не режь через `head`: сначала live schema или keys. `jq`/`gron`
меняют представление, не смысл; counted field сильнее догадки по длине output.

External/docs URLs можно инвентаризировать через `lychee '**/*.md' --dump`;
network validation запускай только когда она нужна задаче. Obsidian wikilinks и
anchors этому route не принадлежат.

## Symbols И Syntax

Для symbol truth используй active project LSP, только если он exposed в
текущем client. Иначе минимальная связка:

1. `rg` — exact spellings и paths;
2. project-local `sg` / `ast-grep` — syntax-shaped candidates;
3. compiler/typechecker;
4. targeted tests.

Примеры формы; flags сверь по live help:

```bash
sg run -p 'useEffect($$$)' src --json=stream
sg scan --inline-rules '<yaml>' src --json=stream
pnpm exec tsc --noEmit --pretty false
```

Unsupported language → project-local parser/LSP. Optional semantic code search
через NPX допустим только после registry/version choice и разрешённого
network/cache side effect; similarity не заменяет exact/runtime proof.

## Analyzers

`knip`, `depcruise`, package-shape tools и linters дают candidates. Выбери один
analyzer по project config и вопросу, а не запускай каталог инструментов.

- dead file/export: analyzer finding + exact refs + build/test;
- import impact: reachability/fan-in candidate + direct imports + targeted test;
- package publish/types: project-owned checker + pack artifact;
- codemod: match inventory и review до rewrite.

Analyzer green доказывает только configured coverage. Проверь config,
supported language и ignored/generated paths.

## Стоп

Стоп, когда exact scope и единица счёта названы, output адресуем, analyzer
правильно классифицирован, а high-risk action подтверждён runtime/test или
вторым независимым сигналом.
