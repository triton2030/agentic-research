# Search mechanics

## Purpose

Search picks sources to read. It does not establish the owner's position and
does not guarantee that every fitting remark is found. This note ties the tool's
mechanics to your next move.

The truth about behavior is [chat_digest.py](../scripts/chat_digest.py); the
checked cases are [test_chat_digest.py](../tests/test_chat_digest.py). Function
names below help verify a specific mismatch after a code update.

## Before the first search

Read this note whole. When the search code changes or output disagrees with
this description, check the function and its tests: an earlier understanding
of the tool does not confirm a new version.

| Mechanism | Strength and limit | What it means for your search |
| --- | --- | --- |
| `_dense_text`, `_search_dense_texts`: a vector per record from its text and `context-note`. Current model: `Xenova/multilingual-e5-large`, local, with `query:` and `passage:` prefixes. | Semantic closeness finds a thought phrased differently. A record vector does not represent the whole conversation. | Phrase the query at the level of meaning; understand a found remark through its whole conversation. |
| `_fts_query`, `_fts_term`, `search_bm25`: SQLite FTS5 `unicode61`; query words joined by OR without stopwords (`QUERY_STOPWORDS`); a Russian word is searched by its Snowball stem as a prefix, a trailing `*` sets a prefix explicitly. | Word forms match: «телефон» catches «телефона». The stem is crude: alternations and suppletive forms do not merge, a short stem can catch unrelated words; without fastembed's stemmer (a run not via `uv`) search is literal. | Use several meaningful wordings. `--lexical` keeps only lexical search and is less complete than hybrid. |
| `search_hybrid`: BM25 and dense search the filtered records independently; ranks merge by RRF. `lexical_matched` counts BM25 hits; zero is marked `no-lexical-match`, an empty eligible set `no-eligible-records`. | A paraphrase with no shared words can now find a conversation. Nearest vectors exist even for a question with no answer. | Check `channels` per quote: `bm25` for a literal match, `dense` for a place in the bounded vector set, or both. Dense without BM25 is a candidate to read; a verbatim result does not by itself answer the question. |
| `_merge_file_rankings`: RRF merge, depth limit, then conversations with supporting remarks. | Several channels and grouping help pick conversations. Rank does not measure truth, strength or completeness. | Read the chosen conversations; supporting remarks are not all matches. A higher `--limit` does not lift the internal depth. |
| `search_session_routes`, `search_topic_candidates`: session cards and topic descriptions have their own routes and admission rules. | A card can lead to a conversation the quotes did not. A dense card alone is not admitted: the first five BM25/dense must overlap, or lexical conditions apply; topics also need a lexical match. | `admitted_by=lexical+dense` on a topic means it entered the bounded dense top-k; otherwise `lexical`. Independent dense quote hits do not open cards and topics automatically. Check `card_route`, `admitted_by` and `topic_candidates`; try another wording, two stems with `*`, or `--topic … --timeline`. A card points to a source; it proves nothing. |
| `_filter`, `_decision_records`, `_query_conflicts`: filters apply before ranking; ordinary search excludes service, superseded and contested records and looks for conflicts separately with lexical admission only. | Output is protected from some inapplicable records. A narrow filter can drop what you need; no conflicts found does not prove the corpus is consistent. | With thin evidence, widen topic, type or period; look at conflicts and the timeline. `--since` filters by remark date, so an old backfill means re-reading the affected conversation regardless. |
| `_domain_verdict`, `_bounded*`, JSON assembly: closeness to the corpus domain and truncation are different signals. | `in-domain` means closeness to the corpus subject, not that a position exists. `truncated=false` means the script marked no truncation, not that search was complete or the tool delivered the full text. | Fix the reported `truncated_by`; watch separately for truncated tool output. Do not turn high closeness into certainty. |

## When the result is incomplete or the tool is unavailable

Choose the next move by the cause of the gap: new wording changes candidates,
a wider filter returns excluded records, a topic timeline restores order, the
whole conversation gives the scene. One query repeated with a higher limit does
not fix these causes.

Hybrid needs a prepared local runtime and cache. `--prepare` may need the
network; ordinary search uses the local model. The vector cache is tied to
content and model profile, and heavy hybrid calls are serialized by a shared
queue (`_cached_vectors`, `_content_hash`, `_hybrid_queue`). A prepare error or
queue timeout means the tool is unavailable, not that the corpus is empty. When
you fall back to `--lexical`, name the limitation if it could change the result.

Concluding that no fitting words exist requires a widened search; one empty
query, a high score or a read instruction does not justify it.
