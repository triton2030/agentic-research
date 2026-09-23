# 1md-search — Retrieval Engine

## Содержание

- Section model
- Ranking
- Language
- Output и evidence
- Exit states

## Section Model

Каждый heading становится индексируемой section; headingless file становится
одной section. Stored representation объединяет:

```text
description | title | heading chain | body
```

Длинные bodies могут разбиваться на embedding chunks, но output и stable
handles остаются section-level. Short body получает bounded sibling context для
retrieval; возвращаемый body при этом не переписывается.

## Ranking

- lexical channel: SQLite FTS5/BM25F;
- dense channel: OpenAI-compatible embeddings;
- fusion: Reciprocal Rank Fusion;
- typical field weights: `description ×5`, `title ×4`, `heading ×3`,
  `body ×1`.

`rrf_score` — ranking signal, не confidence/authority. `fields_hit` показывает,
какие каналы/fields нашли result.

Pair/topic commands используют retrieval-enriched vectors. Общий template,
title или heading chain может сблизить разные claims, а иной framing —
развести эквивалентные. Поэтому high similarity и no-hit не дают semantic
verdict без чтения bodies.

Перед schema-dependent разбором сверяй live payload или:

```bash
md tools COMMAND --json
```

Не поддерживай статический полный tool catalog внутри skill.

## Language

Lexical retrieval остаётся в основном monolingual. Morphological normalization
может связывать формы внутри языка, но не переводит heading/query:

- Russian query против English heading остаётся cross-language mismatch;
- noun/verb form-class может иметь разные lemmas;
- mixed corpus требует отдельного короткого query на каждом реально
  представленном языке.

Rerank меняет порядок найденных candidates, но не возвращает потерянный
language/aspect.

## Output И Evidence

Normal `search-read` возвращает section handles, heading chains, start lines,
snippets, descriptions, token counts и ranking signals. `--expanded` добавляет
budgeted bodies.

Читай результат слоями:

1. scope/index envelope;
2. candidate map;
3. selected bodies;
4. owner/claim verification.

Top-1 может быть decision record, derivative view или duplicate wording.
Authority подтверждает project owner, не ranking.

## Exit States

- `0` — command completed; empty payload всё ещё требует coverage reading.
- `1` — no eligible Markdown/items.
- `2` — bad arguments/path/scope.
- `3` — embedding backend unavailable.
- `4` — index needs warmup; это не no-hit.

Named envelope state/next step сильнее запомненного numeric code.
