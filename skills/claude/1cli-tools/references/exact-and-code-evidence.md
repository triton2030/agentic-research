---
description: "Exact text, path, count and JSON evidence plus code-aware symbol, syntax and analyzer candidates."
---

# Exact And Code Evidence

Открывай, когда scope уже задан и нужны exact strings/paths/counts, raw-block
или JSON inspection, code symbol/refactor evidence, syntax inventory либо
analyzer candidates. Markdown meaning и owner принадлежат `1md-navigator`;
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
