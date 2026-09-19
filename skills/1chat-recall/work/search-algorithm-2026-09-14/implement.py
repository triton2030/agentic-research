from pathlib import Path
for runtime in ['codex','claude']:
    p=Path(f'skills/{runtime}/1chat-recall/scripts/chat_digest.py')
    s=p.read_text()
    s=s.replace('    for back_reference in ("superseded_by", "contested_by"):', '    if record.get("channels"):\n        card["channels"] = record["channels"]\n    for back_reference in ("superseded_by", "contested_by"):',1)
    s=s.replace('        evidence[filename].append(record)', '''        evidence[filename].append({
                **record,
                "channels": [
                    name for name, ranking in zip(("bm25", "dense"), rank_by_address)
                    if record["address"] in ranking
                ],
            })''',1)
    s=s.replace('    collapse_files: bool = False,\n) -> list[dict[str, Any]]:\n    lexical = search_bm25(records, query)\n    if not lexical:\n        return []\n    dense = search_dense(records, query)', '''    collapse_files: bool = False,
    allow_semantic_only: bool = True,
) -> list[dict[str, Any]]:
    lexical = search_bm25(records, query)
    if not records or (not lexical and not allow_semantic_only):
        return []
    dense = search_dense(records, query)''',1)
    s=s.replace('        return [\n            {**representatives[address], "score": scores[address]}\n            for address in ordered\n        ]', '''        channel_addresses = [
            {record["address"] for record in ranking[:HYBRID_DEPTH]}
            for ranking in rankings
        ]
        return [
            {**representatives[address], "score": scores[address], "channels": [
                name for name, addresses in zip(("bm25", "dense"), channel_addresses)
                if address in addresses
            ]}
            for address in ordered
        ]''',1)
    s=s.replace('ranking = search_hybrid(disputed, args.query, collapse_files=False)', '''# Conflicts trigger a different reader action from candidate sources.
            # Keep their previous admission until semantic conflict relevance is validated.
            ranking = search_hybrid(
                disputed, args.query, collapse_files=False, allow_semantic_only=False
            )''',1)
    s=s.replace('    if hybrid:\n        dense = _search_dense_texts(cards, query, lambda card: card["search_text"])', '    dense_topics: set[str] = set()\n    if hybrid:\n        dense = _search_dense_texts(cards, query, lambda card: card["search_text"])\n        dense_topics = {card["topic"] for card in dense[:limit]}',1)
    s=s.replace('            if hybrid\n            else "lexical"\n        )', '            if topic in dense_topics\n            else "lexical"\n        )',1)
    # Preserve structured provenance in full/timeline records as well.
    s=s.replace('        "score",\n    )\n    summary', '        "score",\n        "channels",\n    )\n    summary',1)
    # Status is explicitly passed, not stored in shared mutable search state.
    a=s.index('def _render_holders(');b=s.index('\ndef _query_selection(',a)
    section=s[a:b]
    section=section.replace('    retrieval: str,\n)', '    retrieval: str,\n    lexical_matched: int | None = None,\n)')
    section=section.replace('    lines = [status]\n', '''    if lexical_matched is not None:
        status += f" · lexical_matched={lexical_matched}"
        if lexical_matched == 0:
            status += " · warning=no-lexical-match"
    lines = [status]
''',1)
    section=section.replace('            text = " ".join(strongest["text"].split())', '            text = " ".join(strongest["text"].split())\n            via = "+".join(strongest.get("channels", [])) or "unknown"',1)
    section=section.replace('f"strongest-quote: {text} · date=', 'f"strongest-quote: {text} · via={via} · date=',1)
    section=section.replace('            retrieval=retrieval,\n', '            retrieval=retrieval,\n            lexical_matched=lexical_matched,\n')
    s=s[:a]+section+s[b:]
    a=s.index('def main(');section=s[a:]
    section=section.replace('    args = build_parser().parse_args()', '    global _DENSE_TOP1\n    _DENSE_TOP1 = None\n    args = build_parser().parse_args()',1)
    section=section.replace('        total = len(records)\n', '''        total = len(records)
        # Count exactly the same eligible set as ordinary holder retrieval.
        lexical_matched = (
            len(search_bm25(_decision_records(_filter(records, args)), args.query))
            if holder_mode else None
        )
''',1)
    section=section.replace('                    retrieval=retrieval or "lexical",\n', '                    retrieval=retrieval or "lexical",\n                    lexical_matched=lexical_matched,\n')
    section=section.replace('        if holder_mode:\n            envelope["conflict_matched"]', '''        if holder_mode:
            envelope["lexical_matched"] = lexical_matched
            if lexical_matched == 0:
                envelope["warnings"].append("no-lexical-match")
            envelope["conflict_matched"]''',1)
    s=s[:a]+section
    p.write_text(s)
